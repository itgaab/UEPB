"""Interesses, refinamento opcional e cálculo de compatibilidade com os cursos da UEPB.

O fluxo principal é por toque: a pessoa marca de 3 a 5 interesses (botões com emoji) e o ranking
sai na hora, por cálculo local (sem API). Opcionalmente ela refina o resultado com 3 perguntas
rápidas ou conta em uma frase o que quer.

Cada interesse e cada resposta somam pontos em 8 dimensões:
R prático/técnico · I investigativo/científico · A criativo/comunicação · S ensinar e ajudar
E liderar/empreender · C organização/dados · H saúde e cuidado · N natureza/ambiente
"""
import math
import re
import unicodedata

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

MAX_INTERESSES = 5
N_BASE = 16  # os primeiros 16 interesses aparecem sempre; o resto fica em "Ver mais interesses"
MIN_RECOMENDADO = 3

# id -> emoji, rótulo, pontos por dimensão, cursos afins (ganham um bônus, porque as 8 dimensões
# sozinhas não separam bem, por exemplo, computação de engenharia) e palavras-chave (usadas só para
# entender a frase livre quando a IA não está disponível).
INTERESSES = {
    "computadores": {
        "emoji": "💻", "rotulo": "Computadores",
        "cor": "#2563EB",
        "vetor": {"R": 2, "I": 2, "C": 1},
        "afins": ['Ciência da Computação', 'Tecnologia em Análise e Desenvolvimento de Sistemas', 'Tecnologia em Ciência de Dados', 'Estatística e Ciência de Dados'],
        "palavras": ["comput", "program", "tecnolog", "jogo", "game", "software", "sistema", "internet", "aplicativo", "site", "robo", "inteligencia artificial"],
    },
    "cuidar": {
        "emoji": "🩺", "rotulo": "Cuidar de pessoas",
        "cor": "#E11D48",
        "vetor": {"H": 3, "S": 2},
        "afins": ['Enfermagem', 'Fisioterapia', 'Psicologia', 'Odontologia', 'Farmácia'],
        "palavras": ["saude", "cuidar", "enferm", "medic", "hospital", "paciente", "psicolog", "terapia", "clinica", "dentista", "farmac"],
    },
    "natureza": {
        "emoji": "🌱", "rotulo": "Natureza",
        "cor": "#16A34A",
        "vetor": {"N": 3, "R": 1},
        "afins": ['Agronomia', 'Agroecologia', 'Engenharia Sanitária e Ambiental', 'Ciências Biológicas'],
        "palavras": ["natureza", "planta", "agricult", "ambient", "sustent", "ecolog", "floresta", "solo", "clima", "agro"],
    },
    "ensinar": {
        "emoji": "📚", "rotulo": "Ensinar",
        "cor": "#14B8A6",
        "vetor": {"S": 3, "A": 1},
        "afins": [],
        "palavras": ["ensin", "professor", "escola", "educa", "aula", "docen", "pedagog"],
    },
    "leis": {
        "emoji": "⚖️", "rotulo": "Leis e justiça",
        "cor": "#6D28D9",
        "vetor": {"E": 2, "C": 2, "S": 1},
        "afins": ['Direito'],
        "palavras": ["lei", "direito", "justica", "advog", "juiz", "promotor", "concurso", "tribunal"],
    },
    "numeros": {
        "emoji": "📊", "rotulo": "Números e dados",
        "cor": "#0891B2",
        "vetor": {"C": 3, "I": 2},
        "afins": ['Estatística', 'Estatística e Ciência de Dados', 'Ciências Contábeis', 'Tecnologia em Ciência de Dados', 'Matemática'],
        "palavras": ["numero", "matematica", "estatistic", "dados", "calcul", "financ", "contab", "analis", "grafico"],
    },
    "escrever": {
        "emoji": "✍️", "rotulo": "Escrever e criar",
        "cor": "#C026D3",
        "vetor": {"A": 3, "I": 1},
        "afins": ['Jornalismo', 'Letras Português'],
        "palavras": ["escrev", "redacao", "livro", "literat", "jornal", "texto", "roteiro", "poesia", "conteudo", "ler "],
    },
    "construir": {
        "emoji": "🔧", "rotulo": "Construir coisas",
        "cor": "#EA580C",
        "vetor": {"R": 3, "I": 1},
        "afins": ['Engenharia Civil', 'Tecnologia em Sistemas de Energias Renováveis', 'Química Industrial'],
        "palavras": ["constru", "engenh", "obra", "maquina", "mecanic", "eletric", "montar", "consertar", "projetar"],
    },
    "ciencia": {
        "emoji": "🔬", "rotulo": "Ciência e pesquisa",
        "cor": "#4338CA",
        "vetor": {"I": 3, "R": 1},
        "afins": ['Física', 'Química', 'Ciências Biológicas', 'Química Industrial'],
        "palavras": ["ciencia", "pesquis", "laborat", "quimic", "fisic", "biolog", "descobr", "cientist", "experiment"],
    },
    "esporte": {
        "emoji": "🏃", "rotulo": "Esporte e corpo",
        "cor": "#DC2626",
        "vetor": {"H": 3, "S": 1, "R": 1},
        "afins": ['Educação Física', 'Fisioterapia'],
        "palavras": ["esport", "academia", "atlet", "futebol", "treino", "corpo", "fisioter", "corrida"],
    },
    "negocios": {
        "emoji": "💼", "rotulo": "Negócios e dinheiro",
        "cor": "#CA8A04",
        "vetor": {"E": 3, "C": 2},
        "afins": ['Administração', 'Ciências Contábeis'],
        "palavras": ["negocio", "empreend", "empresa", "vend", "dinheiro", "gestao", "administr", "lider", "chefe", "marketing"],
    },
    "arte": {
        "emoji": "🎨", "rotulo": "Arte e design",
        "cor": "#DB2777",
        "vetor": {"A": 3, "E": 1},
        "afins": ['Jornalismo'],
        "palavras": ["arte", "desenh", "design", "pintur", "music", "teatro", "cinema", "fotograf", "criativ"],
    },
    "animais": {
        "emoji": "🐾", "rotulo": "Animais e campo",
        "cor": "#65A30D",
        "vetor": {"N": 2, "H": 1, "R": 1},
        "afins": ['Agronomia', 'Agroecologia', 'Ciências Biológicas'],
        "palavras": ["animal", "pet", "veterin", "fazenda", "cavalo", "gado", "bicho", "rural", "campo"],
    },
    "comunicar": {
        "emoji": "🎤", "rotulo": "Comunicar e falar",
        "cor": "#0369A1",
        "vetor": {"A": 2, "E": 2, "S": 1},
        "afins": ['Jornalismo', 'Relações Internacionais'],
        "palavras": ["comunic", "apresent", "palestr", "entrevist", "influenc", "falar", "midia", "radio", "podcast", "reporter"],
    },
    "sociedade": {
        "emoji": "🌍", "rotulo": "Sociedade e história",
        "cor": "#B45309",
        "vetor": {"S": 2, "I": 2, "A": 1},
        "afins": ['História', 'Sociologia', 'Geografia', 'Serviço Social', 'Filosofia'],
        "palavras": ["sociedade", "social", "historia", "politica", "desigualdade", "comunidade", "direitos humanos", "filosof", "geografia", "cultura"],
    },
    "idiomas": {
        "emoji": "🗣️", "rotulo": "Idiomas e culturas",
        "cor": "#0F766E",
        "vetor": {"A": 2, "S": 1, "E": 1},
        "afins": ['Letras Inglês', 'Letras Espanhol', 'Relações Internacionais'],
        "palavras": ["idioma", "ingles", "espanhol", "lingua", "traduc", "viajar", "intercambio", "estrangeir"],
    },
    "mente": {
        "emoji": "🧠", "rotulo": "Mente e comportamento",
        "cor": "#7C3AED",
        "vetor": {"H": 2, "I": 2, "S": 1},
        "afins": ["Psicologia"],
        "palavras": ["mente", "comportament", "psicolog", "emocao", "emocoes", "terapia", "ansiedade", "cerebro"],
    },
    "comunidade": {
        "emoji": "🤝", "rotulo": "Ajudar a comunidade",
        "cor": "#EA580C",
        "vetor": {"S": 3, "H": 1},
        "afins": ["Serviço Social", "Sociologia", "Pedagogia"],
        "palavras": ["comunidade", "voluntar", "ong", "ajudar", "desigualdade", "pobreza", "direitos"],
    },
    "politica": {
        "emoji": "🏛️", "rotulo": "Política e governo",
        "cor": "#1D4ED8",
        "vetor": {"E": 2, "C": 1, "S": 1, "I": 1},
        "afins": ["Relações Internacionais", "Direito", "Sociologia"],
        "palavras": ["politic", "governo", "diplomac", "eleic", "relacoes internacionais", "onu", "estado"],
    },
    "cidades": {
        "emoji": "🏗️", "rotulo": "Cidades e obras",
        "cor": "#B45309",
        "vetor": {"R": 3, "C": 1},
        "afins": ["Engenharia Civil", "Engenharia Sanitária e Ambiental", "Geografia"],
        "palavras": ["cidade", "obra", "predio", "casa", "urban", "arquitet", "infraestrutura", "ponte", "estrada"],
    },
    "energia": {
        "emoji": "⚡", "rotulo": "Energia e sustentabilidade",
        "cor": "#CA8A04",
        "vetor": {"R": 2, "N": 2, "I": 1},
        "afins": ["Tecnologia em Sistemas de Energias Renováveis", "Engenharia Sanitária e Ambiental", "Física"],
        "palavras": ["energia", "solar", "eolic", "sustent", "renovav", "eletric"],
    },
    "agua": {
        "emoji": "💧", "rotulo": "Água e saneamento",
        "cor": "#0284C7",
        "vetor": {"N": 3, "R": 1, "H": 1},
        "afins": ["Engenharia Sanitária e Ambiental", "Engenharia Civil", "Química Industrial"],
        "palavras": ["agua", "saneamento", "esgoto", "rio", "seca", "residuo", "lixo", "reciclag"],
    },
    "quimica": {
        "emoji": "🧪", "rotulo": "Química e laboratório",
        "cor": "#9333EA",
        "vetor": {"I": 3, "R": 1},
        "afins": ["Química", "Química Industrial", "Farmácia"],
        "palavras": ["quimic", "reacao", "laborat", "substanc", "medicamento", "industria"],
    },
    "matematica": {
        "emoji": "🧮", "rotulo": "Matemática e lógica",
        "cor": "#0F766E",
        "vetor": {"I": 2, "C": 3},
        "afins": ["Matemática", "Estatística", "Ciência da Computação", "Física"],
        "palavras": ["matematic", "logica", "equacao", "problema", "calculo", "raciocinio", "enigma"],
    },
    "jogos": {
        "emoji": "🎮", "rotulo": "Jogos e criação digital",
        "cor": "#DB2777",
        "vetor": {"R": 2, "A": 2, "I": 1},
        "afins": ["Ciência da Computação", "Tecnologia em Análise e Desenvolvimento de Sistemas"],
        "palavras": ["jogo", "game", "animacao", "aplicativo", "app ", "desenvolv", "criar site"],
    },
    "redes": {
        "emoji": "📱", "rotulo": "Redes sociais e conteúdo",
        "cor": "#E11D48",
        "vetor": {"A": 3, "E": 1},
        "afins": ["Jornalismo"],
        "palavras": ["rede social", "instagram", "tiktok", "youtube", "influenc", "conteudo", "video", "edicao"],
    },
    "agro": {
        "emoji": "🚜", "rotulo": "Alimentos e agricultura",
        "cor": "#4D7C0F",
        "vetor": {"N": 3, "R": 1, "E": 1},
        "afins": ["Agronomia", "Agroecologia"],
        "palavras": ["agricult", "alimento", "colheita", "fazenda", "plantio", "comida", "agro", "produzir"],
    },
    "inovar": {
        "emoji": "🚀", "rotulo": "Inovação e empreender",
        "cor": "#4338CA",
        "vetor": {"E": 3, "I": 1, "R": 1},
        "afins": ["Administração", "Tecnologia em Análise e Desenvolvimento de Sistemas"],
        "palavras": ["inovac", "startup", "empreend", "ideia", "criar empresa", "tecnolog"],
    },
}


