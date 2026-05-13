import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import os
from unittest.mock import patch
from notifier import send_notification


@patch.dict(os.environ, {}, clear=True)
def test_send_notification_no_webhook():
    result = send_notification("Test", "Message", True)
    assert result is False


@patch.dict(os.environ, {"NOTIFICATION_WEBHOOK_URL": "https://hooks.slack.com/test"})
@patch("notifier.requests.post")
def test_send_notification_success(mock_post):
    mock_post.return_value.status_code = 200
    result = send_notification("Test Title", "Test Message", True)
    assert result is True
    mock_post.assert_called_once()


@patch.dict(os.environ, {"NOTIFICATION_WEBHOOK_URL": "https://hooks.slack.com/test"})
@patch("notifier.requests.post")
def test_send_notification_failure_ignored(mock_post):
    mock_post.side_effect = Exception("network error")
    result = send_notification("Test Title", "Test Message", False)
    assert result is True
