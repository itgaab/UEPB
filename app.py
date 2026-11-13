from pathlib import Path

import streamlit as st

import agente
from cursos_uepb import AREAS, CAMPUS, CIDADES, CURSOS, GRAUS
from orientador import DIM_NOMES, QUESTOES, ranking, resumo_respostas

ASSETS = Path(__file__).parent / "assets"
AVATAR = str(ASSETS / "avatar.png")

st.set_page_config(
    page_title="Orientador de Cursos UEPB • VANDER IA",
    page_icon=AVATAR,
    layout="centered",
)

SAUDACAO = (
    "Oi! Eu sou o **VANDER IA** 🤖. Posso explicar o seu resultado, comparar cursos da UEPB "
    "e tirar dúvidas sobre carreiras. O que você quer saber?"
)

# ----------------------------------------------------------------------------
# Estado
# ----------------------------------------------------------------------------
st.session_state.setdefault("resultado", None)
st.session_state.setdefault("respostas", {})
st.session_state.setdefault("chat", [{"role": "assistant", "content": SAUDACAO, "saudacao": True}])


def contexto_para_ia() -> str:
    linhas = []
    if st.session_state.resultado:
        linhas.append("RESPOSTAS DA PESSOA NO TESTE:")
        linhas.append(resumo_respostas(st.session_state.respostas))
        linhas.append("\nCURSOS MAIS COMPATÍVEIS (compatibilidade calculada pelo app):")
        for c in st.session_state.resultado["lista"][:10]:
            linhas.append(f"- {c['nome']} ({c['grau']}): {c['afinidade']}%")
    else:
        linhas.append("A pessoa ainda não fez o teste.")
    linhas.append("\nCATÁLOGO COMPLETO DE CURSOS DA UEPB (nome, grau, campi):")
    for c in CURSOS:
        campi = "; ".join(f"{cid} ({CAMPUS[cid]})" for cid in c["campi"])
        linhas.append(f"- {c['nome']} [{c['grau']}] — {campi}. O que faz: {c['faz']}")
    return "\n".join(linhas)


def mostrar_curso(c: dict, destaque: dict | None = None, chave: str = ""):
    """Mostra os detalhes de um curso."""
    st.markdown(f"**O que faz:** {c['faz']}")
    st.markdown(f"**O que você estuda:** {c['estuda']}")
    st.markdown("**Onde você pode atuar:**")
    for item in c["carreiras"]:
        st.markdown(f"- {item}")
    st.markdown("**Onde é oferecido (turno):**")
    for cidade, turno in c["campi"].items():
        marca = " ✅" if destaque and cidade in destaque else ""
        st.markdown(f"- {cidade} ({CAMPUS[cidade]}): {turno}{marca}")


# ----------------------------------------------------------------------------
# Barra lateral
# ----------------------------------------------------------------------------
with st.sidebar:
    st.image(str(ASSETS / "logo.png"), width="stretch")
    p = agente.provedor()
    if p == "anthropic":
        st.success("VANDER IA conectado")
    elif p == "vander":
        st.success("VANDER IA conectado")
    elif p == "gemini":
        st.info("VANDER IA ativo (via Gemini)")
    else:
        st.warning("Chat com IA desativado")
        st.text_input(
            "Chave da API Gemini (opcional)",
            type="password",
            key="user_api_key",
            help="Gratuita em aistudio.google.com. O teste e o catálogo funcionam sem chave.",
        )
    if st.button("Refazer o teste", width="stretch"):
        st.session_state.resultado = None
        st.session_state.respostas = {}
        st.session_state.chat = [{"role": "assistant", "content": SAUDACAO, "saudacao": True}]
        st.rerun()
    st.caption("Fonte dos cursos: Pró-reitoria de Graduação da UEPB. Confirme turnos e vagas em uepb.edu.br.")

# ----------------------------------------------------------------------------
# Cabeçalho
# ----------------------------------------------------------------------------
col1, col2 = st.columns([1, 4], vertical_alignment="center")
with col1:
    st.image(str(ASSETS / "mascote.png"), width="stretch")
with col2:
    st.title("Qual curso da UEPB combina com você?")
    st.caption("Responda 9 perguntas rápidas e converse com o VANDER IA.")

aba_teste, aba_cursos, aba_chat = st.tabs(["🎯 Teste", "📚 Cursos da UEPB", "💬 VANDER IA"])

