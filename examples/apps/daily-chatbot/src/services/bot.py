import os
import subprocess
from fastapi import HTTPException
from pathlib import Path

from utils.daily import create_room, get_token

MAX_BOTS_PER_ROOM = 1

# Bot sub-process dict for status reporting and concurrency control
bot_procs = {}


def cleanup_bots():
    # Clean up function, just to be extra safe
    for proc, room_url in bot_procs.values():
        proc.terminate()
        proc.wait()


def create_room_with_bot():
    print(f"!!! Creating room")
    room_url, room_name, room_sip_uri = create_room()
    print(f"!!! Room URL: {room_url}")
    # Ensure the room property is present
    if not room_url:
        raise HTTPException(
            status_code=500,
            detail="Missing 'room' property in request data. Cannot start agent without a target room!",
        )

    # Check if there is already an existing process running in this room
    num_bots_in_room = sum(
        1
        for proc in bot_procs.values()
        if proc[1] == room_url and proc[0].poll() is None
    )
    if num_bots_in_room >= MAX_BOTS_PER_ROOM:
        raise HTTPException(
            status_code=500, detail=f"Max bot limited reach for room: {room_url}"
        )

    # Get the token for the room
    token = get_token(room_url)

    if not token:
        raise HTTPException(
            status_code=500, detail=f"Failed to get token for room: {room_url}"
        )

    # Spawn a new agent, and join the user session
    # Note: this is mostly for demonstration purposes (refer to 'deployment' in README)
    try:
        current_file_path = Path(__file__).resolve()
        grandparent_directory = current_file_path.parents[2]

        proc = subprocess.Popen(
            [f"python3 src/bot.py -u {room_url} -t {token}"],
            shell=True,
            bufsize=1,
            cwd=grandparent_directory,
        )
        bot_procs[proc.pid] = (proc, room_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start subprocess: {e}")

    return room_url, room_name, room_sip_uri
