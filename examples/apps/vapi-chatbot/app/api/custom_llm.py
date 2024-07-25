import os
from flask import Blueprint, request, Response
from openai import OpenAI
from elixir import Elixir

Elixir.init()

custom_llm = Blueprint("custom_llm", __name__)

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv("OPENAI_API_KEY"),
)


def generate_streaming_response(data):
    """
    Generator function to simulate streaming data.
    """
    for message in data:
        json_data = message.model_dump_json()
        yield f"data: {json_data}\n\n"


@custom_llm.route("/chat/completions", methods=["POST"])
def custom_llm_openai_sse_handler():
    request_data = request.get_json()
    Elixir.init_conversation(request_data["call"]["id"])
    Elixir.identify("test-user", {"name": "Test User"})

    chat_request_data = {
        "model": request_data["model"],
        "messages": request_data["messages"],
        "tools": request_data["tools"],
        "max_tokens": request_data["max_tokens"],
        "temperature": request_data["temperature"],
    }

    chat_completion_stream = client.chat.completions.create(
        **chat_request_data, stream=True
    )

    return Response(
        generate_streaming_response(chat_completion_stream),
        content_type="text/event-stream",
    )
