import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from config import Niche

WIDTH = 1748
HEIGHT = 2480

def _hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def _find_font(bold: bool = False) -> str:
    paths = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        if Path(p).exists():
            return p
    return "DejaVuSans.ttf"

def _draw_gradient(draw: ImageDraw, color1: str, color2: str):
    r1, g1, b1 = _hex_to_rgb(color1)
    r2, g2, b2 = _hex_to_rgb(color2)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

def _draw_shapes(draw: ImageDraw):
    random.seed(42)
    for _ in range(4):
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 50)
        r = random.randint(100, 400)
        alpha = random.randint(15, 40)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, alpha))

def _draw_title_text(draw: ImageDraw, niche: Niche):
    font_bold = _find_font(bold=True)
    font_reg = _find_font()

    title = niche.title
    subtitle = niche.subtitle
    cx, cy = WIDTH // 2, HEIGHT // 2

    font_size = 90
    font = ImageFont.truetype(font_bold, font_size)
    bb = font.getbbox(title)
    tw = bb[2] - bb[0]
    while tw > WIDTH * 0.85 and font_size > 40:
        font_size -= 2
        font = ImageFont.truetype(font_bold, font_size)
        bb = font.getbbox(title)
        tw = bb[2] - bb[0]

    ty = cy - 200
    draw.text((cx + 3, ty + 3), title, fill=(0, 0, 0, 80), font=font, anchor="mm")
    draw.text((cx, ty), title, fill="white", font=font, anchor="mm")

    line_y = ty + font_size // 2 + 30
    line_w = 200
    draw.rectangle([cx - line_w // 2, line_y, cx + line_w // 2, line_y + 4], fill="white")

    sub_size = 40
    sub_font = ImageFont.truetype(font_reg, sub_size)
    bb = sub_font.getbbox(subtitle)
    sw = bb[2] - bb[0]
    while sw > WIDTH * 0.7 and sub_size > 20:
        sub_size -= 2
        sub_font = ImageFont.truetype(font_reg, sub_size)
        bb = sub_font.getbbox(subtitle)
        sw = bb[2] - bb[0]

    sub_y = line_y + 40
    draw.text((cx + 2, sub_y + 2), subtitle, fill=(0, 0, 0, 60), font=sub_font, anchor="mm")
    draw.text((cx, sub_y), subtitle, fill="white", font=sub_font, anchor="mm")

def generate_cover(niche: Niche, output_path: str):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    _draw_gradient(draw, niche.color1, niche.color2)
    _draw_shapes(draw)
    _draw_title_text(draw, niche)
    img.save(output_path, "PNG")
