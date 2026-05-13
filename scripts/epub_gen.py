import re
import markdown
from pathlib import Path
from ebooklib import epub

from config import Niche
from log import logger

CSS = """
body { font-family: Georgia, serif; line-height: 1.6; margin: 1em; font-size: 1em; color: #333; }
h1 { font-size: 1.8em; margin-top: 1.5em; color: #1a1a1a; }
h2 { font-size: 1.4em; margin-top: 1.2em; color: #1a1a1a; }
p { margin: 0.8em 0; text-align: justify; }
ul { margin: 0.5em 0; padding-left: 1.5em; }
li { margin: 0.3em 0; }
strong { color: #000; }
"""


def _split_content(markdown_text: str, lang: str) -> list[tuple[str, str]]:
    lines = markdown_text.strip().split("\n")
    chapters = []
    current_title = ""
    current_body = []

    for line in lines:
        if line.startswith("## "):
            if current_body:
                chapters.append((current_title, "\n".join(current_body)))
            current_title = line.strip("# ")
            current_body = []
        else:
            current_body.append(line)

    if current_body:
        chapters.append((current_title, "\n".join(current_body)))

    chapters = [(t, b) for t, b in chapters if t or b.strip()]
    intro_label = "Introduction" if lang == "en" else "Introdução"
    if not chapters:
        chapters = [(intro_label, markdown_text)]
    elif not chapters[0][0]:
        chapters[0] = (intro_label, chapters[0][1])

    return chapters


def generate_epub(niche: Niche, content_md: str, cover_path: str, output_path: str):
    book = epub.EpubBook()
    book.set_title(niche.title)
    lang_code = "en" if niche.lang == "en" else "pt"
    book.set_language(lang_code)
    book.add_author("project-ebooks")

    with open(cover_path, "rb") as fh:
        book.set_cover("cover.png", fh.read())

    css_item = epub.EpubItem(
        uid="style",
        file_name="style/style.css",
        media_type="text/css",
        content=CSS,
    )
    book.add_item(css_item)

    chapters = _split_content(content_md, niche.lang)
    epub_chapters = []
    toc_items = []

    for i, (title, body) in enumerate(chapters):
        html_body = markdown.markdown(body, extensions=["extra"]) if body.strip() else "<p></p>"
        safe_title = (title or niche.title).strip() or f"Chapter {i+1}"
        xhtml = f"""<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>{safe_title}</title>
<link rel="stylesheet" type="text/css" href="style/style.css"/></head>
<body><h2>{safe_title}</h2>{html_body}</body></html>"""

        chapter = epub.EpubHtml(
            title=safe_title,
            file_name=f"chap_{i:02d}.xhtml",
            lang=lang_code,
        )
        chapter.content = xhtml
        chapter.add_item(css_item)
        book.add_item(chapter)
        epub_chapters.append(chapter)
        toc_items.append(epub.Link(f"chap_{i:02d}.xhtml", safe_title, f"chap_{i:02d}"))

    book.toc = tuple(toc_items)

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    spine = ["nav"] + epub_chapters
    book.spine = spine

    epub.write_epub(output_path, book)
    logger.info(f"EPUB saved: {output_path} ({len(chapters)} chapters)")
