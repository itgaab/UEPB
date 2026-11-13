"""Questionário (9 questões) e cálculo de compatibilidade com os cursos da UEPB.

Cada resposta soma pontos em 8 dimensões:
R prático/técnico · I investigativo/científico · A criativo/comunicação · S ensinar e ajudar
E liderar/empreender · C organização/dados · H saúde e cuidado · N natureza/ambiente
"""
import math

from cursos_uepb import CURSOS

DIMS = ["R", "I", "A", "S", "E", "C", "H", "N"]
DIM_NOMES = {
    "R": "Prático e técnico",
    "I": "Investigativo e científico",
    "A": "Criativo e comunicativo",
    "S": "Ensinar e ajudar pessoas",
    "E": "Liderar e empreender",
    "C": "Organização e dados",
    "H": "Saúde e cuidado",
    "N": "Natureza e ambiente",
}

# Cada questão: id, título, tipo ("one" ou "multi"), opções {texto: {dim: pontos}}
QUESTOES = [
    {
        "id": "q1",
        "titulo": "1. No tempo livre, o que você mais gosta de fazer?",
        "tipo": "one",
        "opcoes": {
            "Mexer em computador, jogos, programação ou aparelhos": {"R": 2, "I": 2, "C": 1},
            "Ler, escrever, desenhar, criar vídeos ou música": {"A": 3, "I": 1},
            "Ajudar amigos e familiares com seus problemas": {"S": 3, "H": 1},
            "Praticar esporte ou cuidar do corpo": {"H": 3, "S": 1},
            "Organizar coisas, planejar, juntar dinheiro": {"C": 3, "E": 1},
            "Ficar ao ar livre, com plantas e animais": {"N": 3, "R": 1},
        },
    },
    {
        "id": "q2",
        "titulo": "2. Que tipo de problema você gostaria de resolver no trabalho?",
        "tipo": "one",
        "opcoes": {
            "Fazer um sistema ou máquina funcionar melhor": {"R": 3, "I": 1},
            "Descobrir a causa de algo com pesquisa e análise": {"I": 3, "C": 1},
            "Ajudar alguém a se curar ou a se sentir melhor": {"H": 3, "S": 1},
            "Ensinar e ajudar alguém a aprender": {"S": 3, "A": 1},
            "Fazer um negócio ou equipe crescer": {"E": 3, "C": 1},
            "Defender direitos e resolver conflitos": {"S": 2, "E": 1, "C": 1},
            "Cuidar do meio ambiente e da produção de alimentos": {"N": 3, "R": 1},
        },
    },
    {
        "id": "q3",
        "titulo": "3. Em que ambiente você se imagina trabalhando?",
        "tipo": "one",
        "opcoes": {
            "Escritório ou home office, com computador": {"C": 2, "I": 1, "R": 1},
            "Hospital, clínica ou unidade de saúde": {"H": 3, "S": 1},
            "Escola ou universidade": {"S": 3, "A": 1},
            "Campo, obra, laboratório ou indústria": {"R": 2, "N": 1, "I": 1},
            "Redação, estúdio ou ambiente criativo": {"A": 3},
            "Meu próprio negócio, com autonomia": {"E": 3, "C": 1},
        },
    },
    {
        "id": "q4",
        "titulo": "4. Quais matérias ou temas você mais gosta? (escolha até 3)",
        "tipo": "multi",
        "max": 3,
        "opcoes": {
            "Matemática": {"I": 2, "C": 2},
            "Física e Química": {"I": 2, "R": 2},
            "Biologia": {"H": 1, "N": 2, "I": 1},
            "História, Geografia e Sociologia": {"S": 1, "A": 1, "N": 1},
            "Português, Literatura e Redação": {"A": 3},
            "Inglês ou Espanhol": {"A": 2, "E": 1},
            "Informática e tecnologia": {"R": 2, "I": 1, "C": 1},
            "Educação Física e esportes": {"H": 2, "S": 1},
            "Artes": {"A": 3},
        },
    },
    {
        "id": "q5",
        "titulo": "5. Em um trabalho em grupo, você costuma ser quem...",
        "tipo": "one",
        "opcoes": {
            "Lidera e distribui as tarefas": {"E": 3, "C": 1},
            "Organiza prazos e cuida dos detalhes": {"C": 3},
            "Tem as ideias criativas": {"A": 3, "I": 1},
            "Pesquisa e aprofunda o conteúdo": {"I": 3},
            "Mantém o grupo unido e ajuda os colegas": {"S": 3, "H": 1},
            "Põe a mão na massa e executa": {"R": 3},
        },
    },
    {
        "id": "q6",
        "titulo": "6. O que é mais importante para você na carreira?",
        "tipo": "one",
        "opcoes": {
            "Ajudar as pessoas e a sociedade": {"S": 2, "H": 2},
            "Estabilidade e concurso público": {"C": 2, "S": 1},
            "Bom salário e crescimento": {"E": 2, "C": 1, "R": 1},
            "Criatividade e liberdade": {"A": 3, "E": 1},
            "Descobrir coisas novas e pesquisar": {"I": 3},
            "Trabalhar com sustentabilidade": {"N": 3, "I": 1},
        },
    },
    {
        "id": "q7",
        "titulo": "7. Com o que você prefere lidar no dia a dia?",
        "tipo": "one",
        "opcoes": {
            "Pessoas (atender, ensinar, cuidar)": {"S": 3, "H": 1},
            "Dados, números e documentos": {"C": 3, "I": 1},
            "Máquinas, programas e equipamentos": {"R": 3},
            "Ideias, textos e conteúdos": {"A": 2, "I": 2},
            "Plantas, animais e ambiente": {"N": 3},
            "Dinheiro, vendas e negócios": {"E": 3, "C": 1},
        },
    },
    {
        "id": "q8",
        "titulo": "8. Diante de um desafio difícil, você normalmente...",
        "tipo": "one",
        "opcoes": {
            "Estuda a fundo até entender": {"I": 3},
            "Testa na prática até funcionar": {"R": 3, "I": 1},
            "Conversa com outras pessoas para decidir": {"S": 2, "E": 1},
            "Faz um plano com etapas e prazos": {"C": 3},
            "Busca uma solução criativa e diferente": {"A": 3, "E": 1},
            "Assume a frente e toma a decisão": {"E": 3},
        },
    },
    {
        "id": "q9",
        "titulo": "9. Em quais cidades você poderia estudar? (pode marcar várias)",
        "tipo": "cidades",
        "opcoes": {},
    },
]


