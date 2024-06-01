import urllib.parse
import os
import time
import urllib
import requests

from dotenv import load_dotenv
from typing import NamedTuple

load_dotenv()


daily_api_path = os.getenv("DAILY_API_URL") or "api.daily.co/v1"
daily_api_key = os.getenv("DAILY_API_KEY")


class RoomInfo(NamedTuple):
    id: str
    url: str
    name: str
    sip_uri: str


def create_room() -> RoomInfo:
    """
    Helper function to create a Daily room.
    # See: https://docs.daily.co/reference/rest-api/rooms

    Returns:
        RoomInfo: An instance of RoomInfo class containing the room URL, room name, and room SIP URI.

    Raises:
        Exception: If the request to create the room fails or if the response does not contain the room URL or room name.
    """
    room_props = {
        "exp": time.time() + 60 * 60,  # 1 hour
        "enable_chat": True,
        "enable_emoji_reactions": True,
        "eject_at_room_exp": True,
        "enable_prejoin_ui": False,  # Important for the bot to be able to join headlessly
        "sip": {
            "sip_mode": "dial-in",
            "display_name": "SIP Participant",
        },
    }
    res = requests.post(
        f"https://{daily_api_path}/rooms",
        headers={"Authorization": f"Bearer {daily_api_key}"},
        json={"properties": room_props},
    )
    if res.status_code != 200:
        raise Exception(f"Unable to create room: {res.text}")

    data = res.json()
    room_id: str = data.get("id")
    room_url: str = data.get("url")
    room_name: str = data.get("name")
    room_sip_uri: str = data.get("config").get("sip_uri").get("endpoint")

    if room_id is None or room_url is None or room_name is None or room_sip_uri is None:
        raise Exception("Missing room properties in response")

    return RoomInfo(id=room_id, url=room_url, name=room_name, sip_uri=room_sip_uri)


def get_name_from_url(room_url: str) -> str:
    """
    Extracts the name from a given room URL.

    Args:
        room_url (str): The URL of the room.

    Returns:
        str: The extracted name from the room URL.
    """
    return urllib.parse.urlparse(room_url).path[1:]


def get_token(room_url: str) -> str:
    """
    Retrieves a meeting token for the specified Daily room URL.
    # See: https://docs.daily.co/reference/rest-api/meeting-tokens

    Args:
        room_url (str): The URL of the Daily room.

    Returns:
        str: The meeting token.

    Raises:
        Exception: If no room URL is specified or if no Daily API key is specified.
        Exception: If there is an error creating the meeting token.
    """
    if not room_url:
        raise Exception(
            "No Daily room specified. You must specify a Daily room in order a token to be generated."
        )

    if not daily_api_key:
        raise Exception(
            "No Daily API key specified. set DAILY_API_KEY in your environment to specify a Daily API key, available from https://dashboard.daily.co/developers."
        )

    expiration: float = time.time() + 60 * 60
    room_name = get_name_from_url(room_url)

    res: requests.Response = requests.post(
        f"https://{daily_api_path}/meeting-tokens",
        headers={"Authorization": f"Bearer {daily_api_key}"},
        json={
            "properties": {
                "room_name": room_name,
                "is_owner": True,  # Owner tokens required for transcription
                "exp": expiration,
            }
        },
    )

    if res.status_code != 200:
        raise Exception(f"Failed to create meeting token: {res.status_code} {res.text}")

    token: str = res.json()["token"]

    return token


def check_room_participants(room_name, max_time_limit=30):
    start_time = time.time()  # Start time

    while True:
        response = requests.get(
            f"https://{daily_api_path}/rooms/{room_name}/presence",
            headers={"Authorization": f"Bearer {daily_api_key}"},
        )
        if response.status_code == 200:
            participants_info = response.json()
            if (
                len(participants_info["data"]) > 0
            ):  # Check if there are any participants
                break
        time.sleep(1)  # Wait for 1 second before checking again

        elapsed_time = time.time() - start_time  # Calculate elapsed time
        if elapsed_time >= max_time_limit:
            break
