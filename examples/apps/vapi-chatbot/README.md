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

## Docker

1. Build the Docker app

   ```bash
   docker build -t vapi-chatbot -f Dockerfile ../../..
   ```

2. Run the Docker image

   ```bash
   docker run -p 8000:8000 --env-file .env vapi-chatbot
   ```

## Call the Assistant

To expose the server to the internet, use `ngrok`:

```bash
ngrok http --domain=YOUR_DOMAIN 8000
```

Set the resultant URL in your env file as `SERVER_URL`. If not set, the script will hit the production server `https://elixir-vapi-chatbot.onrender.com`. Then, run the script to call the Vapi agent:

```bash
poetry run python scripts/call_vapi_agent.py
```
