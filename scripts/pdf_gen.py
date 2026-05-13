import markdown
from pathlib import Path
from fpdf import FPDF, XPos, YPos

from config import Niche

FONT = "Helvetica"


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
    pdf.multi_cell(0, 12, niche.title, align="C")
    pdf.ln(8)
    pdf.set_font(FONT, "", 12)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 8, niche.subtitle, align="C")
    pdf.ln(16)
    pdf.set_font(FONT, "I", 10)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 8, "project-ebooks", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

def _add_content(pdf: EbookPDF, markdown_text: str):
    html = markdown.markdown(markdown_text, extensions=["extra"])
    pdf.set_font(FONT, "", 10)
    pdf.set_text_color(44, 44, 44)
    pdf.write_html(html)

def generate_pdf(niche: Niche, content_md: str, cover_path: str, output_path: str):
    pdf = EbookPDF(niche.title)
    _add_cover(pdf, cover_path)
    _add_title_page(pdf, niche)
    _add_content(pdf, content_md)
    pdf.output(output_path)
