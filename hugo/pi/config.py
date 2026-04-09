"""Pi-side configuration."""

import os

# Mac mini inference server
SERVER_HOST: str = os.environ.get("HUGO_SERVER_HOST", "hugo-server.local")
SERVER_PORT: int = int(os.environ.get("HUGO_SERVER_PORT", "8000"))
SERVER_BASE_URL: str = f"http://{SERVER_HOST}:{SERVER_PORT}"

# Luma 350 native resolution
DISPLAY_WIDTH: int = 854
DISPLAY_HEIGHT: int = 480

# Camera
CAPTURE_WIDTH: int = 1280
CAPTURE_HEIGHT: int = 960
FULL_RES_WIDTH: int = 4608
FULL_RES_HEIGHT: int = 2592

# ToF sensor
TOF_I2C_BUS: int = 1
TOF_I2C_ADDRESS: int = 0x29
TOF_POLL_HZ: int = 15
TOF_TAP_THRESHOLD_MM: int = 30
TOF_TAP_TIMEOUT_MS: int = 500
TOF_DEBOUNCE_MS: int = 300

# Voice
SAMPLE_RATE: int = 16000
WAKE_PHRASE: str = "hey hugo"

# Orchestrator
DESK_SCAN_INTERVAL_SEC: int = 30