# ----------------------------------------------------------------------------
# Aba 1: teste
# ----------------------------------------------------------------------------
with aba_teste:
    if not st.session_state.resultado:
        with st.form("teste"):
            respostas = {}
            for q in QUESTOES:
                if q["tipo"] == "one":
                    respostas[q["id"]] = st.radio(q["titulo"], list(q["opcoes"]), index=None, key=q["id"])
                elif q["tipo"] == "multi":
                    respostas[q["id"]] = st.multiselect(
                        q["titulo"], list(q["opcoes"]), max_selections=q["max"], key=q["id"]
                    )
                else:
                    respostas[q["id"]] = st.multiselect(
                        q["titulo"],
                        CIDADES,
                        format_func=lambda cid: f"{cid} ({CAMPUS[cid]})",
                        key=q["id"],
                        help="Deixe em branco se puder estudar em qualquer cidade.",
                    )
            st.markdown("**Opcional:** filtrar o resultado")
            graus = st.multiselect("Tipo de curso", GRAUS, help="Em branco = todos.")
            so_cidades = st.checkbox("Mostrar apenas cursos oferecidos nas cidades escolhidas")
            enviar = st.form_submit_button("Ver meu resultado", type="primary", width="stretch")

        if enviar:
            faltando = [
                q["titulo"].split(".")[0]
                for q in QUESTOES
                if q["tipo"] != "cidades" and not respostas.get(q["id"])
            ]
            if faltando:
                st.error("Faltou responder as perguntas: " + ", ".join(faltando) + ".")
            else:
                lista, vetor = ranking(respostas, respostas["q9"], graus, so_cidades)
                if not lista:
                    st.warning("Nenhum curso encontrado com esses filtros. Tente ampliar as cidades ou os tipos.")
                else:
                    st.session_state.respostas = respostas
                    st.session_state.resultado = {"lista": lista, "vetor": vetor}
                    st.rerun()
    else:
        res = st.session_state.resultado
        vetor = res["vetor"]
        st.subheader("Seu perfil")
        total = sum(vetor.values()) or 1
        for dim, pts in sorted(vetor.items(), key=lambda kv: kv[1], reverse=True)[:4]:
            st.progress(min(1.0, pts / total * 2.2), text=DIM_NOMES[dim])

        st.subheader("Cursos com mais compatibilidade")
        cidades = st.session_state.respostas.get("q9") or []
        for i, c in enumerate(res["lista"][:8], start=1):
            with st.expander(f"{i}. {c['nome']} ({c['grau']}) • {c['afinidade']}%", expanded=(i == 1)):
                st.progress(c["afinidade"] / 100)
                mostrar_curso(c, c["nas_cidades"] or None)
        st.info("Quer entender melhor o resultado? Abra a aba **VANDER IA** e converse sobre ele.")
        st.caption(
            "A compatibilidade é uma estimativa baseada nas suas respostas e no perfil geral de cada curso. "
            "É uma orientação, não uma sentença: converse com estudantes e profissionais da área."
        )

# ----------------------------------------------------------------------------
# Aba 2: catálogo
# ----------------------------------------------------------------------------
with aba_cursos:
    n_ofertas = sum(len(c["campi"]) for c in CURSOS)
    st.markdown(f"**{len(CURSOS)} cursos** em **{n_ofertas} ofertas** nos 8 campi da UEPB.")
    busca = st.text_input("Buscar curso", placeholder="Ex.: computação, saúde, professor...")
    f1, f2, f3 = st.columns(3)
    area_f = f1.selectbox("Área", ["Todas"] + AREAS)
    grau_f = f2.selectbox("Tipo", ["Todos"] + GRAUS)
    cid_f = f3.selectbox("Cidade", ["Todas"] + CIDADES)

    def passa(c):
        if area_f != "Todas" and c["area"] != area_f:
            return False
        if grau_f != "Todos" and c["grau"] != grau_f:
            return False
        if cid_f != "Todas" and cid_f not in c["campi"]:
            return False
        if busca:
            alvo = " ".join([c["nome"], c["faz"], c["estuda"], " ".join(c["carreiras"])]).lower()
            return busca.lower() in alvo
        return True

    filtrados = sorted((c for c in CURSOS if passa(c)), key=lambda c: (c["nome"], c["grau"]))
    st.caption(f"{len(filtrados)} curso(s) encontrado(s)")
    for c in filtrados:
        with st.expander(f"{c['nome']} • {c['grau']} • {c['area']}"):
            mostrar_curso(c, {cid_f: 1} if cid_f != "Todas" else None)

# ----------------------------------------------------------------------------
# Aba 3: chat com o VANDER IA
# ----------------------------------------------------------------------------
with aba_chat:
    st.caption("Converse com o VANDER IA sobre cursos, carreiras e o seu resultado.")
    if agente.provedor() is None:
        st.warning(
            "O chat precisa de uma conexão com IA. Configure o VANDER IA (ou uma chave Gemini) "
            "nos Secrets ou na barra lateral. O teste e o catálogo funcionam normalmente sem isso."
        )

    for m in st.session_state.chat:
        with st.chat_message(m["role"], avatar=AVATAR if m["role"] == "assistant" else None):
            st.markdown(m["content"])

    sugestoes = []
    if st.session_state.resultado:
        sugestoes.append("Explique meu resultado")
    sugestoes += ["Quais cursos de tecnologia a UEPB tem?", "Como é a rotina de quem faz Enfermagem?"]
    escolha = st.pills("Sugestões", sugestoes, label_visibility="collapsed")
    prompt = st.chat_input("Pergunte ao VANDER IA...") or escolha

    LIMITE_MSGS = 20  # protege o seu crédito: máximo de perguntas por sessão
    if prompt and sum(m["role"] == "user" for m in st.session_state.chat) >= LIMITE_MSGS:
        st.info("Você atingiu o limite de perguntas desta sessão. Clique em **Refazer o teste** para recomeçar.")
        prompt = None

    if prompt and agente.provedor():
        st.session_state.chat.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        historico = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.chat
            if not m.get("saudacao")
        ]
        with st.chat_message("assistant", avatar=AVATAR):
            with st.spinner("VANDER IA está pensando..."):
                try:
                    resposta = agente.conversar(historico, contexto_para_ia())
                except Exception as e:
                    resposta = f"Não consegui falar com a IA agora ({type(e).__name__}). Tente de novo em instantes."
            st.markdown(resposta)
        st.session_state.chat.append({"role": "assistant", "content": resposta})