def vetor_usuario(respostas: dict) -> dict:
    """Soma os pontos das respostas em cada dimensão."""
    v = {d: 0.0 for d in DIMS}
    for q in QUESTOES:
        if q["tipo"] == "cidades":
            continue
        resp = respostas.get(q["id"])
        if not resp:
            continue
        escolhidas = resp if isinstance(resp, list) else [resp]
        for esc in escolhidas:
            for dim, pts in q["opcoes"].get(esc, {}).items():
                v[dim] += pts
    return v


def _cos(a, b):
    num = sum(x * y for x, y in zip(a, b))
    den = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return num / den if den else 0.0


def ranking(respostas: dict, cidades=None, graus=None, so_cidades=False):
    """Retorna a lista de cursos ordenada por compatibilidade (0 a 100)."""
    v = vetor_usuario(respostas)
    u = [v[d] for d in DIMS]
    resultado = []
    for c in CURSOS:
        if graus and c["grau"] not in graus:
            continue
        campi = c["campi"]
        if cidades:
            nas_cidades = {k: t for k, t in campi.items() if k in cidades}
            if so_cidades and not nas_cidades:
                continue
        else:
            nas_cidades = {}
        sim = _cos(u, list(c["perfil"]))
        # Similaridade de cosseno ao quadrado: separa melhor os cursos e quase nunca chega a 100%.
        pct = 100.0 * sim * sim
        if nas_cidades:
            pct = min(99.0, pct + 2)
        resultado.append({**c, "afinidade": round(pct), "nas_cidades": nas_cidades})
    resultado.sort(key=lambda x: x["afinidade"], reverse=True)
    return resultado, v


def resumo_respostas(respostas: dict) -> str:
    linhas = []
    for q in QUESTOES:
        r = respostas.get(q["id"])
        if r:
            linhas.append(f"- {q['titulo']} {', '.join(r) if isinstance(r, list) else r}")
    return "\n".join(linhas)
