# UEPB Orienta (versão site estático)

Site de orientação de cursos da UEPB com o VANDER IA. HTML, CSS e JavaScript puros, sem build e sem servidor.
Funciona: interesses, cidades, frase livre, refinar com 3 perguntas, arrastar para votar, detalhes do curso, catálogo, comparar, mapa, imagem para compartilhar. O chat com IA é opcional (veja `worker/LEIA-ME.md`).

## Publicar de graça
**GitHub Pages:** envie esta pasta para um repositório, depois Settings > Pages > Deploy from branch > `main` / root. O endereço sai em `https://USUARIO.github.io/REPO/`.
**Cloudflare Pages:** Workers & Pages > Create > Pages > Upload assets, arraste a pasta.
**Netlify:** app.netlify.com/drop, arraste a pasta.

## Personalizar
- `config.js`: link do processo seletivo, endereço do chat, nome do site na imagem.
- `extras.js`: nota de corte, mercado, depoimento e link por curso. Só preencha com dados reais e cite a fonte.
- `js/data.js`: cursos, interesses e perguntas. A lógica de cálculo está em `js/core.js` (mesmo ranking do app Streamlit).

Para testar local: `python -m http.server 8000` e abra http://localhost:8000. O mapa e as fontes funcionam sem internet, exceto os blocos do mapa (Esri).
