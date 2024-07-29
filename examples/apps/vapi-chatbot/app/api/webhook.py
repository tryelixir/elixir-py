import json
import logging
from elixir import Elixir
from flask import Blueprint, request, jsonify
from app.tools import functions

webhook = Blueprint("webhook", __name__)

log = logging.getLogger(__name__)


@webhook.route("/", methods=["POST"])
async def webhook_route():
    request_data = request.get_json()
    payload = request_data.get("message")

    Elixir.init_conversation(payload["call"]["id"])
    Elixir.identify("test-user", {"name": "Test User"})

    if payload["type"] == "tool-calls":
        response = await tool_calls_handler(payload)
        return jsonify(response), 201
    elif payload["type"] == "status-update":
        response = await status_update_handler(payload)
        return jsonify(response), 201
    elif payload["type"] == "assistant-request":
        response = await assistant_request_handler(payload)
        return jsonify(response), 201
    elif payload["type"] == "end-of-call-report":
        await end_of_call_report_handler(payload)
        return jsonify({}), 201
    elif payload["type"] == "speech-update":
        response = await speech_update_handler(payload)
        return jsonify(response), 201
    elif payload["type"] == "transcript":
        response = await transcript_handler(payload)
        return jsonify(response), 201
    elif payload["type"] == "hang":
        response = await hang_event_handler(payload)
        return jsonify(response), 201
    else:
        return jsonify({"message": "Unhandled message type"}), 201


async def tool_calls_handler(payload):
    """
    Handle Business logic here.
    You can handle function calls here. The payload will have function name and parameters.
    You can trigger the appropriate function based on your requirements and configurations.
    You can also have a set of validators along with each function which can be used to first validate the parameters and then call the functions.
    Here Assumption is that the functions are handling the fallback cases as well. They should return the appropriate response in case of any error.
    """

    tool_calls = payload.get("toolCalls")

    if not tool_calls:
        raise ValueError("Invalid Request.")

    results = []
    for tool_call in tool_calls:
        function = tool_call.get("function")
        name = function.get("name")
        arguments = function.get("arguments")

        tool_result = await functions[name](arguments)
        results.append(
            {
                "toolCallId": tool_call.get("id"),
                "result": json.dumps(tool_result),
            }
        )

    return {"results": results}


async def status_update_handler(payload):
    """
    Handle Business logic here.
    Sent during a call whenever the status of the call has changed.
    Possible statuses are: "queued","ringing","in-progress","forwarding","ended".
    You can have certain logic or handlers based on the call status.
    You can also store the information in your database. For example whenever the call gets forwarded.
    """
    return {}


async def end_of_call_report_handler(payload):
    """
    Handle Business logic here.
    You can store the information like summary, typescript, recordingUrl or even the full messages list in the database.
    """
    recording_url = payload.get("stereoRecordingUrl")
    call_id = payload.get("call").get("id")
    if recording_url:
        log.info(f"Conversation ID: {call_id}, recording URL: {recording_url}")
        await Elixir.upload_audio(conversation_id=call_id, audio_url=recording_url)


async def speech_update_handler(payload):
    """
    Handle Business logic here.
    Sent during a speech status update during the call. It also lets u know who is speaking.
    You can enable this by passing "speech-update" in the serverMessages array while creating the assistant.
    """
    return {}


async def transcript_handler(payload):
    """
    Handle Business logic here.
    Sent during a call whenever the transcript is available for certain chunk in the stream.
    You can store the transcript in your database or have some other business logic.
    """
    return


async def hang_event_handler(payload):
    """
    Handle Business logic here.
    Sent once the call is terminated by user.
    You can update the database or have some followup actions or workflow triggered.
    """
    return


async def assistant_request_handler(payload):
    """
    Handle Business logic here.
    You can fetch your database to see if there is an existing assistant associated with this call. If yes, return the assistant.
    You can also fetch some params from your database to create the assistant and return it.
    You can have various predefined static assistant here and return them based on the call details.
    """
    return
