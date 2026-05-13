import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from unittest.mock import patch, MagicMock
from main import generate_market
from config import Niche


def _make_market():
    return {
        "name": "en",
        "niches": [
            Niche(
                id="test-niche",
                title="Test Ebook Title Here",
                subtitle="Test Subtitle",
                lang="en",
                cover_keywords="test",
                content_brief="test",
                color1="#000000",
                color2="#FFFFFF",
            ),
        ],
        "price": 499,
        "currency": "usd",
    }


@patch("main.state.pick_next_niche")
@patch("main.state.mark_generated")
@patch("main.content_gen.generate_content")
@patch("main.cover_ai.generate_cover")
@patch("main.pdf_gen.generate_pdf")
@patch("main.epub_gen.generate_epub")
@patch("main.publisher.publish")
def test_generate_market_success(mock_publish, mock_epub, mock_pdf, mock_cover, mock_content, mock_mark, mock_pick):
    mock_pick.return_value = "test-niche"
    mock_content.return_value = "## Introduction\n\nContent.\n\n## Section 1\n\nBody.\n\n## Section 2\n\nBody.\n\n## Section 3\n\nBody.\n\n## Section 4\n\nBody.\n\n## Section 5\n\nBody.\n\n## Conclusion\n\nDone.\n\n## Next Steps\n\n- One\n- Two\n- Three\n- Four\n- Five\n\n"
    mock_publish.return_value = True

    market = _make_market()
    st = {"last_generated": None}
    ok, new_st = generate_market(market, st)

    assert ok is True
    assert new_st["en_last_success"] is not None
    mock_mark.assert_called_once_with("en", "test-niche")
    mock_content.assert_called_once()
    mock_cover.assert_called_once()
    mock_pdf.assert_called_once()
    mock_epub.assert_called_once()
    mock_publish.assert_called_once()


@patch("main.state.pick_next_niche")
@patch("main.state.mark_generated")
@patch("main.content_gen.generate_content")
@patch("main.cover_ai.generate_cover")
@patch("main.pdf_gen.generate_pdf")
@patch("main.epub_gen.generate_epub")
@patch("main.publisher.publish")
def test_generate_market_skip_publish(mock_publish, mock_epub, mock_pdf, mock_cover, mock_content, mock_mark, mock_pick):
    mock_pick.return_value = "test-niche"
    mock_content.return_value = "## Introduction\n\nContent.\n\n## Section 1\n\nBody.\n\n## Section 2\n\nBody.\n\n## Section 3\n\nBody.\n\n## Section 4\n\nBody.\n\n## Section 5\n\nBody.\n\n## Conclusion\n\nDone.\n\n## Next Steps\n\n- One\n- Two\n- Three\n- Four\n- Five\n\n"
    mock_publish.return_value = False

    market = _make_market()
    st = {"last_generated": None}
    ok, new_st = generate_market(market, st)

    assert ok is False
    mock_mark.assert_not_called()
