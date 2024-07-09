from openai.types.chat import ChatCompletionToolParam

get_calendar_schedule_tool = ChatCompletionToolParam(
    type="function",
    function={
        "name": "get_calendar_schedule",
        "description": "Get the appointment availability for a given date",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "format": "date",
                    "description": "The date for which to retrieve the schedule, in YYYY-MM-DD format",
                }
            },
            "required": ["date"],
        },
    },
)


async def get_calendar_schedule(args):
    return {
        "available_times": [
            {"start_time": "14:00", "end_time": "14:30"},
            {"start_time": "16:30", "end_time": "17:00"},
        ]
    }
