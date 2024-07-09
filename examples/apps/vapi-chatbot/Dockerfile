# Use a base image with Python
FROM python:3.11-bullseye

# Install Poetry
RUN pip install poetry

# Copy the elixir directory into the image
COPY /elixir /elixir
COPY poetry.lock pyproject.toml README.md ./
RUN poetry install --no-root

WORKDIR /examples/apps/vapi-chatbot

# Copy the vapi-chatbot directory into the image
COPY /examples/apps/vapi-chatbot .
RUN apt-get update && apt-get install -y portaudio19-dev
RUN poetry install --no-root

# Command to run the application
CMD ["poetry", "run", "gunicorn", "--bind", "0.0.0.0:8000", "app.main:app"]
