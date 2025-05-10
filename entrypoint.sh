#!/bin/bash
set -e

echo "Starting Ollama service..."

# Pull models specified in OLLAMA_MODELS environment variable
if [ -n "$OLLAMA_MODELS" ]; then
  echo "Pulling specified models: $OLLAMA_MODELS"
  
  # Split the comma-separated list of models
  IFS=',' read -ra MODELS <<< "$OLLAMA_MODELS"
  
  for MODEL in "${MODELS[@]}"; do
    MODEL_TRIMMED=$(echo "$MODEL" | xargs)  # Trim whitespace
    if [ -n "$MODEL_TRIMMED" ]; then
      echo "Pulling model: $MODEL_TRIMMED"
      ollama pull "$MODEL_TRIMMED"
    fi
  done
else
  echo "No models specified in OLLAMA_MODELS. Skipping model pull."
fi

# List available models
echo "Available models:"
ollama list

# Start Ollama server
echo "Starting Ollama server..."
exec ollama serve
