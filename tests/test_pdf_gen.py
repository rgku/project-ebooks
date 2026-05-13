import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from config import Niche
from pdf_gen import _add_cover, _add_title_page, EbookPDF


def test_ebookpdf_init():
    pdf = EbookPDF("Test Title")
    assert pdf.ebook_title == "Test Title"


def test_add_cover_creates_page(tmp_path):
    from PIL import Image
    cover = tmp_path / "cover.png"
    Image.new("RGB", (148, 210), (255, 255, 255)).save(cover)

    pdf = EbookPDF("Test")
    _add_cover(pdf, str(cover))
    assert pdf.page_no() == 1


def test_add_title_page_creates_page():
    pdf = EbookPDF("Test")
    niche = Niche(
        id="test",
        title="Test Title",
        subtitle="Test Subtitle",
        lang="en",
        cover_keywords="test",
        content_brief="test content",
        color1="#000000",
        color2="#FFFFFF",
    )
    _add_title_page(pdf, niche)
    assert pdf.page_no() >= 1


def test_header_footer_not_on_first_pages():
    pdf = EbookPDF("Test")
    assert pdf.page_no() == 0
    pdf.add_page()
    assert pdf.page_no() == 1
    pdf.add_page()
    assert pdf.page_no() == 2
