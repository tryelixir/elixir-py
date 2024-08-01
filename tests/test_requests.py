from aiohttp import FormData
from aioresponses import aioresponses
import pytest
from yarl import URL
from elixir.api import requests
from elixir.config.constants import get_base_url

base_url = get_base_url()


@pytest.mark.asyncio
async def test_post_body_json_request():
    endpoint = "/endpoint"
    api_key = "your_api_key"
    body = {"key": "value"}

    with aioresponses() as m:
        m.post(
            f"{base_url}{endpoint}",
            status=200,
            payload={"message": "Success"},
        )

        response = await requests.post_body_request(endpoint, api_key, body)
        request = m.requests.get(("POST", URL(f"{base_url}{endpoint}")))[0]

        assert request.kwargs["json"] == body
        assert request.kwargs["headers"]["Authorization"] == f"Bearer {api_key}"
        assert response == {"message": "Success"}


@pytest.mark.asyncio
async def test_post_file_request():
    endpoint = "/endpoint"
    api_key = "your_api_key"
    body = {"key": "value"}
    file_content = b"file content"
    content_type = "application/octet-stream"

    with aioresponses() as m:
        m.post(
            f"{base_url}{endpoint}",
            status=200,
            payload={"message": "Success"},
        )

        response = await requests.post_file_request(
            endpoint, api_key, body, file_content, content_type
        )
        request = m.requests.get(("POST", URL(f"{base_url}{endpoint}")))[0]

        request_form: FormData = request.kwargs["data"]

        assert request_form._fields[0][0].get("name") == "key"
        assert request_form._fields[0][2] == "value"

        assert request_form._fields[1][0].get("name") == "file"
        assert request_form._fields[1][0].get("filename") == "file"
        assert request_form._fields[1][1].get("Content-Type") == content_type
        assert request_form._fields[1][2] == file_content

        assert request.kwargs["headers"]["Authorization"] == f"Bearer {api_key}"
        assert response == {"message": "Success"}
