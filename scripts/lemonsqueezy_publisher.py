import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from log import logger


BASE_URL = "https://api.lemonsqueezy.com/v1"


def _session() -> requests.Session:
    s = requests.Session()
    retries = Retry(total=2, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s


def _headers(api_key: str) -> dict:
    return {"Authorization": f"Bearer {api_key}", "Accept": "application/vnd.api+json"}


def _list_products(api_key: str) -> list:
    r = _session().get(f"{BASE_URL}/products", headers=_headers(api_key), timeout=15)
    r.raise_for_status()
    return r.json().get("data", [])


def publish(niche_title: str) -> str | None:
    api_key = os.getenv("LEMONSQUEEZY_API_KEY")
    if not api_key:
        logger.info("[LS] No LEMONSQUEEZY_API_KEY set, skipping")
        return None

    try:
        products = _list_products(api_key)
        for p in products:
            attrs = p.get("attributes", {})
            if attrs.get("name") == niche_title:
                url = attrs.get("buy_now_url")
                pid = p.get("id")
                status = attrs.get("status", "draft")
                logger.info(f"[LS] Found '{niche_title}' (id={pid}, status={status}, url={url})")
                if url:
                    logger.info(f"[LS] Checkout URL: {url}")
                    return url
                logger.warning(f"[LS] Product '{niche_title}' has no buy_now_url")
                return None

        logger.info(f"[LS] No product found for '{niche_title}'. Create at https://app.lemonsqueezy.com/products")
        return None
    except Exception as e:
        logger.error(f"[LS] API request failed: {e}")
        return None
