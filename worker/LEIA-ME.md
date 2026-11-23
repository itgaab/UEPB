# Ativar o chat com IA (opcional, grátis)

O site funciona sem isso. O chat precisa de uma função que guarda a chave da IA, para ela não ficar exposta no navegador.

1. Crie uma conta grátis em https://dash.cloudflare.com e abra **Workers & Pages > Create > Worker**.
2. Dê o nome `uepb-orienta-chat`, clique em **Deploy**, depois **Edit code**, cole o conteúdo de `chat-worker.js` e **Deploy**.
3. Em **Settings > Variables and Secrets**, adicione:
   - `ALLOWED_ORIGIN` (texto): o endereço do seu site, sem barra no fim. Ex.: `https://itgaab.github.io`
   - `GEMINI_API_KEY` (secret): chave grátis do Google AI Studio. Ou `ANTHROPIC_API_KEY` (secret), se preferir Claude.
4. Copie o endereço do worker (`https://uepb-orienta-chat.SEU-USUARIO.workers.dev`) e cole em `CHAT_ENDPOINT` no arquivo `config.js` do site.
5. Publique o site de novo.

O worker aceita pedidos só do seu site, limita o tamanho das mensagens e usa a chave só no servidor.
