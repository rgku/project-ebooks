import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from config import NICHES_EN, NICHES_PT, MARKETS


def test_en_niches_count():
    assert len(NICHES_EN) == 12


def test_pt_niches_count():
    assert len(NICHES_PT) == 12


def test_all_niches_have_ids():
    for n in NICHES_EN + NICHES_PT:
        assert n.id, f"Missing id in {n.title}"
        assert n.lang in ("en", "pt")


def test_markets_structure():
    assert len(MARKETS) == 2
    for m in MARKETS:
        assert "name" in m
        assert "niches" in m
        assert "price" in m
        assert "currency" in m
        assert len(m["niches"]) == 12


def test_market_names():
    names = [m["name"] for m in MARKETS]
    assert "en" in names
    assert "pt" in names


def test_niche_unique_ids():
    ids = [n.id for n in NICHES_EN + NICHES_PT]
    assert len(ids) == len(set(ids)), "Duplicate niche IDs found"


def test_en_ids_differ_from_pt():
    en_ids = {n.id for n in NICHES_EN}
    pt_ids = {n.id for n in NICHES_PT}
    assert en_ids.isdisjoint(pt_ids), "EN and PT niches share IDs"
