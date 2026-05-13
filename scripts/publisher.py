import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from log import logger

MAX_RETRIES = 3


def _session() -> requests.Session:
    s = requests.Session()
    retries = Retry(
        total=MAX_RETRIES,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["PUT"],
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.mount("http://", HTTPAdapter(max_retries=retries))
    return s


def publish(market_name: str, pdf_path: str, title: str, price: int, currency: str) -> bool:
    token_var = f"GUMROAD_TOKEN_{market_name.upper()}"
    pid_var = f"GUMROAD_PRODUCT_ID_{market_name.upper()}"

    token = os.getenv(token_var)
    product_id = os.getenv(pid_var)

    if not token or not product_id:
        logger.warning(f"[{market_name}] Gumroad not configured ({token_var}, {pid_var}). Skip.")
        return False

    url = f"https://api.gumroad.com/v2/products/{product_id}"

    try:
        with open(pdf_path, "rb") as fh:
            r = _session().put(
                url,
            data={
                "access_token": token,
                "name": title,
                "price": price,
                "currency": currency,
                "description": f"Automatic generation: {title}",
                "custom_receipt": f"<p>Thank you for purchasing <strong>{title}</strong>!</p><p>This ebook was generated automatically. Enjoy your reading.</p>",
            },
                files={"file": ("ebook.pdf", fh, "application/pdf")},
                timeout=120,
            )

        r.raise_for_status()
        result = r.json()

        if result.get("success"):
            logger.info(f"[{market_name}] Published: {title} ({price/100:.2f} {currency.upper()})")
            return True

        logger.error(f"[{market_name}] Gumroad API error: {result}")
        return False
    except requests.RequestException as e:
        logger.error(f"[{market_name}] Request failed after {MAX_RETRIES} retries: {e}")
        return False
