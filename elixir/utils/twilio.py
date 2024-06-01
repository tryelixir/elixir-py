from io import BytesIO
import os
import re
from typing import Optional
import aiohttp

from elixir.api.s3 import upload_stream_to_s3


def _get_account_sid(recording_url: str) -> str | None:
    pattern = r"https://api\.twilio\.com/2010-04-01/Accounts/(AC[a-zA-Z0-9]+)/Recordings/RE[a-zA-Z0-9]+"
    match = re.search(pattern, recording_url)
    if not match:
        return None
    return match.group(1)


async def _get_content_length(url: str, account_sid: str, auth_token: str) -> int:
    """
    Retrieves the content length of a given URL using Twilio authentication.

    Args:
        url (str): The URL to retrieve the content length from.
        account_sid (str): The Twilio account SID for authentication.
        auth_token (str): The Twilio authentication token.

    Returns:
        int: The total content length in bytes.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url,
            auth=aiohttp.BasicAuth(account_sid, auth_token),
        ) as response:
            total_bytes = 0
            async for chunk in response.content.iter_chunked(1024):
                total_bytes += len(chunk)
            return total_bytes


async def upload_twilio_recording(
    session_id: str,
    recording_url: str,
    auth_token: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN"),
):
    """
    Uploads a Twilio recording to a specified presigned URL.

    Args:
        auth_token (str): The authentication token for the Twilio account.
        recording_url (str): The URL of the Twilio recording.
        presigned_url (str): The presigned URL where the recording will be uploaded.

    Raises:
        Exception: If the Twilio recording URL is invalid.

    """
    account_sid = _get_account_sid(recording_url)
    if not account_sid:
        raise Exception(f"Invalid Twilio recording URL: {recording_url}")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{recording_url}.mp3?RequestedChannels=2",
            auth=aiohttp.BasicAuth(account_sid, auth_token),
        ) as response:
            # TODO: Figure out if we can use `response.content` directly, though this stream doesn't seem to
            # provide the entire file contents.
            content = await response.read()
            file_stream = BytesIO(content)

            await upload_stream_to_s3(session_id, file_stream)
