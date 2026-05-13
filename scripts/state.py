import sqlite3
import os
from datetime import datetime

DB_FILE = "state.db"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS niches (
            market TEXT NOT NULL,
            niche_id TEXT NOT NULL,
            last_generated TEXT,
            generated_count INTEGER DEFAULT 0,
            PRIMARY KEY (market, niche_id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    return conn


def read_state() -> dict:
    conn = _get_conn()
    result = {"last_generated": None}
    row = conn.execute("SELECT value FROM meta WHERE key='last_run'").fetchone()
    if row:
        result["last_generated"] = row["value"]
    conn.close()
    return result


def save_state(state: dict):
    conn = _get_conn()
    if state.get("last_generated"):
        conn.execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
            ("last_run", state["last_generated"]),
        )
    conn.commit()
    conn.close()


def check_48h_elapsed(state: dict) -> bool:
    last = state.get("last_generated")
    if not last:
        return True
    elapsed = datetime.now() - datetime.fromisoformat(last)
    return elapsed.total_seconds() >= 48 * 3600


def pick_next_niche(market: str, available_ids: list[str]) -> str:
    conn = _get_conn()
    for nid in available_ids:
        conn.execute(
            "INSERT OR IGNORE INTO niches (market, niche_id, generated_count) VALUES (?, ?, 0)",
            (market, nid),
        )
    conn.commit()

    row = conn.execute(
        """
        SELECT niche_id FROM niches
        WHERE market = ?
        ORDER BY last_generated ASC NULLS FIRST
        LIMIT 1
    """,
        (market,),
    ).fetchone()
    conn.close()
    return row["niche_id"] if row else available_ids[0]


def mark_generated(market: str, niche_id: str):
    conn = _get_conn()
    conn.execute(
        """
        INSERT INTO niches (market, niche_id, last_generated, generated_count)
        VALUES (?, ?, ?, 1)
        ON CONFLICT(market, niche_id) DO UPDATE SET
            last_generated = excluded.last_generated,
            generated_count = generated_count + 1
    """,
        (market, niche_id, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()
