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


async def schedule_appointment(args):
    return {"status": "success"}
