import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import os
from unittest.mock import patch, MagicMock
import lemonsqueezy_publisher


def _make_product(name: str, status: str = "draft") -> dict:
    return {
        "type": "products",
        "id": "999999",
        "attributes": {
            "name": name,
            "slug": name.lower().replace(" ", "-"),
            "status": status,
            "buy_now_url": f"https://various-ebooks.lemonsqueezy.com/checkout/buy/{name.lower().replace(' ', '-')}",
            "price": 399,
            "price_formatted": "€3.99",
        },
    }


@patch.dict(os.environ, {}, clear=True)
def test_publish_no_api_key():
    result = lemonsqueezy_publisher.publish("Test Title")
    assert result is None


@patch.dict(os.environ, {"LEMONSQUEEZY_API_KEY": "test-key"}, clear=True)
@patch("lemonsqueezy_publisher._session")
def test_publish_found(mock_session_factory):
    mock_session = MagicMock()
    mock_session_factory.return_value = mock_session

    resp = MagicMock()
    resp.json.return_value = {
        "data": [_make_product("Test Title"), _make_product("Other Book")]
    }
    mock_session.get.return_value = resp

    result = lemonsqueezy_publisher.publish("Test Title")
    assert result == "https://various-ebooks.lemonsqueezy.com/checkout/buy/test-title"


@patch.dict(os.environ, {"LEMONSQUEEZY_API_KEY": "test-key"}, clear=True)
@patch("lemonsqueezy_publisher._session")
def test_publish_not_found(mock_session_factory):
    mock_session = MagicMock()
    mock_session_factory.return_value = mock_session

    resp = MagicMock()
    resp.json.return_value = {
        "data": [_make_product("Other Book"), _make_product("Another Book")]
    }
    mock_session.get.return_value = resp

    result = lemonsqueezy_publisher.publish("Missing Title")
    assert result is None


@patch.dict(os.environ, {"LEMONSQUEEZY_API_KEY": "test-key"}, clear=True)
@patch("lemonsqueezy_publisher._session")
def test_publish_no_buy_url(mock_session_factory):
    mock_session = MagicMock()
    mock_session_factory.return_value = mock_session

    prod = _make_product("Draft Product")
    prod["attributes"]["buy_now_url"] = None
    resp = MagicMock()
    resp.json.return_value = {"data": [prod]}
    mock_session.get.return_value = resp

    result = lemonsqueezy_publisher.publish("Draft Product")
    assert result is None


@patch.dict(os.environ, {"LEMONSQUEEZY_API_KEY": "test-key"}, clear=True)
@patch("lemonsqueezy_publisher._session")
def test_publish_api_error(mock_session_factory):
    mock_session = MagicMock()
    mock_session_factory.return_value = mock_session
    mock_session.get.side_effect = Exception("API timeout")

    result = lemonsqueezy_publisher.publish("Test")
    assert result is None


@patch.dict(os.environ, {"LEMONSQUEEZY_API_KEY": "test-key"}, clear=True)
@patch("lemonsqueezy_publisher._session")
def test_publish_published_status_ok(mock_session_factory):
    mock_session = MagicMock()
    mock_session_factory.return_value = mock_session

    resp = MagicMock()
    resp.json.return_value = {
        "data": [_make_product("Published Book", status="published")]
    }
    mock_session.get.return_value = resp

    result = lemonsqueezy_publisher.publish("Published Book")
    assert result == "https://various-ebooks.lemonsqueezy.com/checkout/buy/published-book"
