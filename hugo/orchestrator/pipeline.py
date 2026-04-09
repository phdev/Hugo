"""Main pipeline loop tying all Hugo modules together.

Capture → Vision → OCR → Layout → Classifier → Helpers → Projection.
Manages state transitions and error recovery.
"""

from pathlib import Path


def run_once(source: str | Path | None = None) -> None:
    """Run a single iteration of the Hugo pipeline.

    Args:
        source: Path to a worksheet image for dev/testing.
                If None, captures from the live camera.
    """
    raise NotImplementedError


def run_loop(source: str | Path | None = None) -> None:
    """Run the Hugo pipeline in a continuous loop.

    Args:
        source: Path to a worksheet image for dev/testing.
                If None, captures from the live camera.
    """
    raise NotImplementedError
