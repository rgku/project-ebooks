import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import os
from unittest.mock import patch, MagicMock


def _content_md() -> str:
    return (
        "## Introduction\n\nIntro text.\n\n"
        "## Section 1\n\nBody 1.\n\n"
        "## Section 2\n\nBody 2.\n\n"
        "## Section 3\n\nBody 3.\n\n"
        "## Section 4\n\nBody 4.\n\n"
        "## Section 5\n\nBody 5.\n\n"
        "## Conclusion\n\nDone.\n\n"
        "## Next Steps\n\n- One\n- Two\n\n"
    )


def test_split_content_en():
    from epub_gen import _split_content
    chapters = _split_content(_content_md(), "en")
    assert len(chapters) == 8
    assert chapters[0][0] == "Introduction"
    assert chapters[1][0] == "Section 1"
    assert chapters[-1][0] == "Next Steps"


def test_split_content_pt():
    from epub_gen import _split_content
    chapters = _split_content(_content_md().replace("## Introduction", "## Introdução").replace("## Conclusion", "## Conclusão").replace("## Next Steps", "## Proximos Passos"), "pt")
    assert len(chapters) == 8


def test_split_content_fallback_when_missing():
    from epub_gen import _split_content
    chapters = _split_content("# Just a header\n\nSome text.", "en")
    assert len(chapters) == 1
    assert chapters[0][0] == "Introduction"


def test_generate_epub_creates_file(tmp_path):
    orig = os.getcwd()
    os.chdir(tmp_path)
    try:
        from config import Niche
        from epub_gen import generate_epub
        niche = Niche(
            id="test-niche",
            title="Test Ebook",
            subtitle="Test Sub",
            lang="en",
            cover_keywords="test",
            content_brief="test",
            color1="#000000",
            color2="#FFFFFF",
        )
        cover_path = str(tmp_path / "cover.png")
        from PIL import Image
        Image.new("RGBA", (100, 100)).save(cover_path)

        epub_path = str(tmp_path / "test.epub")
        generate_epub(niche, _content_md(), cover_path, epub_path)
        assert os.path.exists(epub_path)
        assert os.path.getsize(epub_path) > 500
    finally:
        os.chdir(orig)
