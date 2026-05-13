import re
import base64
import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

import requests
from log import logger
import config
import cover_gen as fallback_cover


def _generate_image_with_flux(prompt: str) -> Image.Image | None:
    api_key = config.get_api_key()
    if not api_key:
        logger.warning("No API key, falling back to PIL cover")
        return None

    try:
        resp = requests.post(
            f"{config.OPENROUTER_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": config.OPENROUTER_IMAGE_MODEL,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]

        match = re.search(r"data:image/(?:png|jpeg|webp);base64,([A-Za-z0-9+/=]+)", content)
        if not match:
            logger.warning("No base64 image in Flux response")
            return None

        img_data = base64.b64decode(match.group(1))
        return Image.open(io.BytesIO(img_data))

    except Exception as e:
        logger.warning(f"Flux generation failed: {e}")
        return None


def _resize_and_crop(img: Image.Image) -> Image.Image:
    target_w = config.COVER_IMAGE_WIDTH
    target_h = config.COVER_IMAGE_HEIGHT
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


def _overlay_text(draw: ImageDraw, niche: config.Niche):
    font_bold = fallback_cover._find_font(bold=True)
    font_reg = fallback_cover._find_font()
    cx, cy = config.COVER_IMAGE_WIDTH // 2, config.COVER_IMAGE_HEIGHT // 2

    font_size = 90
    font = ImageFont.truetype(font_bold, font_size)
    bb = font.getbbox(niche.title)
    tw = bb[2] - bb[0]
    while tw > config.COVER_IMAGE_WIDTH * 0.85 and font_size > 40:
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
    while sw > config.COVER_IMAGE_WIDTH * 0.7 and sub_size > 20:
        sub_size -= 2
        sub_font = ImageFont.truetype(font_reg, sub_size)
        bb = sub_font.getbbox(niche.subtitle)
        sw = bb[2] - bb[0]

    sub_y = line_y + 40
    draw.text((cx + 2, sub_y + 2), niche.subtitle, fill=(0, 0, 0, 120), font=sub_font, anchor="mm")
    draw.text((cx, sub_y), niche.subtitle, fill="white", font=sub_font, anchor="mm")


def generate_cover(niche: config.Niche, output_path: str):
    prompt = config.COVER_PROMPT_TEMPLATE.format(keywords=niche.cover_keywords)
    img = _generate_image_with_flux(prompt)

    if img is None:
        logger.info("Flux unavailable, using PIL fallback")
        fallback_cover.generate_cover(niche, output_path)
        return

    img = _resize_and_crop(img.convert("RGBA"))
    draw = ImageDraw.Draw(img)
    _overlay_text(draw, niche)
    img.save(output_path, "PNG")
    logger.info(f"AI cover saved: {output_path}")
