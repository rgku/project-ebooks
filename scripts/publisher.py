import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from log import logger

MAX_RETRIES = 3
GUMROAD_BASE = "https://api.gumroad.com/v2"
SPAM_INDICATORS = ["moderation", "spam", "not comply", "banned", "inappropriate", "blocked", "content_policy"]


def _session() -> requests.Session:
    s = requests.Session()
    retries = Retry(
        total=MAX_RETRIES,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["PUT", "POST"],
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.mount("http://", HTTPAdapter(max_retries=retries))
    return s


def _find_product_by_id(token: str, pid: str) -> str | None:
    r = _session().get(
        f"{GUMROAD_BASE}/products/{pid}",
        params={"access_token": token},
        timeout=15,
    )
    if r.json().get("success"):
        logger.info(f"Found product by ID: {pid}")
        return pid
    return None


def _find_or_create_product(token: str, title: str, price: int, currency: str, override_id: str | None = None) -> str | None:
    if override_id:
        pid = _find_product_by_id(token, override_id)
        if pid:
            return pid
        logger.warning(f"Override product ID {override_id} not found, will search by name")

    r = _session().get(
        f"{GUMROAD_BASE}/products",
        params={"access_token": token},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    for p in data.get("products", []):
        if p["name"] == title:
            logger.info(f"Found existing product: {title} (id={p['id']})")
            return p["id"]

    create_r = _session().post(
        f"{GUMROAD_BASE}/products",
        data={
            "access_token": token,
            "name": title,
            "price": price,
            "currency": currency,
        },
        timeout=30,
    )
    create_r.raise_for_status()
    result = create_r.json()
    if result.get("success"):
        pid = result["product"]["id"]
        logger.info(f"Created product: {title} (id={pid})")
        return pid
    logger.error(f"Failed to create product: {result}")
    return None


def _upload_file(token: str, file_path: str) -> str | None:
    file_size = os.path.getsize(file_path)
    filename = os.path.basename(file_path)

    presign_resp = _session().post(
        f"{GUMROAD_BASE}/files/presign",
        headers={"Authorization": f"Bearer {token}"},
        data={"filename": filename, "file_size": str(file_size)},
        timeout=30,
    )
    presign_resp.raise_for_status()
    presign_data = presign_resp.json()
    if not presign_data.get("success"):
        logger.error(f"Presign failed: {presign_data}")
        return None

    upload_id = presign_data["upload_id"]
    key = presign_data["key"]
    parts = presign_data["parts"]

    uploaded_parts = []
    with open(file_path, "rb") as fh:
        for part in parts:
            part_num = part["part_number"]
            presigned_url = part["presigned_url"]
            part_resp = _session().put(presigned_url, data=fh, timeout=120)
            part_resp.raise_for_status()
            etag = part_resp.headers.get("ETag", "")
            uploaded_parts.append({"part_number": part_num, "etag": etag})

    complete_resp = _session().post(
        f"{GUMROAD_BASE}/files/complete",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"upload_id": upload_id, "key": key, "parts": uploaded_parts},
        timeout=30,
    )
    complete_resp.raise_for_status()
    complete_data = complete_resp.json()
    if not complete_data.get("success"):
        logger.error(f"File complete failed: {complete_data}")
        return None

    return complete_data["file_url"]


def _is_spam_error(result: dict) -> bool:
    msg = str(result.get("message", "")).lower()
    for indicator in SPAM_INDICATORS:
        if indicator in msg:
            return True
    for field in result.get("errors", []):
        if isinstance(field, str) and any(ind in field.lower() for ind in SPAM_INDICATORS):
            return True
    return False


def publish(market_name: str, pdf_path: str, title: str, price: int, currency: str, description: str = "", niche_title: str = "") -> bool:
    token_var = f"GUMROAD_TOKEN_{market_name.upper()}"

    token = os.getenv(token_var)

    if not token:
        logger.warning(f"[{market_name}] Gumroad not configured ({token_var}). Skip.")
        return False

    try:
        product_id = _find_or_create_product(token, title, price, currency, override_id=os.getenv(f"GUMROAD_PRODUCT_ID_{market_name.upper()}"))
        if not product_id:
            return False

        file_url = _upload_file(token, pdf_path)
        if not file_url:
            logger.error(f"[{market_name}] File upload failed")
            return False

        safe_desc = description or title
        receipt_name = niche_title or title

        payload = {
            "name": title,
            "price": price,
            "currency": currency,
            "description": safe_desc,
            "custom_receipt": (
                f"<p>Thank you for purchasing <strong>{receipt_name}</strong>!</p>"
                f"<p>We hope you enjoy this ebook and find it valuable.</p>"
            ),
            "files[][url]": file_url,
        }

        r = _session().put(
            f"{GUMROAD_BASE}/products/{product_id}",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )

        r.raise_for_status()
        result = r.json()

        if result.get("success"):
            logger.info(f"[{market_name}] Published: {title} ({price/100:.2f} {currency.upper()})")
            return True

        if _is_spam_error(result):
            logger.warning(f"[{market_name}] Moderation flag for '{title}': {result.get('message', '')} | full: {result}")
            clean_payload = {
                "name": title,
                "price": price,
                "currency": currency,
                "description": title,
                "custom_receipt": (
                    f"<p>Thank you for purchasing <strong>{receipt_name}</strong>!</p>"
                    f"<p>We hope you enjoy this ebook and find it valuable.</p>"
                ),
                "files[][url]": file_url,
            }
            try:
                r2 = _session().put(
                    f"{GUMROAD_BASE}/products/{product_id}",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    json=clean_payload,
                    timeout=60,
                )
                r2.raise_for_status()
                result2 = r2.json()
                if result2.get("success"):
                    logger.info(f"[{market_name}] Published with clean description: {title}")
                    return True
                logger.error(f"[{market_name}] Clean description also failed: {result2}")
            except requests.RequestException as e2:
                logger.error(f"[{market_name}] Clean description retry failed: {e2}")
        else:
            logger.error(f"[{market_name}] Gumroad API error: {result}")

        return False
    except requests.RequestException as e:
        logger.error(f"[{market_name}] Request failed after {MAX_RETRIES} retries: {e}")
        return False
