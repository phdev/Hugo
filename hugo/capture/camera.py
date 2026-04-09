"""Camera interface — XIAO ESP32-S3 Sense + OV5640 over WiFi.

The XIAO streams MJPEG on :8080/stream and single frames on
:8080/capture. In dev mode, loads images from disk.
"""

import io
import logging
from pathlib import Path

import httpx
from PIL import Image

logger = logging.getLogger(__name__)

# ── Configuration ──

XIAO_CAM_HOST: str = "hugo-cam.local"
XIAO_CAM_PORT: int = 8080
CAPTURE_TIMEOUT: float = 5.0


def capture_frame(
    source: str | Path | None = None,
    host: str = XIAO_CAM_HOST,
    port: int = XIAO_CAM_PORT,
) -> Image.Image:
    """Capture a single frame from the camera or load from file.

    Args:
        source: Path to an image file for dev/testing. If None,
                captures from the XIAO camera over HTTP.
        host: XIAO camera hostname or IP.
        port: HTTP port (default 8080).

    Returns:
        A PIL Image of the worksheet.
    """
    if source is not None:
        return Image.open(source)

    url = f"http://{host}:{port}/capture"
    try:
        response = httpx.get(url, timeout=CAPTURE_TIMEOUT)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content))
    except httpx.ConnectError:
        raise ConnectionError(
            f"Cannot reach XIAO camera at {url}. "
            "Check WiFi and that the XIAO is powered on."
        )


def capture_stream(
    host: str = XIAO_CAM_HOST,
    port: int = XIAO_CAM_PORT,
):
    """Open an MJPEG stream from the XIAO camera.

    Yields PIL Images as they arrive. Use for continuous capture
    in the main pipeline loop.

    Yields:
        PIL Image frames.
    """
    url = f"http://{host}:{port}/stream"
    with httpx.stream("GET", url, timeout=None) as response:
        buffer = b""
        for chunk in response.iter_bytes():
            buffer += chunk
            # MJPEG frames are delimited by JPEG SOI/EOI markers
            while True:
                soi = buffer.find(b"\xff\xd8")
                eoi = buffer.find(b"\xff\xd9", soi + 2) if soi >= 0 else -1
                if soi < 0 or eoi < 0:
                    break
                jpeg_data = buffer[soi:eoi + 2]
                buffer = buffer[eoi + 2:]
                try:
                    yield Image.open(io.BytesIO(jpeg_data))
                except Exception as e:
                    logger.warning(f"Bad MJPEG frame: {e}")
