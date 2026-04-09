"""Camera interface for capturing worksheet images.

In dev mode, loads images from disk. On the Pi, captures from
the Pi Camera Module via picamera2.
"""

from pathlib import Path

from PIL import Image


def capture_frame(source: str | Path | None = None) -> Image.Image:
    """Capture a single frame from the camera or load from file.

    Args:
        source: Path to an image file for dev/testing. If None,
                captures from the Pi camera (not yet implemented).

    Returns:
        A PIL Image of the worksheet.
    """
    if source is not None:
        return Image.open(source)
    raise NotImplementedError("Live camera capture not yet implemented")
