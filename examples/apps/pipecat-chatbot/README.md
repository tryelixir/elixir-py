<div align="center">
 <img alt="pipecat" width="300px" height="auto" src="image.png">
</div>

# Dialin example

Example project that demonstrates how to add phone number dialin to your Pipecat bots.

- 🔁 Transport: Daily WebRTC
- 💬 Speech-to-Text: Deepgram via Daily transport
- 🤖 LLM: GPT4-o / OpenAI
- 🔉 Text-to-Speech: ElevenLabs

## Setup

```shell
# Install the requirements
poetry install

# Setup your env
mv env.example .env
```

## Using Twilio numbers

Run `bot_runner.py` to handle incoming HTTP requests:

```shell
poetry run python src/bot_runner.py --host localhost
```

Target the following URL:

`POST /twilio_start_bot`

Expose the server to the internet via ngrok. Note that this is a persistent ngrok domain that may cause issues if run by multiple people. To avoid collisions, we can spin up Twilio numbers as needed and configure the webhook URL.

```bash
# Replace with your ngrok domain
ngrok http --domain=elixir-py-pipecat-chatbot.ngrok.app 7860
```

The webhook url should be `{YOUR_NGROK_URL}/twilio`.

Then, call the configured number. `(510) 619 2831` is the default number that has been configured with `elixir-py-pipecat-chatbot.ngrok.app`.
