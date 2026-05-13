import re
import markdown
from pathlib import Path
from fpdf import FPDF, XPos, YPos

from config import Niche

FONT = "Helvetica"

_UNICODE_REPLACE = {
    "\u2014": "--",  # em dash
    "\u2013": "-",   # en dash
    "\u2018": "'",   # left single quote
    "\u2019": "'",   # right single quote
    "\u201c": '"',   # left double quote
    "\u201d": '"',   # right double quote
    "\u2026": "...", # ellipsis
    "\u00a0": " ",   # non-breaking space
    "\u2022": "-",   # bullet
    "\uf0b7": "-",   # bullet alt
    "\u25cf": "*",   # black circle
}

def _sanitize(text: str) -> str:
    for char, repl in _UNICODE_REPLACE.items():
        text = text.replace(char, repl)
    return text.encode("latin-1", "replace").decode("latin-1")


class EbookPDF(FPDF):
    def __init__(self, title: str):
        super().__init__(unit="mm", format=(148, 210))
        self.ebook_title = title

    def header(self):
        if self.page_no() <= 2:
            return
        self.set_font(FONT, "I", 7)
        self.set_text_color(160, 160, 160)
        self.cell(0, 4, self.ebook_title, align="L")
        self.ln(6)

    def footer(self):
        if self.page_no() <= 2:
            return
        self.set_y(-15)
        self.set_font(FONT, "I", 8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 10, str(self.page_no() - 2), align="C")


def _add_cover(pdf: EbookPDF, cover_path: str):
    pdf.add_page()
    pdf.image(cover_path, x=0, y=0, w=148, h=210)

def _add_title_page(pdf: EbookPDF, niche: Niche):
    pdf.add_page()
    pdf.ln(50)
    pdf.set_font(FONT, "B", 20)
    pdf.set_text_color(33, 33, 33)
    pdf.multi_cell(0, 12, _sanitize(niche.title), align="C")
    pdf.ln(8)
    pdf.set_font(FONT, "", 12)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 8, _sanitize(niche.subtitle), align="C")
    pdf.ln(16)
    pdf.set_font(FONT, "I", 10)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 8, "project-ebooks", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

def _convert_lists(text: str) -> str:
    lines = text.split("\n")
    out = []
    for line in lines:
        m = re.match(r"^(\s*)(\d+)\.\s+(.*)", line)
        if m:
            indent, num, rest = m.groups()
            out.append(f"{indent}**{num}.** {rest}")
        else:
            out.append(line)
    return "\n".join(out)

def _add_content(pdf: EbookPDF, markdown_text: str):
    text = _convert_lists(markdown_text)
    html = markdown.markdown(_sanitize(text), extensions=["extra"])
    pdf.set_font(FONT, "", 10)
    pdf.set_text_color(44, 44, 44)
    pdf.write_html(html)

def generate_pdf(niche: Niche, content_md: str, cover_path: str, output_path: str):
    pdf = EbookPDF(niche.title)
    _add_cover(pdf, cover_path)
    _add_title_page(pdf, niche)
    _add_content(pdf, content_md)
    pdf.output(output_path)
