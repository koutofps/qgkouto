import json
import os
import urllib.request
import urllib.parse
from pathlib import Path

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
STATE_FILE = Path("state.json")
STATE = json.loads(STATE_FILE.read_text(encoding="utf-8")) if STATE_FILE.exists() else {"sent": []}
sent = set(STATE.get("sent", []))
new_sent = []

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "QGKOUTO-Deals/1.0"})
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))

def send_embed(title, description, url, color=3447003, image=None):
    payload = {
        "username": "QGKOUTO Deals",
        "embeds": [{
            "title": title[:256],
            "description": description[:4000],
            "url": url,
            "color": color,
            **({"thumbnail": {"url": image}} if image else {}),
            "footer": {"text": "QGKOUTO Deals • confira o preço e a disponibilidade na loja"}
        }]
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        WEBHOOK_URL, data=data,
        headers={"Content-Type": "application/json", "User-Agent": "QGKOUTO-Deals/1.0"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=25) as response:
        response.read()

def remember(key):
    sent.add(key)
    new_sent.append(key)

def check_epic_free_games():
    # Fonte pública usada por projetos que acompanham os jogos grátis da Epic.
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=pt-BR&country=BR&allowCountries=BR"
    try:
        data = get_json(url)
        elements = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
        for game in elements:
            promotions = game.get("promotions") or {}
            offers = promotions.get("promotionalOffers") or []
            active = [offer for group in offers for offer in group.get("promotionalOffers", [])]
            if not active:
                continue
            title = game.get("title", "Jogo grátis na Epic Games")
            key = "epic:" + str(game.get("id") or game.get("productSlug") or title)
            if key in sent:
                continue
            slug = game.get("productSlug") or game.get("urlSlug") or ""
            link = "https://store.epicgames.com/pt-BR/p/" + str(slug) if slug else "https://store.epicgames.com/pt-BR/free-games"
            desc = "🎁 **Grátis para resgatar!**\nConfira a página da Epic para ver o prazo e resgatar o jogo."
            image = None
            for item in game.get("keyImages", []):
                if item.get("type") in ("OfferImageWide", "DieselStoreFrontWide"):
                    image = item.get("url")
                    break
            send_embed("🎁 JOGO GRÁTIS — EPIC GAMES", f"**{title}**\n\n{desc}", link, 5763719, image)
            remember(key)
    except Exception as exc:
        print("Epic Games: erro ao consultar:", repr(exc))

def check_steam_deals():
    # A API de categorias em destaque da Steam apresenta especiais para a região brasileira.
    url = "https://store.steampowered.com/api/featuredcategories/?cc=br&l=brazilian"
    try:
        data = get_json(url)
        items = data.get("specials", {}).get("items", [])
        for game in items:
            appid = game.get("id")
            title = game.get("name", "Jogo em promoção na Steam")
            if not appid:
                continue
            discount = int(game.get("discount_percent") or 0)
            if discount <= 0:
                continue
            key = f"steam:{appid}:{discount}"
            if key in sent:
                continue
            price = game.get("final_price")
            original = game.get("original_price")
            def brl(cents):
                return "Preço indisponível" if cents is None else ("R$ " + f"{cents/100:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            desc = f"💸 **Desconto: {discount}%**\n"
            if original is not None and price is not None:
                desc += f"~~{brl(original)}~~ → **{brl(price)}**\n"
            desc += "Preço consultado para a região brasileira; confirme na loja."
            link = f"https://store.steampowered.com/app/{appid}/?cc=br"
            image = game.get("header_image")
            send_embed("💸 PROMOÇÃO — STEAM", f"**{title}**\n\n{desc}", link, 3447003, image)
            remember(key)
    except Exception as exc:
        print("Steam: erro ao consultar:", repr(exc))

def check_gog_deals():
    # Endpoint de catálogo da GOG; pode mudar sem aviso, então falhas não interrompem os outros alertas.
    params = urllib.parse.urlencode({
        "limit": "30", "order": "desc:trending", "productType": "in:game",
        "discounted": "true", "country": "BR", "locale": "pt-BR", "currency": "BRL"
    })
    url = "https://catalog.gog.com/v1/catalog?" + params
    try:
        data = get_json(url)
        products = data.get("products", [])
        for game in products:
            product_id = game.get("id") or game.get("slug")
            title = game.get("title", "Jogo em promoção na GOG")
            if not product_id:
                continue
            key = f"gog:{product_id}"
            if key in sent:
                continue
            slug = game.get("slug")
            link = f"https://www.gog.com/en/game/{slug}" if slug else "https://www.gog.com/en/games?discounted=true"
            price = game.get("price") or {}
            final = price.get("final")
            regular = price.get("base")
            discount = price.get("discount")
            desc = "Confira o preço atual na GOG."
            if discount:
                desc = f"💸 **Desconto: {discount}%**\n" + desc
            if final:
                desc += f"\nPreço promocional informado pela loja: {final}"
                if regular:
                    desc += f" (preço normal: {regular})"
            image = game.get("coverHorizontal") or game.get("image")
            send_embed("💸 PROMOÇÃO — GOG", f"**{title}**\n\n{desc}", link, 16753920, image)
            remember(key)
    except Exception as exc:
        print("GOG: consulta indisponível ou formato alterado:", repr(exc))

if __name__ == "__main__":
    check_epic_free_games()
    check_steam_deals()
    check_gog_deals()
    # Guarda os 2.000 avisos mais recentes para não repetir mensagens em toda execução.
    STATE_FILE.write_text(json.dumps({"sent": list(sent)[-2000:]}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Concluído. Novos avisos nesta execução: {len(new_sent)}")
