"""LED feedback via XIAO ESP32-S3 onboard LED over WiFi.

The XIAO #1 has a WS2812 addressable LED. We control it via
HTTP POST to give visual feedback for voice state.
"""

import logging
from enum import Enum

import httpx

logger = logging.getLogger(__name__)

XIAO_CAM_HOST: str = "hugo-cam.local"
XIAO_CAM_PORT: int = 8080


class LEDState(Enum):
    """LED feedback states."""

    OFF = "off"
    LISTENING = "listening"         # pulsing cyan
    COMMAND_MODE = "command_mode"   # solid green
    PROCESSING = "processing"       # yellow flash
    ERROR = "error"                 # red flash
    SUCCESS = "success"             # green flash


def set_led(
    state: LEDState,
    host: str = XIAO_CAM_HOST,
    port: int = XIAO_CAM_PORT,
) -> None:
    """Set the XIAO LED to reflect the current voice state.

    Sends an HTTP POST to the XIAO's LED control endpoint.
    Fails silently if the XIAO is unreachable.
    """
    url = f"http://{host}:{port}/led"
    try:
        httpx.post(url, json={"state": state.value}, timeout=1.0)
    except Exception as e:
        logger.debug(f"LED control failed: {e}")
