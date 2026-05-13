import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import os
from unittest.mock import patch, MagicMock
from publisher import publish


@patch.dict(os.environ, {}, clear=True)
def test_publish_skipped_no_config():
    result = publish("en", "/fake/path.pdf", "Test Title", 499, "usd")
    assert result is False


@patch.dict(os.environ, {
    "GUMROAD_TOKEN_EN": "test-token",
    "GUMROAD_PRODUCT_ID_EN": "test-prod",
})
@patch("publisher._session")
def test_publish_success(mock_session_factory, tmp_path):
    pdf = tmp_path / "test.pdf"
    pdf.write_text("fake-pdf-content")

    mock_session = MagicMock()
    mock_session_factory.return_value = mock_session
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"success": True}
    mock_session.put.return_value = mock_resp

    result = publish("en", str(pdf), "Test Title", 499, "usd")
    assert result is True
    mock_session.put.assert_called_once()


@patch.dict(os.environ, {
    "GUMROAD_TOKEN_EN": "test-token",
    "GUMROAD_PRODUCT_ID_EN": "test-prod",
})
@patch("publisher.requests.put")
def test_publish_api_error(mock_put, tmp_path):
    pdf = tmp_path / "test.pdf"
    pdf.write_text("fake-pdf-content")

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"success": False, "error": "bad request"}
    mock_put.return_value = mock_resp

    result = publish("en", str(pdf), "Test Title", 499, "usd")
    assert result is False
