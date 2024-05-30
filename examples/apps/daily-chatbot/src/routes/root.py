from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse

from services.bot import create_room_with_bot, bot_procs

root_router = APIRouter()


@root_router.get("/start")
async def start_agent():
    room_url, room_name, room_sip_uri = create_room_with_bot()
    return RedirectResponse(room_url)


@root_router.get("/status/{pid}")
def get_status(pid: int):
    # Look up the subprocess
    proc = bot_procs.get(pid)

    # If the subprocess doesn't exist, return an error
    if not proc:
        raise HTTPException(
            status_code=404, detail=f"Bot with process id: {pid} not found"
        )

    # Check the status of the subprocess
    if proc[0].poll() is None:
        status = "running"
    else:
        status = "finished"

    return JSONResponse({"bot_id": pid, "status": status})
