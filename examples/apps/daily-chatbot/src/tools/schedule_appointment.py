from pipecat.frames.frames import TextFrame
from openai.types.chat import ChatCompletionToolParam

schedule_appointment_tool = ChatCompletionToolParam(
    type="function",
    function={
        "name": "schedule_appointment",
        "description": "Schedule the appointment",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "format": "date",
                    "description": "The date of the appointment, in YYYY-MM-DD format",
                },
                "time": {
                    "type": "string",
                    "format": "time",
                    "description": "The time of the appointment, in HH:MM format",
                },
            },
            "required": ["date", "time"],
        },
    },
)


async def start_schedule_appointment(llm):
    await llm.push_frame(TextFrame("Sure let me book that for you. Give me a second!"))


async def schedule_appointment(llm, args):
    return {"status": "success"}
