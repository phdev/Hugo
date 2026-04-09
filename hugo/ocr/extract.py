"""Text extraction from preprocessed worksheet images.

Wraps Tesseract or PaddleOCR to pull printed and handwritten
text with bounding box positions.
"""

from dataclasses import dataclass

from PIL import Image


@dataclass
class OcrResult:
    """A single text region detected by OCR."""

    text: str
    bbox: tuple[int, int, int, int]  # (x, y, width, height)
    confidence: float


def extract_text(image: Image.Image) -> list[OcrResult]:
    """Extract text regions from a preprocessed worksheet image.

    Returns a list of OcrResult with text, bounding box, and
    confidence score for each detected region.
    """
    raise NotImplementedError
