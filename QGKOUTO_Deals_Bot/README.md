# QGKOUTO Deals

Bot simples de avisos de jogos grátis e promoções para Discord, executado gratuitamente pelo GitHub Actions.

## O que monitora
- Epic Games Store: jogos com oferta gratuita ativa.
- Steam: jogos com desconto na seção de especiais, com preços da região brasileira.
- GOG: tentativa de consulta ao catálogo com descontos. A API pública pode mudar; veja os logs do workflow se a GOG não responder.

## Configuração rápida
1. Crie um webhook no canal do Discord: **Editar canal → Integrações → Webhooks → Novo webhook**.
2. Copie a URL do webhook. Não a compartilhe.
3. Crie um repositório público no GitHub chamado `qgkouto-deals`.
4. Envie os arquivos deste pacote para a raiz do repositório, mantendo a pasta `.github/workflows`.
5. No GitHub, abra **Settings → Secrets and variables → Actions → New repository secret**.
6. Nome do segredo: `DISCORD_WEBHOOK_URL`. Valor: a URL copiada do Discord.
7. Abra **Actions**, selecione **Verificar ofertas de jogos** e clique em **Run workflow** para testar.
8. O agendamento tenta rodar a cada 4 horas. O GitHub pode atrasar tarefas agendadas.

## Segurança
- Nunca coloque a URL do webhook diretamente no código.
- Não compartilhe o segredo do GitHub.
- Repositórios públicos deixam o código visível, mas os GitHub Secrets não ficam expostos no código.
- Se o webhook vazar, apague-o e crie outro no Discord.

## Observações
- Os dados e a disponibilidade podem variar por país e mudar a qualquer momento.
- Os preços da Steam são consultados para o Brasil. Algumas fontes de terceiros podem não cobrir todas as lojas ou todos os jogos.
- O workflow guarda IDs de ofertas em `state.json` para reduzir mensagens repetidas.
- O GitHub Actions em repositórios públicos é gratuito para runners padrão, sujeito às regras atuais da plataforma.
