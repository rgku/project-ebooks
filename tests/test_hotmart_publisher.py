import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import os
from unittest.mock import patch, MagicMock
import hotmart_publisher


def _make_product(name: str, url: str = "https://hotmart.com/product/abc") -> dict:
    return {
        "id": "123456",
        "productId": 123456,
        "name": name,
        "checkoutUrl": url,
    }


@patch.dict(os.environ, {}, clear=True)
def test_publish_no_credentials():
    result = hotmart_publisher.publish("Test Title")
    assert result is None


@patch.dict(os.environ, {"HOTMART_CLIENT_ID": "cid", "HOTMART_CLIENT_SECRET": "csec"}, clear=True)
@patch("hotmart_publisher._session")
def test_publish_found(mock_session_factory):
    mock_session = MagicMock()
    mock_session_factory.return_value = mock_session

    # OAuth token response
    token_resp = MagicMock()
    token_resp.json.return_value = {"access_token": "tok_xxx"}
    token_resp.status_code = 200

    # Products list response
    prod_resp = MagicMock()
    prod_resp.json.return_value = {
        "items": [_make_product("Test Title"), _make_product("Other Book")]
    }
    prod_resp.status_code = 200

    mock_session.post.return_value = token_resp
    mock_session.get.return_value = prod_resp

    result = hotmart_publisher.publish("Test Title")
    assert result == "https://hotmart.com/product/abc"


@patch.dict(os.environ, {"HOTMART_CLIENT_ID": "cid", "HOTMART_CLIENT_SECRET": "csec"}, clear=True)
@patch("hotmart_publisher._session")
def test_publish_not_found(mock_session_factory):
    mock_session = MagicMock()
    mock_session_factory.return_value = mock_session

    token_resp = MagicMock()
    token_resp.json.return_value = {"access_token": "tok_xxx"}
    mock_session.post.return_value = token_resp

    prod_resp = MagicMock()
    prod_resp.json.return_value = {
        "items": [_make_product("Other Book"), _make_product("Another Book")]
    }
    mock_session.get.return_value = prod_resp

    result = hotmart_publisher.publish("Missing Title")
    assert result is None


@patch.dict(os.environ, {"HOTMART_CLIENT_ID": "cid", "HOTMART_CLIENT_SECRET": "csec"}, clear=True)
@patch("hotmart_publisher._session")
def test_publish_no_checkout_url(mock_session_factory):
    mock_session = MagicMock()
    mock_session_factory.return_value = mock_session

    token_resp = MagicMock()
    token_resp.json.return_value = {"access_token": "tok_xxx"}
    mock_session.post.return_value = token_resp

    prod = _make_product("Draft Product")
    prod["checkoutUrl"] = None
    prod_resp = MagicMock()
    prod_resp.json.return_value = {"items": [prod]}
    mock_session.get.return_value = prod_resp

    result = hotmart_publisher.publish("Draft Product")
    assert result is None


@patch.dict(os.environ, {"HOTMART_CLIENT_ID": "cid", "HOTMART_CLIENT_SECRET": "csec"}, clear=True)
@patch("hotmart_publisher._session")
def test_publish_api_error(mock_session_factory):
    mock_session = MagicMock()
    mock_session_factory.return_value = mock_session
    mock_session.post.side_effect = Exception("OAuth timeout")

    result = hotmart_publisher.publish("Test")
    assert result is None
