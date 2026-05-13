import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import os
from datetime import datetime, timedelta
import state


def test_read_state_defaults(tmp_path):
    orig = os.getcwd()
    os.chdir(tmp_path)
    try:
        st = state.read_state()
        assert st["last_generated"] is None
    finally:
        os.chdir(orig)


def test_save_and_read_state(tmp_path):
    orig = os.getcwd()
    os.chdir(tmp_path)
    try:
        state.save_state({"last_generated": "2026-01-01T00:00:00"})
        assert state.read_state()["last_generated"] == "2026-01-01T00:00:00"
    finally:
        os.chdir(orig)


def test_check_48h_no_last():
    assert state.check_48h_elapsed({"last_generated": None}) is True


def test_check_48h_elapsed_true():
    old = (datetime.now() - timedelta(hours=72)).isoformat()
    assert state.check_48h_elapsed({"last_generated": old}) is True


def test_check_48h_elapsed_false():
    recent = (datetime.now() - timedelta(hours=12)).isoformat()
    assert state.check_48h_elapsed({"last_generated": recent}) is False


def test_check_48h_boundary():
    exact = (datetime.now() - timedelta(hours=48)).isoformat()
    assert state.check_48h_elapsed({"last_generated": exact}) is True


def test_pick_next_niche_returns_unused_first(tmp_path):
    orig = os.getcwd()
    os.chdir(tmp_path)
    try:
        chosen = state.pick_next_niche("en", ["a", "b", "c"])
        assert chosen in ("a", "b", "c")
    finally:
        os.chdir(orig)


def test_pick_next_niche_cycles(tmp_path):
    orig = os.getcwd()
    os.chdir(tmp_path)
    try:
        state.mark_generated("en", "a")
        state.mark_generated("en", "b")
        chosen = state.pick_next_niche("en", ["a", "b", "c"])
        assert chosen == "c"
    finally:
        os.chdir(orig)


def test_pick_next_niche_returns_oldest(tmp_path):
    orig = os.getcwd()
    os.chdir(tmp_path)
    try:
        state.mark_generated("en", "a")
        first = state.pick_next_niche("en", ["a", "b"])
        assert first == "b"
        state.mark_generated("en", "b")
        # Both generated; should return oldest (a)
        second = state.pick_next_niche("en", ["a", "b"])
        assert second == "a"
    finally:
        os.chdir(orig)


def test_mark_generated_increments_count(tmp_path):
    orig = os.getcwd()
    os.chdir(tmp_path)
    try:
        state.pick_next_niche("en", ["x"])
        state.mark_generated("en", "x")
        state.mark_generated("en", "x")
        import sqlite3
        conn = sqlite3.connect("state.db")
        row = conn.execute("SELECT generated_count FROM niches WHERE market='en' AND niche_id='x'").fetchone()
        conn.close()
        assert row[0] == 2
    finally:
        os.chdir(orig)
