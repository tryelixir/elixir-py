#!/bin/bash

# List of opentelemetry-instrumentation packages to update
packages=(
  "opentelemetry-semantic-conventions-ai"
  "opentelemetry-instrumentation-mistralai"
  "opentelemetry-instrumentation-openai"
  "opentelemetry-instrumentation-ollama"
  "opentelemetry-instrumentation-anthropic"
  "opentelemetry-instrumentation-cohere"
  "opentelemetry-instrumentation-pinecone"
  "opentelemetry-instrumentation-qdrant"
  "opentelemetry-instrumentation-langchain"
  "opentelemetry-instrumentation-chromadb"
  "opentelemetry-instrumentation-transformers"
  "opentelemetry-instrumentation-llamaindex"
  "opentelemetry-instrumentation-milvus"
  "opentelemetry-instrumentation-haystack"
  "opentelemetry-instrumentation-bedrock"
  "opentelemetry-instrumentation-replicate"
  "opentelemetry-instrumentation-vertexai"
  "opentelemetry-instrumentation-watsonx"
  "opentelemetry-instrumentation-weaviate"
)

packages_str=$(printf " %s" "${packages[@]}")
packages_str=${packages_str:1}

poetry remove $packages_str
poetry add $packages_str

# Execute the command
eval $command