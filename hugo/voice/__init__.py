"""Voice module — XIAO ESP32-S3 onboard mic over WiFi.

Audio streams from the XIAO #1's onboard PDM MEMS microphone
via HTTP to the Mac mini. The Mac mini runs wake word detection,
VAD, and speech-to-text (whisper.cpp) locally.

Features:
- Wake word detection ("Hey Hugo") via whisper.cpp on Mac mini
- Voice commands ("help me with number three")
- Voice activity detection (VAD) via webrtcvad
"""
