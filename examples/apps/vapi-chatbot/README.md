# Server-Side Example Python Flask

This repository hosts a Python Flask application that demonstrates server-side operations with Flask. This project is structured to provide a straightforward example of how to manage API integrations and environment configurations.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.6 or higher
- Poetry for dependency management

## Installation

Install dependencies using Poetry:

```bash
poetry install
```

## Configuring Environment Variables

This project requires certain environment variables to be set. Create a .env file in the root directory of your project and add the keys found in the `.example.env` file.

## Running the Project

To run the project, use Poetry to handle the environment:

```bash
poetry run flask --app ./app/main run --host=0.0.0.0 --port=8000 --debug
```

This command starts the Flask server on http://127.0.0.1:8000/. You can access the server from your web browser at this address.

To expose the server to the internet, use `ngrok`:

```bash
ngrok http --domain=elixir-py-vapi-chatbot.ngrok.app 8000
```

Set the resultant URL in your env file as `SERVER_URL`. Then, run the script to call the Vapi agent:

```bash
poetry run python scripts/call_vapi_agent.py
```
