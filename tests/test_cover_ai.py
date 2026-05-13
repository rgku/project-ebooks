import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import os
from unittest.mock import patch, MagicMock
from config import Niche


def _niche():
    return Niche(
        id="test",
        title="Test Title",
        subtitle="Test Subtitle",
        lang="en",
        cover_keywords="test modern minimal",
        content_brief="test",
        color1="#000000",
        color2="#FFFFFF",
    )


def test_fallback_on_no_api_key(tmp_path):
    orig = os.getcwd()
    os.chdir(tmp_path)
    try:
        with patch("cover_ai.config.get_api_key", return_value=None):
            import cover_ai
            out = str(tmp_path / "cover.png")
            cover_ai.generate_cover(_niche(), out)
            assert os.path.exists(out)
    finally:
        os.chdir(orig)


def test_always_uses_pil_fallback(tmp_path):
    orig = os.getcwd()
    os.chdir(tmp_path)
    try:
        import cover_ai
        out = str(tmp_path / "cover.png")
        cover_ai.generate_cover(_niche(), out)
        assert os.path.exists(out)
    finally:
        os.chdir(orig)


def test_creates_png_file(tmp_path):
    orig = os.getcwd()
    os.chdir(tmp_path)
    try:
        with patch("cover_ai.config.get_api_key", return_value=None):
            import cover_ai
            out = str(tmp_path / "cover.png")
            cover_ai.generate_cover(_niche(), out)
            assert os.path.exists(out)
            assert os.path.getsize(out) > 100
    finally:
        os.chdir(orig)
