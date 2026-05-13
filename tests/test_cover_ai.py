import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import os
from unittest.mock import patch
from config import Niche


def _niche():
    return Niche(
        id="test", title="Test Title", subtitle="Test Subtitle",
        lang="en", cover_keywords="test modern minimal",
        content_brief="test", color1="#000000", color2="#FFFFFF",
    )


def test_fallback_to_pil(tmp_path):
    with patch("cover_ai._fetch_image", return_value=None):
        import cover_ai
        out = str(tmp_path / "cover.png")
        cover_ai.generate_cover(_niche(), out)
        assert os.path.exists(out)
        assert os.path.getsize(out) > 100


def test_ai_cover_creates_png(tmp_path):
    from PIL import Image
    fake = Image.new("RGB", (500, 500), (100, 150, 200))
    with patch("cover_ai._fetch_image", return_value=fake):
        import cover_ai
        out = str(tmp_path / "cover.png")
        cover_ai.generate_cover(_niche(), out)
        assert os.path.exists(out)
        assert os.path.getsize(out) > 100


def test_real_or_fallback(tmp_path):
    import cover_ai
    out = str(tmp_path / "cover.png")
    cover_ai.generate_cover(_niche(), out)
    assert os.path.exists(out)
    assert os.path.getsize(out) > 100
