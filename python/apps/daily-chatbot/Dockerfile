FROM python:3.10-bullseye

RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy shared
WORKDIR /shared

RUN mkdir /shared/pipecat

COPY shared/pipecat/src /shared/pipecat/src
COPY shared/pipecat/pyproject.toml shared/pipecat/poetry.lock /shared/pipecat/

WORKDIR /shared/pipecat

RUN pip install poetry
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Copy daily-chatbot
WORKDIR /app

RUN mkdir /app/assets
RUN mkdir /app/utils

COPY apps/daily-chatbot/*.py /app/
COPY apps/daily-chatbot/pyproject.toml apps/daily-chatbot/poetry.lock /app/
COPY apps/daily-chatbot/assets/* /app/assets/
COPY apps/daily-chatbot/utils/* /app/utils/

# Install Poetry
RUN pip install poetry
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

EXPOSE 7860

CMD ["python3", "server.py"]