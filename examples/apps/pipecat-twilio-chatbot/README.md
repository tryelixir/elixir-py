# Twilio Chatbot

This project is a FastAPI-based chatbot that integrates with Twilio to handle WebSocket connections and provide real-time communication. The project includes endpoints for starting a call and handling WebSocket connections.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configure Twilio URLs](#configure-twilio-urls)
- [Running the Application](#running-the-application)
- [Usage](#usage)

## Features

- **FastAPI**: A modern, fast (high-performance), web framework for building APIs with Python 3.6+.
- **WebSocket Support**: Real-time communication using WebSockets.
- **CORS Middleware**: Allowing cross-origin requests for testing.
- **Dockerized**: Easily deployable using Docker.

## Requirements

- Python 3.10
- Docker (for containerized deployment)
- ngrok (for tunneling)
- Twilio Account

## Installation

```bash
poetry install
```

## Running the Application

### Using Python

1. **Run the FastAPI application**:

   ```sh
   poetry run python src/server.py
   ```

2. **Start ngrok**:
   In a new terminal, start ngrok to tunnel the local server:
   ```bash
   # Replace with your ngrok domain
   ngrok http --domain=elixir-py-twilio-chatbot.ngrok.app 8765
   ```

## Usage

To start a call, simply make a call to your Twilio phone number. The webhook URL will direct the call to your FastAPI application, which will handle it accordingly.

`(510) 619-2831` is the default number that has been configured with `elixir-py-twilio-chatbot.ngrok.app`.
