"""Arducam Pi Camera 3 Wide — CSI capture on Pi 5.

Captures worksheet images via Picamera2, sends full-resolution
frames to the Mac mini inference server for homework analysis.
Caches the latest analysis result locally for instant hint lookup.
"""

import io
import logging
from pathlib import Path

import httpx
from PIL import Image

from hugo.pi.config import (
    CAPTURE_HEIGHT,
    CAPTURE_WIDTH,
    FULL_RES_HEIGHT,
    FULL_RES_WIDTH,
    SERVER_BASE_URL,
)

logger = logging.getLogger(__name__)


def capture_frame(
    source: str | Path | None = None,
    full_res: bool = False,
) -> Image.Image:
    """Capture a single frame from the camera or load from file.

    Args:
        source: Path to image file for dev/testing. None = live camera.
        full_res: If True, capture at 4608×2592 for analysis.
                  If False, capture at 1280×960 for monitoring.

    Returns:
        PIL Image of the worksheet.
    """
    if source is not None:
        return Image.open(source)

    try:
        from picamera2 import Picamera2

        cam = Picamera2()
        if full_res:
            config = cam.create_still_configuration(
                main={"size": (FULL_RES_WIDTH, FULL_RES_HEIGHT)},
            )
        else:
            config = cam.create_still_configuration(
                main={"size": (CAPTURE_WIDTH, CAPTURE_HEIGHT)},
            )
        cam.configure(config)
        cam.start()
        frame = cam.capture_image("main")
        cam.stop()
        cam.close()
        return frame
    except ImportError:
        raise RuntimeError(
            "Picamera2 not installed. Use source= for dev mode, "
            "or install on Pi 5: pip install picamera2"
        )


def analyze_homework(
    image: Image.Image,
    server_url: str = SERVER_BASE_URL,
    timeout: float = 15.0,
) -> dict:
    """Send a frame to the Mac mini for homework analysis.

    POSTs JPEG to /analyze-homework, returns structured problems.

    Returns:
        {"problems": [{"id": 1, "text": "3+2=", "type": "addition",
                        "bbox": [x,y,w,h], "hint": {...}}, ...]}
    """
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=90)
    buf.seek(0)

    try:
        response = httpx.post(
            f"{server_url}/analyze-homework",
            files={"image": ("frame.jpg", buf, "image/jpeg")},
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError:
        logger.error(f"Cannot reach server at {server_url}")
        return {"problems": []}
    except Exception as e:
        logger.error(f"Homework analysis failed: {e}")
        return {"problems": []}
