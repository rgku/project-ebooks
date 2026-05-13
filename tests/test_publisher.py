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
})
@patch("publisher._session")
def test_publish_success(mock_session_factory, tmp_path):
    pdf = tmp_path / "test.pdf"
    pdf.write_text("fake-pdf-content")

    mock_session = MagicMock()
    mock_session_factory.return_value = mock_session

    list_resp = MagicMock()
    list_resp.json.return_value = {"success": True, "products": []}
    create_resp = MagicMock()
    create_resp.json.return_value = {"success": True, "product": {"id": "new-prod-id"}}

    presign_resp = MagicMock()
    presign_resp.json.return_value = {
        "success": True,
        "upload_id": "upload123",
        "key": "attachments/key/file.pdf",
        "parts": [{"part_number": 1, "presigned_url": "https://s3.example.com/upload"}],
    }
    part_resp = MagicMock()
    part_resp.headers = {"ETag": '"abc123"'}

    complete_resp = MagicMock()
    complete_resp.json.return_value = {"success": True, "file_url": "https://files.gumroad.com/file.pdf"}

    put_resp = MagicMock()
    put_resp.json.return_value = {"success": True, "product": {"id": "new-prod-id"}}

    mock_session.get.return_value = list_resp
    mock_session.post.side_effect = [create_resp, presign_resp, complete_resp]
    mock_session.put.side_effect = [part_resp, put_resp]

    result = publish("en", str(pdf), "Test Title", 499, "usd")
    assert result is True


@patch.dict(os.environ, {
    "GUMROAD_TOKEN_EN": "test-token",
})
@patch("publisher._session")
def test_publish_api_error(mock_session_factory, tmp_path):
    pdf = tmp_path / "test.pdf"
    pdf.write_text("fake-pdf-content")

    mock_session = MagicMock()
    mock_session_factory.return_value = mock_session

    list_resp = MagicMock()
    list_resp.json.return_value = {"success": True, "products": []}
    create_resp = MagicMock()
    create_resp.json.return_value = {"success": True, "product": {"id": "new-prod-id"}}

    presign_resp = MagicMock()
    presign_resp.json.return_value = {
        "success": True,
        "upload_id": "upload123",
        "key": "attachments/key/file.pdf",
        "parts": [{"part_number": 1, "presigned_url": "https://s3.example.com/upload"}],
    }
    part_resp = MagicMock()
    part_resp.headers = {"ETag": '"abc123"'}

    complete_resp = MagicMock()
    complete_resp.json.return_value = {"success": True, "file_url": "https://files.gumroad.com/file.pdf"}

    put_resp = MagicMock()
    put_resp.json.return_value = {"success": False, "error": "bad request"}

    mock_session.get.return_value = list_resp
    mock_session.post.side_effect = [create_resp, presign_resp, complete_resp]
    mock_session.put.side_effect = [part_resp, put_resp]

    result = publish("en", str(pdf), "Test Title", 499, "usd")
    assert result is False


@patch.dict(os.environ, {
    "GUMROAD_TOKEN_EN": "test-token",
})
@patch("publisher._session")
def test_publish_existing_product(mock_session_factory, tmp_path):
    pdf = tmp_path / "test.pdf"
    pdf.write_text("fake-pdf-content")

    mock_session = MagicMock()
    mock_session_factory.return_value = mock_session

    list_resp = MagicMock()
    list_resp.json.return_value = {
        "success": True,
        "products": [{"id": "existing-id", "name": "Test Title"}],
    }

    presign_resp = MagicMock()
    presign_resp.json.return_value = {
        "success": True,
        "upload_id": "upload123",
        "key": "attachments/key/file.pdf",
        "parts": [{"part_number": 1, "presigned_url": "https://s3.example.com/upload"}],
    }
    part_resp = MagicMock()
    part_resp.headers = {"ETag": '"abc123"'}

    complete_resp = MagicMock()
    complete_resp.json.return_value = {"success": True, "file_url": "https://files.gumroad.com/file.pdf"}

    put_resp = MagicMock()
    put_resp.json.return_value = {"success": True, "product": {"id": "existing-id"}}

    mock_session.get.return_value = list_resp
    mock_session.post.side_effect = [presign_resp, complete_resp]
    mock_session.put.side_effect = [part_resp, put_resp]

    result = publish("en", str(pdf), "Test Title", 499, "usd")
    assert result is True
