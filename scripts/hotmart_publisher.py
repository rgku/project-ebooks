import os
import base64
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from log import logger


TOKEN_URL = "https://api-oauth.hotmart.com/oauth/token"
PRODUCTS_URL = "https://api-hotmart.com/products/api/v1/products"


def _session() -> requests.Session:
    s = requests.Session()
    retries = Retry(total=2, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s


def _get_access_token(client_id: str, client_secret: str) -> str | None:
    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    r = _session().post(
        TOKEN_URL,
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/json",
        },
        json={"grant_type": "client_credentials"},
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    token = data.get("access_token")
    if not token:
        logger.error(f"[Hotmart] OAuth failed: {data}")
        return None
    logger.info("[Hotmart] Access token obtained")
    return token


def _list_products(token: str) -> list:
    r = _session().get(
        PRODUCTS_URL,
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    r.raise_for_status()
    return r.json().get("items", [])


def publish(niche_title: str) -> str | None:
    client_id = os.getenv("HOTMART_CLIENT_ID")
    client_secret = os.getenv("HOTMART_CLIENT_SECRET")
    if not client_id or not client_secret:
        logger.info("[Hotmart] No HOTMART_CLIENT_ID/SECRET set, skipping")
        return None

    try:
        token = _get_access_token(client_id, client_secret)
        if not token:
            return None

        products = _list_products(token)
        for p in products:
            name = p.get("name", "")
            if name == niche_title:
                checkout_url = p.get("checkoutUrl") or p.get("url") or p.get("checkout_url")
                pid = p.get("id") or p.get("productId")
                logger.info(f"[Hotmart] Found '{niche_title}' (id={pid}, url={checkout_url})")
                if checkout_url:
                    logger.info(f"[Hotmart] Checkout URL: {checkout_url}")
                    return checkout_url
                logger.warning(f"[Hotmart] Product '{niche_title}' has no checkout URL")
                return None

        logger.info(f"[Hotmart] No product found for '{niche_title}'. Create at https://app.hotmart.com/products")
        return None
    except Exception as e:
        logger.error(f"[Hotmart] API request failed: {e}")
        return None
