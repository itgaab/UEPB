"""Gera a imagem do resultado (1080x1350) para a pessoa baixar e compartilhar."""
import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).parent / "assets"
W, H = 1080, 1350
NAVY = (11, 42, 85)
NAVY_ESCURO = (7, 27, 58)


def _fonte(tamanho: int, negrito: bool = False):
    nome = "DejaVuSans-Bold.ttf" if negrito else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(str(ASSETS / "fonts" / nome), tamanho)
    except OSError:
        return ImageFont.load_default()


def _ajusta(draw, texto: str, fonte_px: int, largura: int, negrito: bool = True):
    """Reduz a fonte até o texto caber na largura."""
    for px in range(fonte_px, 20, -2):
        f = _fonte(px, negrito)
        if draw.textlength(texto, font=f) <= largura:
            return f
    return _fonte(20, negrito)


def gerar_imagem(cursos: list[dict], interesses: list[str]) -> bytes:
    """cursos: [{nome, grau, afinidade, cor: (r, g, b)}]; interesses: rótulos sem emoji."""
    img = Image.new("RGB", (W, H), NAVY)
    # Fundo em degradê vertical.
    topo, base = NAVY, NAVY_ESCURO
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(topo[i] + (base[i] - topo[i]) * t) for i in range(3)))

    # Sigma gigante, bem discreto, ao fundo.
    sigma = Image.open(ASSETS / "sigma_branco.png").convert("RGBA")
    marca = sigma.copy()
    marca.thumbnail((900, 900))
    alfa = marca.getchannel("A").point(lambda v: int(v * 0.06))
    marca.putalpha(alfa)
    img.paste(marca, (W - marca.width + 120, 330), marca)

    d = ImageDraw.Draw(img)
    logo = sigma.copy()
    logo.thumbnail((64, 64))
    img.paste(logo, (64, 60), logo)
    d.text((148, 66), "UEPB Orienta", font=_fonte(34, True), fill="white")
    d.text((148, 108), "VANDER IA", font=_fonte(22), fill=(160, 190, 240))

    d.text((64, 190), "Meu resultado", font=_fonte(78, True), fill="white")
    d.text((64, 282), "Os cursos da UEPB que mais combinam comigo", font=_fonte(30), fill=(185, 205, 240))

    # Interesses em "chips".
    x, y = 64, 350
    f_chip = _fonte(28, True)
    for rot in interesses[:8]:
        w = int(d.textlength(rot, font=f_chip)) + 44
        if x + w > W - 64:
            x, y = 64, y + 62
        d.rounded_rectangle((x, y, x + w, y + 50), radius=25, fill=(255, 255, 255, 255))
        d.text((x + 22, y + 8), rot, font=f_chip, fill=NAVY)
        x += w + 14

    # Cartões dos cursos.
    y0 = max(y + 100, 470)
    altura, gap = 138, 18
    for i, c in enumerate(cursos[:5], start=1):
        top = y0 + (i - 1) * (altura + gap)
        d.rounded_rectangle((64, top, W - 64, top + altura), radius=28, fill="white")
        d.rounded_rectangle((64, top, 82, top + altura), radius=9, fill=c["cor"])
        d.text((112, top + 34), str(i), font=_fonte(54, True), fill=c["cor"])
        f_nome = _ajusta(d, c["nome"], 38, 560)
        d.text((190, top + 24), c["nome"], font=f_nome, fill=NAVY)
        d.text((190, top + 78), c["grau"], font=_fonte(26), fill=(100, 116, 145))
        pct = c["afinidade"]
        d.text((W - 96, top + 28), f"{pct}%", font=_fonte(52, True), fill=NAVY, anchor="ra")
        bx0, bx1, by = 780, W - 96, top + 100
        d.rounded_rectangle((bx0, by, bx1, by + 14), radius=7, fill=(226, 232, 244))
        d.rounded_rectangle((bx0, by, bx0 + int((bx1 - bx0) * pct / 100), by + 14), radius=7, fill=c["cor"])

    d.text((64, H - 84), "É um ponto de partida, não uma sentença. Confirme turnos e vagas em uepb.edu.br.",
           font=_fonte(22), fill=(160, 190, 240))

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
