import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import os
from unittest.mock import patch, MagicMock
from ai_client import generate_text


@patch.dict(os.environ, {}, clear=True)
def test_generate_text_no_api_key():
    try:
        generate_text("test prompt")
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "OPENROUTER_API_KEY" in str(e)


@patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test-key"})
@patch("ai_client.requests.post")
def test_generate_text_success(mock_post):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "Generated content here."}}]
    }
    mock_post.return_value = mock_resp

    result = generate_text("test prompt", system_prompt="You are helpful.")
    assert result == "Generated content here."
    mock_post.assert_called_once()


@patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test-key"})
@patch("ai_client.requests.post")
def test_generate_text_without_system(mock_post):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "  trimmed  "}}]
    }
    mock_post.return_value = mock_resp

    result = generate_text("test prompt")
    assert result == "trimmed"
    # should not include system message
    call_kwargs = mock_post.call_args[1]
    messages = call_kwargs["json"]["messages"]
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
