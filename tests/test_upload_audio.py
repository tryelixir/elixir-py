import pytest
from unittest.mock import patch

from elixir import Elixir


@pytest.mark.asyncio
@patch("elixir.post_file_request")
async def test_upload_file(mock_post_file_request, exporter):
    mock_post_file_request.return_value = {"message": "Success"}

    result = await Elixir.upload_audio(
        conversation_id="test", audio_buffer=b"test", audio_content_type="audio/wav"
    )

    mock_post_file_request.assert_called_once_with(
        endpoint="/ingestion/audio-file",
        api_key="elixir_api_key",
        body={"conversation_id": "test"},
        file_content=b"test",
        content_type="audio/wav",
    )
    assert result == {"message": "Success"}


@pytest.mark.asyncio
@patch("elixir.post_body_request")
async def test_upload_url(mock_post_body_request, exporter):
    mock_post_body_request.return_value = {"message": "Success"}

    result = await Elixir.upload_audio(
        conversation_id="test", audio_url="http://test.com"
    )

    mock_post_body_request.assert_called_once_with(
        endpoint="/ingestion/audio-url",
        api_key="elixir_api_key",
        body={"audio_url": "http://test.com", "conversation_id": "test"},
    )
    assert result == {"message": "Success"}
