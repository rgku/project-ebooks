import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from config import Niche
from cover_gen import _hex_to_rgb, generate_cover


def test_hex_to_rgb_values():
    assert _hex_to_rgb("#1E3A5F") == (30, 58, 95)
    assert _hex_to_rgb("#2563EB") == (37, 99, 235)
    assert _hex_to_rgb("#4C1D95") == (76, 29, 149)


def test_generate_cover_creates_file(tmp_path):
    output = tmp_path / "cover.png"
    niche = Niche(
        id="test",
        title="Test Title for Cover",
        subtitle="Test Subtitle",
        lang="en",
        cover_keywords="test minimal modern",
        content_brief="test",
        color1="#1E3A5F",
        color2="#2563EB",
    )
    generate_cover(niche, str(output))
    assert output.exists()
    assert output.stat().st_size > 1000  # PNG with actual content
