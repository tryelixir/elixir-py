from pipecat.frames.frames import TextFrame


async def start_fetch_weather(llm):
    await llm.push_frame(TextFrame("Let me think."))


async def fetch_weather_from_api(llm, args):
    return {"conditions": "nice", "temperature": "75"}
