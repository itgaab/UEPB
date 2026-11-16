# 🤖 Orientador de Cursos UEPB • VANDER IA

App em Streamlit que ajuda a descobrir qual curso de graduação da **UEPB** combina com você:

- **Tela única por toque**: a pessoa marca de 3 a 5 interesses (botões com emoji), escolhe a cidade se quiser e vê os 5 cursos mais compatíveis na hora, com uma linha de "por que combina". O ranking é calculado localmente, sem gastar API.
- **Refinar (opcional)**: o botão "Quero um resultado mais preciso" abre 3 perguntas rápidas que ajustam o ranking.
- **Frase livre (opcional)**: a pessoa conta em uma frase o que quer e o VANDER IA converte em interesses (chamada curta e barata; sem IA, usa palavras-chave).
- **Catálogo completo**: 38 cursos em 64 ofertas nos 8 campi, com o que cada curso faz, o que se estuda, onde atuar e turnos.
- **Chat com o VANDER IA** para explicar o resultado e tirar dúvidas.

O resultado e o catálogo funcionam **sem nenhuma chave**. A IA só entra no chat e na leitura da frase livre.

## Estrutura

```
app.py              interface (páginas Descobrir, Cursos, VANDER IA)
orientador.py       interesses, perguntas de refinamento e cálculo de compatibilidade
cursos_uepb.py      catálogo de cursos (edite aqui para corrigir ou adicionar cursos)
agente.py           conexão com o VANDER IA (chat e leitura da frase livre; plano B com Gemini)
assets/             logo, mascote e avatar
.streamlit/config.toml   cores do tema
```

## Conectar o VANDER IA (Claude)

O VANDER IA roda sobre o Claude, com a persona e as regras definidas em `agente.py`.

1. Acesse https://console.anthropic.com, faça login e vá em **API keys > Create key**. Copie a chave (`sk-ant-...`): ela só aparece uma vez.
2. Em **Billing**, adicione créditos (a API é paga por uso, separada de qualquer assinatura do Claude).
3. Defina um **limite mensal de gasto** no Console, por segurança.
4. Cole a chave em **Secrets** (Streamlit Cloud: *Advanced settings > Secrets*; local: `.streamlit/secrets.toml`):

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

Nunca coloque a chave no código nem no GitHub. O modelo padrão é o `claude-haiku-5-5` (o mais barato);
para trocar, defina `ANTHROPIC_MODEL` nos Secrets.

O app limita cada sessão a 20 perguntas para proteger o seu crédito (ajuste `LIMITE_MSGS` em `app.py`).

**Alternativas** (veja `secrets.toml.example`): endpoint próprio via `VANDER_API_URL` ou Gemini gratuito via `GEMINI_API_KEY`.
A prioridade é: Claude, depois endpoint próprio, depois Gemini.

## Rodar localmente

```bash
pip install -r requirements.txt
mkdir -p .streamlit && cp secrets.toml.example .streamlit/secrets.toml   # edite
streamlit run app.py
```

## Publicar no Streamlit Community Cloud

1. Suba **todos os arquivos e pastas** deste projeto para a raiz de um repositório no GitHub (inclua `assets/` e `.streamlit/config.toml`; **não** suba `secrets.toml`).
2. Em https://share.streamlit.io clique em **Create app**, escolha o repositório, a branch e o arquivo `app.py`.
3. Em **Advanced settings > Secrets**, cole as chaves acima e clique em **Deploy**.

## Sobre os dados

- A lista de cursos, campi e turnos vem da página da Pró-reitoria de Graduação da UEPB
  (https://uepb.edu.br/prograd/ensino/cursos-de-graduacao-2/). Turnos e ofertas mudam: confirme no site da UEPB.
- As descrições dos cursos são resumos gerais, não o projeto pedagógico oficial.
- A compatibilidade é uma estimativa por perfil (interesses, preferências e valores), uma orientação inicial e não uma sentença.


Para mudar os botões de interesse (emoji, nome, pesos e cursos afins), edite `INTERESSES` em `orientador.py`.
