import io
import base64
import requests
from PIL import Image, ImageDraw, ImageFont
from log import logger
import config
import cover_gen

WIDTH = config.COVER_IMAGE_WIDTH
HEIGHT = config.COVER_IMAGE_HEIGHT
IMAGE_MODEL = "google/gemini-2.5-flash-image"


def _fetch_image(prompt: str) -> Image.Image | None:
    api_key = config.get_api_key()
    if not api_key:
        logger.warning("No API key for image generation")
        return None
    try:
        resp = requests.post(
            f"{config.OPENROUTER_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": IMAGE_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "modalities": ["image"],
            },
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        images = data.get("choices", [{}])[0].get("message", {}).get("images", [])
        if images:
            url = images[0].get("image_url", {}).get("url", "")
            if url.startswith("data:image"):
                _, b64 = url.split(",", 1)
                return Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGBA")
        logger.warning("No image in response")
        return None
    except Exception as e:
        logger.warning(f"Image generation failed: {e}")
        return None


def _resize_and_crop(img: Image.Image) -> Image.Image:
    target_w, target_h = WIDTH, HEIGHT
    img_ratio = img.width / img.height
    target_ratio = target_w / target_h
    if img_ratio > target_ratio:
        new_w = int(img.height * target_ratio)
        offset = (img.width - new_w) // 2
        img = img.crop((offset, 0, offset + new_w, img.height))
    else:
        new_h = int(img.width / target_ratio)
        offset = (img.height - new_h) // 2
        img = img.crop((0, offset, img.width, offset + new_h))
    return img.resize((target_w, target_h), Image.LANCZOS)


def _overlay_text(img: Image.Image, niche: config.Niche):
    draw = ImageDraw.Draw(img)
    font_bold = cover_gen._find_font(bold=True)
    font_reg = cover_gen._find_font()
    cx, cy = WIDTH // 2, HEIGHT // 2

    font_size = 90
    font = ImageFont.truetype(font_bold, font_size)
    bb = font.getbbox(niche.title)
    tw = bb[2] - bb[0]
    while tw > WIDTH * 0.85 and font_size > 40:
        font_size -= 2
        font = ImageFont.truetype(font_bold, font_size)
        bb = font.getbbox(niche.title)
        tw = bb[2] - bb[0]

    ty = cy - 200
    draw.text((cx + 3, ty + 3), niche.title, fill=(0, 0, 0, 160), font=font, anchor="mm")
    draw.text((cx, ty), niche.title, fill="white", font=font, anchor="mm")

    line_y = ty + font_size // 2 + 30
    draw.rectangle([cx - 100, line_y, cx + 100, line_y + 4], fill="white")

    sub_size = 40
    sub_font = ImageFont.truetype(font_reg, sub_size)
    bb = sub_font.getbbox(niche.subtitle)
    sw = bb[2] - bb[0]
    while sw > WIDTH * 0.7 and sub_size > 20:
        sub_size -= 2
        sub_font = ImageFont.truetype(font_reg, sub_size)
        bb = sub_font.getbbox(niche.subtitle)
        sw = bb[2] - bb[0]

    sub_y = line_y + 40
    draw.text((cx + 2, sub_y + 2), niche.subtitle, fill=(0, 0, 0, 120), font=sub_font, anchor="mm")
    draw.text((cx, sub_y), niche.subtitle, fill="white", font=sub_font, anchor="mm")


def generate_cover(niche: config.Niche, output_path: str):
    prompt = f"Professional ebook cover, {niche.cover_keywords}, clean design, high quality, visually striking, 2:3 portrait aspect ratio, no text"
    img = _fetch_image(prompt)

    if img is not None:
        img = _resize_and_crop(img)
        _overlay_text(img, niche)
        img.save(output_path, "PNG")
        logger.info(f"AI cover saved: {output_path}")
        return

    logger.info("Image model unavailable, using PIL fallback")
    cover_gen.generate_cover(niche, output_path)
