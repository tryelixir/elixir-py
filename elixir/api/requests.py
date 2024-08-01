from typing import Optional
import aiohttp
from elixir.config.constants import get_base_url
from elixir.version import __version__


async def post_body_request(endpoint: str, api_key: str, body: Optional[dict] = None):
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "X-Elixir-SDK-Version": __version__,
        }
        async with session.post(
            f"{get_base_url()}{endpoint}",
            headers=headers,
            json=body,
        ) as response:
            return await response.json()


async def post_file_request(
    endpoint: str,
    api_key: str,
    body: Optional[dict] = None,
    file_content: Optional[bytes] = None,
    content_type: Optional[str] = None,
):
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "X-Elixir-SDK-Version": __version__,
        }

        data = aiohttp.FormData()

        if body:
            for key, value in body.items():
                data.add_field(key, value)

        if file_content and content_type:
            data.add_field("file", file_content, content_type=content_type)

        async with session.post(
            f"{get_base_url()}{endpoint}",
            headers=headers,
            data=data,
        ) as response:
            return await response.json()