def rotulo_interesse(i: str) -> str:
    d = INTERESSES[i]
    return f"{d['emoji']} {d['rotulo']}"


# Perguntas opcionais do "Quero um resultado mais preciso" (opções -> pontos por dimensão).
REFINAR = [
    {
        "id": "r1",
        "titulo": "Que tipo de problema você gostaria de resolver no trabalho?",
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
        "id": "r2",
        "titulo": "Em que ambiente você se imagina trabalhando?",
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
        "id": "r3",
        "titulo": "O que é mais importante para você na carreira?",
        "opcoes": {
            "Ajudar as pessoas e a sociedade": {"S": 2, "H": 2},
            "Estabilidade e concurso público": {"C": 2, "S": 1},
            "Bom salário e crescimento": {"E": 2, "C": 1, "R": 1},
            "Criatividade e liberdade": {"A": 3, "E": 1},
            "Descobrir coisas novas e pesquisar": {"I": 3},
            "Trabalhar com sustentabilidade": {"N": 3, "I": 1},
        },
    },
]


def chave(curso: dict) -> str:
    """Identificador único do curso (o mesmo nome pode ter bacharelado e licenciatura)."""
    return f"{curso['nome']}|{curso['grau']}"


def vetor_total(interesses: list[str], refino: dict | None = None, votos: dict | None = None) -> dict:
    """Soma os pontos dos interesses, do refinamento e dos votos do modo arrastar em cada dimensão."""
    v = {d: 0.0 for d in DIMS}
    for i in interesses:
        for dim, pts in INTERESSES[i]["vetor"].items():
            v[dim] += pts
    for q in REFINAR:
        resp = (refino or {}).get(q["id"])
        for dim, pts in q["opcoes"].get(resp, {}).items():
            v[dim] += pts
    # Modo arrastar: curtir puxa o perfil para o curso; não curtir afasta um pouco.
    for c in CURSOS:
        voto = (votos or {}).get(chave(c))
        if voto:
            peso = 0.6 if voto > 0 else -0.25
            for dim, p in zip(DIMS, c["perfil"]):
                v[dim] += peso * p
    for dim in DIMS:
        v[dim] = max(0.0, v[dim])
    return v


