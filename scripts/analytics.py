import json
import os
from datetime import datetime

ANALYTICS_FILE = "analytics.json"

def _read() -> dict:
    if not os.path.exists(ANALYTICS_FILE):
        return {"total_generated": 0, "total_published": 0, "markets": {}}
    with open(ANALYTICS_FILE, encoding="utf-8") as f:
        return json.load(f)

def _save(data: dict):
    with open(ANALYTICS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def track_generated(market: str, niche_id: str, title: str):
    data = _read()
    data["total_generated"] += 1
    m = data["markets"].setdefault(market, {"generated": 0, "published": 0, "history": []})
    m["generated"] += 1
    m["history"].append({
        "time": datetime.now().isoformat(),
        "niche": niche_id,
        "title": title,
        "event": "generated",
    })
    _save(data)

def track_published(market: str, niche_id: str, title: str, price: int, currency: str):
    data = _read()
    data["total_published"] += 1
    m = data["markets"].setdefault(market, {"generated": 0, "published": 0, "history": []})
    m["published"] += 1
    m["history"].append({
        "time": datetime.now().isoformat(),
        "niche": niche_id,
        "title": title,
        "price": price,
        "currency": currency,
        "event": "published",
    })
    _save(data)
