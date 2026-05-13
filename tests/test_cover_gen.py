import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from cover_gen import _hex_to_rgb


def test_hex_to_rgb():
    assert _hex_to_rgb("#FF0000") == (255, 0, 0)
    assert _hex_to_rgb("#00FF00") == (0, 255, 0)
    assert _hex_to_rgb("#0000FF") == (0, 0, 255)
    assert _hex_to_rgb("#FFFFFF") == (255, 255, 255)
    assert _hex_to_rgb("#000000") == (0, 0, 0)


def test_hex_to_rgb_without_hash():
    assert _hex_to_rgb("FF0000") == (255, 0, 0)


def test_hex_to_rgb_eight_char():
    assert _hex_to_rgb("#FF000080") == (255, 0, 0)
