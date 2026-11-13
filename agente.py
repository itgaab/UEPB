"""Conexão com o agente de IA (VANDER IA) com plano B no Gemini.

Ordem de uso:
1. Claude (Anthropic): se ANTHROPIC_API_KEY estiver nos Secrets. A IA assume a persona VANDER IA.
2. VANDER IA próprio: se VANDER_API_URL estiver nos Secrets (formato "chat/completions" da OpenAI).
3. Gemini: se GEMINI_API_KEY estiver configurada (a IA assume o nome Vander IA).
4. Sem IA: o ranking continua funcionando; só o chat fica desativado.
"""
import os

import requests
import streamlit as st

NOME = "VANDER IA"

PERSONA = f"""Você é o {NOME}, orientador vocacional da UEPB (Universidade Estadual da Paraíba),
simpático, claro e direto, falando português do Brasil.

Regras:
- Use SOMENTE os cursos da lista fornecida no contexto ao falar de cursos da UEPB. Nunca invente curso,
  campus, turno, nota de corte ou número de vagas. Se não souber, diga que a pessoa deve conferir no site
  da UEPB (uepb.edu.br).
- Explique a relação entre as respostas da pessoa e os cursos sugeridos.
- Seja honesto: o resultado é uma orientação, não uma sentença. Incentive conversar com estudantes e
  profissionais da área.
- Respostas curtas (até ~150 palavras), a menos que peçam mais detalhes.
- Não faça diagnósticos de saúde ou psicológicos.
"""


def _secret(nome: str):
    try:
        v = st.secrets.get(nome)
    except Exception:
        v = None
    return v or os.getenv(nome)


def provedor() -> str | None:
    """Retorna 'anthropic', 'vander', 'gemini' ou None."""
    if _secret("ANTHROPIC_API_KEY"):
        return "anthropic"
    if _secret("VANDER_API_URL"):
        return "vander"
    if st.session_state.get("user_api_key") or _secret("GEMINI_API_KEY"):
        return "gemini"
    return None


def _claude(historico, sistema) -> str:
    import anthropic

    modelo = _secret("ANTHROPIC_MODEL") or "claude-haiku-5-5"
    client = anthropic.Anthropic(api_key=_secret("ANTHROPIC_API_KEY"))
    resp = client.messages.create(
        model=modelo,
        max_tokens=700,
        system=sistema,
        messages=historico,
    )
    return "".join(b.text for b in resp.content if b.type == "text").strip()


def _vander(historico, sistema) -> str:
    url = _secret("VANDER_API_URL")
    chave = _secret("VANDER_API_KEY")
    modelo = _secret("VANDER_MODEL")
    headers = {"Content-Type": "application/json"}
    if chave:
        headers["Authorization"] = f"Bearer {chave}"
    corpo = {
        "messages": [{"role": "system", "content": sistema}] + historico,
        "temperature": 0.6,
    }
    if modelo:
        corpo["model"] = modelo
    r = requests.post(url, json=corpo, headers=headers, timeout=60)
    r.raise_for_status()
    dados = r.json()
    return dados["choices"][0]["message"]["content"].strip()


def _gemini(historico, sistema) -> str:
    from google import genai
    from google.genai import types

    chave = st.session_state.get("user_api_key") or _secret("GEMINI_API_KEY")
    modelo = _secret("GEMINI_MODEL") or "gemini-2.5-flash"
    client = genai.Client(api_key=chave)
    contents = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part(text=m["content"])],
        )
        for m in historico
    ]
    resp = client.models.generate_content(
        model=modelo,
        contents=contents,
        config=types.GenerateContentConfig(system_instruction=sistema, temperature=0.6),
    )
    return (resp.text or "").strip()


def conversar(historico: list[dict], contexto: str) -> str:
    """historico: lista de {role: user|assistant, content: str}. Começa sempre por 'user'."""
    sistema = PERSONA + "\n\nCONTEXTO DA PESSOA E DOS CURSOS:\n" + contexto
    p = provedor()
    if p == "anthropic":
        return _claude(historico, sistema)
    if p == "vander":
        return _vander(historico, sistema)
    if p == "gemini":
        return _gemini(historico, sistema)
    raise RuntimeError("Nenhum agente de IA configurado.")
