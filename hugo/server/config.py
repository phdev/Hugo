"""Server-side configuration."""

import os

# Inference
OLLAMA_BASE_URL: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.environ.get("OLLAMA_MODEL", "qwen3:4b")
WHISPER_MODEL: str = os.environ.get("WHISPER_MODEL", "base")

# API keys
ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "")
GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")

# Server
HOST: str = "0.0.0.0"
PORT: int = 8000
