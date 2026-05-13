import os
import json
import requests
from log import logger

WEBHOOK_URL_VAR = "NOTIFICATION_WEBHOOK_URL"

def send_notification(title: str, message: str, success: bool) -> bool:
    url = os.getenv(WEBHOOK_URL_VAR)
    if not url:
        return False

    emoji = "✅" if success else "❌"
    fallback_slack(url, title, f"{emoji} {message}")
    return True


def fallback_slack(webhook_url: str, title: str, text: str):
    try:
        requests.post(
            webhook_url,
            json={"text": f"*{title}*\n{text}"},
            timeout=10,
        )
    except Exception as e:
        logger.warning(f"Notification failed: {e}")
