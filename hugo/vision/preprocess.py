"""Image preprocessing for worksheet analysis.

Applies lighting normalization, perspective correction, and
contrast enhancement to raw captured images.
"""

from PIL import Image


def normalize_lighting(image: Image.Image) -> Image.Image:
    """Normalize uneven lighting across the worksheet image."""
    raise NotImplementedError


def correct_perspective(image: Image.Image) -> Image.Image:
    """Correct perspective distortion from camera angle."""
    raise NotImplementedError


def enhance_for_ocr(image: Image.Image) -> Image.Image:
    """Enhance contrast and sharpen text for OCR extraction."""
    raise NotImplementedError


def preprocess(image: Image.Image) -> Image.Image:
    """Run the full preprocessing pipeline on a captured image.

    Applies lighting normalization, perspective correction, and
    OCR-optimized enhancement in sequence.
    """
    raise NotImplementedError
