"""Finger detection via camera frame differencing.

Uses background subtraction to detect a finger entering the
camera's view of the worksheet. The initial clean capture of the
worksheet (before any interaction) serves as the reference frame.
Subsequent frames are diffed to find new objects (fingers/hands).
"""

from dataclasses import dataclass

import numpy as np
from PIL import Image


@dataclass
class FingerDetection:
    """A detected fingertip position on the worksheet."""

    x: int
    y: int
    confidence: float  # 0.0–1.0
    contour_area: int  # pixel area of the detected region


def set_reference_frame(image: Image.Image) -> np.ndarray:
    """Store a clean worksheet capture as the background reference.

    Args:
        image: A clean capture of the worksheet with no hands present.

    Returns:
        Grayscale numpy array of the reference frame.
    """
    return np.array(image.convert("L"))


def detect_finger(
    frame: Image.Image,
    reference: np.ndarray,
    diff_threshold: int = 40,
    min_area: int = 200,
    max_area: int = 8000,
) -> FingerDetection | None:
    """Detect a fingertip in the current frame by diffing against reference.

    Converts the frame to grayscale, computes the absolute difference
    from the reference, thresholds to find changed regions, and
    identifies the topmost point of the largest qualifying contour
    as the fingertip.

    Args:
        frame: Current camera frame.
        reference: Grayscale reference from set_reference_frame().
        diff_threshold: Pixel intensity difference to count as changed.
        min_area: Minimum contour area (filters noise).
        max_area: Maximum contour area (filters whole-hand occlusion).

    Returns:
        FingerDetection if a fingertip is found, None otherwise.
    """
    raise NotImplementedError


def point_in_circle(
    px: int,
    py: int,
    cx: int,
    cy: int,
    radius: int,
) -> bool:
    """Check if point (px, py) is within a circle at (cx, cy) with given radius."""
    return (px - cx) ** 2 + (py - cy) ** 2 <= radius ** 2