def _cos(a, b):
    num = sum(x * y for x, y in zip(a, b))
    den = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return num / den if den else 0.0


BONUS_AFIM = 6
BONUS_AFIM_MAX = 12


def _afim(curso: dict, i: str) -> bool:
    return curso["nome"] in INTERESSES[i]["afins"]


def ranking(vetor: dict, interesses=(), cidades=None, so_cidades=False, votos=None):
    """Lista de cursos ordenada por compatibilidade (0 a 100)."""
    u = [vetor[d] for d in DIMS]
    resultado = []
    for c in CURSOS:
        nas_cidades = {k: t for k, t in c["campi"].items() if k in cidades} if cidades else {}
        if cidades and so_cidades and not nas_cidades:
            continue
        voto = (votos or {}).get(chave(c), 0)
        if voto < 0:
            continue  # cursos que a pessoa descartou no modo arrastar saem do resultado
        sim = _cos(u, list(c["perfil"]))
        # Cosseno ao quadrado: separa melhor os cursos e quase nunca chega a 100%.
        pct = 100.0 * sim * sim
        pct += min(BONUS_AFIM_MAX, BONUS_AFIM * sum(_afim(c, i) for i in interesses))
        if nas_cidades:
            pct += 2
        if voto > 0:
            pct += 4
        # Escala 0,9 para o topo não ficar todo em 99% e os cursos continuarem distinguíveis.
        pct = min(99.0, pct * 0.9)
        resultado.append({**c, "afinidade": round(pct), "nas_cidades": nas_cidades})
    resultado.sort(key=lambda x: x["afinidade"], reverse=True)
    return resultado


