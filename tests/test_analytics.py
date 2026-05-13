import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import json
import os
from analytics import track_generated, track_published

ANALYTICS_FILE = "analytics.json"


def test_track_generated_creates_file(tmp_path):
    orig = os.getcwd()
    os.chdir(tmp_path)
    try:
        track_generated("en", "productivity", "Test Title")
        assert os.path.exists(ANALYTICS_FILE)
        with open(ANALYTICS_FILE) as f:
            data = json.load(f)
        assert data["total_generated"] == 1
        assert data["markets"]["en"]["generated"] == 1
        assert len(data["markets"]["en"]["history"]) == 1
    finally:
        os.chdir(orig)


def test_track_published_increments(tmp_path):
    orig = os.getcwd()
    os.chdir(tmp_path)
    try:
        track_published("en", "productivity", "Test Title", 499, "usd")
        with open(ANALYTICS_FILE) as f:
            data = json.load(f)
        assert data["total_published"] == 1
        assert data["markets"]["en"]["published"] == 1
        assert data["markets"]["en"]["history"][0]["event"] == "published"
        assert data["markets"]["en"]["history"][0]["price"] == 499
    finally:
        os.chdir(orig)


def test_accumulates(tmp_path):
    orig = os.getcwd()
    os.chdir(tmp_path)
    try:
        for _ in range(3):
            track_generated("en", "prod", "Title")
        track_published("en", "prod", "Title", 499, "usd")

        with open(ANALYTICS_FILE) as f:
            data = json.load(f)
        assert data["total_generated"] == 3
        assert data["total_published"] == 1
        assert len(data["markets"]["en"]["history"]) == 4  # 3 gen + 1 pub
    finally:
        os.chdir(orig)


def test_multiple_markets(tmp_path):
    orig = os.getcwd()
    os.chdir(tmp_path)
    try:
        track_generated("en", "prod", "EN Title")
        track_generated("pt", "prod", "PT Title")
        with open(ANALYTICS_FILE) as f:
            data = json.load(f)
        assert data["total_generated"] == 2
        assert data["markets"]["en"]["generated"] == 1
        assert data["markets"]["pt"]["generated"] == 1
    finally:
        os.chdir(orig)
