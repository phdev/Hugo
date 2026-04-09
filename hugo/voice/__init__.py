"""Voice module — ReSpeaker Lite USB mic array integration.

Handles voice input from the ReSpeaker Lite (2-mic array, XMOS
XU316 with onboard noise suppression and echo cancellation).
Connected via USB to the Pi 5.

Features:
- Wake word detection ("Hey Hugo") for hands-free activation
- Voice commands ("help me with number three")
- Voice activity detection (VAD) to know when the kid is speaking
- LED feedback via WS2812 on the ReSpeaker board
"""
