#!/bin/bash
set -e

echo "Initializing Ollama models..."

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    sleep 2
done

echo "Ollama is ready!"

# Pull models (override with environment variables if needed)
OLLAMA_CHAT_MODEL="${OLLAMA_MODEL:-jais:7b}"
OLLAMA_EMBED_MODEL="${OLLAMA_EMBEDDING_MODEL:-nomic-embed-text:latest}"

echo "Pulling chat model: ${OLLAMA_CHAT_MODEL}"
ollama pull "${OLLAMA_CHAT_MODEL}"

echo "Pulling embedding model: ${OLLAMA_EMBED_MODEL}"
ollama pull "${OLLAMA_EMBED_MODEL}"

echo "Models ready! You can use them now."