def motivo(curso: dict, interesses: list[str], vetor: dict) -> str:
    """Uma linha de 'por que combina', calculada localmente."""
    pontuacoes = []
    for i in interesses:
        iv = INTERESSES[i]["vetor"]
        total = sum(iv.values())
        s = sum(pts * curso["perfil"][DIMS.index(d)] for d, pts in iv.items()) / total
        if _afim(curso, i):
            s += 5  # curso afim passa na frente na explicação
        pontuacoes.append((s, i))
    pontuacoes.sort(reverse=True)
    bons = [i for s, i in pontuacoes if s >= 2.5][:2]
    if bons:
        nomes = " e ".join(f"**{rotulo_interesse(i)}**" for i in bons)
        return f"Combina com o que você curte: {nomes}."
    melhor = max(DIMS, key=lambda d: vetor[d] * curso["perfil"][DIMS.index(d)])
    return f"Combina com o seu perfil: **{DIM_NOMES[melhor]}**."


def _normaliza(txt: str) -> str:
    txt = unicodedata.normalize("NFD", txt.lower())
    txt = "".join(ch for ch in txt if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", txt)


def interpretar_por_palavras(texto: str, limite: int = 4) -> list[str]:
    """Plano B sem IA: encontra interesses pelas palavras da frase."""
    t = " " + _normaliza(texto) + " "
    achados = []
    for i, d in INTERESSES.items():
        n = sum(1 for p in d["palavras"] if p in t)
        if n:
            achados.append((n, i))
    achados.sort(key=lambda x: -x[0])
    return [i for _, i in achados[:limite]]


def resumo_refino(refino: dict) -> str:
    linhas = []
    for q in REFINAR:
        r = (refino or {}).get(q["id"])
        if r:
            linhas.append(f"- {q['titulo']} {r}")
    return "\n".join(linhas)
