import aiohttp
from elixir.config.constants import ELIXIR_BASE_URL
from elixir.version import __version__


async def post_url(endpoint: str, api_key: str, body: dict):
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "X-Elixir-SDK-Version": __version__,
        }
        async with session.post(
            f"{ELIXIR_BASE_URL}{endpoint}",
            headers=headers,
            json=body,
        ) as response:
            return await response.json()
