"""Mac mini inference server.

FastAPI endpoints that the Pi 5 calls over WiFi:
- /analyze-homework — JPEG → Claude Vision → structured problems
- /transcribe — PCM audio → whisper.cpp → text
- /get-help — problem → tiered LLM routing → hint
- /health — liveness check
"""
