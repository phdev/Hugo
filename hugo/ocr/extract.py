"""Text extraction from preprocessed worksheet images.

Uses Tesseract OCR to extract printed text with bounding box
positions. Returns structured OcrResult objects that feed into
the layout analysis module.
"""

from dataclasses import dataclass

import pytesseract
from PIL import Image


@dataclass
class OcrResult:
    """A single text region detected by OCR."""

    text: str
    bbox: tuple[int, int, int, int]  # (x, y, width, height)
    confidence: float


def extract_text(image: Image.Image, min_confidence: float = 20.0) -> list[OcrResult]:
    """Extract text regions from a preprocessed worksheet image.

    Uses Tesseract's word-level output with bounding boxes and
    confidence scores. Filters out low-confidence noise.

    Args:
        image: Preprocessed (ideally binary) worksheet image.
        min_confidence: Minimum confidence to include (0-100).

    Returns:
        List of OcrResult sorted top-to-bottom, left-to-right.
    """
    # Get word-level data with bounding boxes
    # PSM 4 = single column of variable-size text (best for worksheets)
    data = pytesseract.image_to_data(
        image,
        output_type=pytesseract.Output.DICT,
        config="--psm 4",
    )

    results = []
    n = len(data["text"])

    for i in range(n):
        text = data["text"][i].strip()
        conf = float(data["conf"][i])

        if not text or conf < min_confidence:
            continue

        results.append(OcrResult(
            text=text,
            bbox=(
                data["left"][i],
                data["top"][i],
                data["width"][i],
                data["height"][i],
            ),
            confidence=conf,
        ))

    # Sort by y position, then x
    results.sort(key=lambda r: (r.bbox[1], r.bbox[0]))
    return results


def extract_lines(image: Image.Image, min_confidence: float = 20.0) -> list[OcrResult]:
    """Extract text as full lines rather than individual words.

    Groups Tesseract output by line number and merges words into
    single line-level OcrResult objects.

    Args:
        image: Preprocessed worksheet image.
        min_confidence: Minimum word confidence to include.

    Returns:
        List of OcrResult, one per detected line, sorted top-to-bottom.
    """
    data = pytesseract.image_to_data(
        image,
        output_type=pytesseract.Output.DICT,
        config="--psm 4",
    )

    # Group words by (block_num, par_num, line_num)
    lines: dict[tuple[int, int, int], list[int]] = {}
    n = len(data["text"])

    for i in range(n):
        text = data["text"][i].strip()
        conf = float(data["conf"][i])
        if not text or conf < min_confidence:
            continue

        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        lines.setdefault(key, []).append(i)

    results = []
    for key in sorted(lines.keys()):
        indices = lines[key]
        words = [data["text"][i].strip() for i in indices]
        line_text = " ".join(words)

        # Bounding box: union of all word boxes in this line
        x_min = min(data["left"][i] for i in indices)
        y_min = min(data["top"][i] for i in indices)
        x_max = max(data["left"][i] + data["width"][i] for i in indices)
        y_max = max(data["top"][i] + data["height"][i] for i in indices)

        avg_conf = sum(float(data["conf"][i]) for i in indices) / len(indices)

        results.append(OcrResult(
            text=line_text,
            bbox=(x_min, y_min, x_max - x_min, y_max - y_min),
            confidence=avg_conf,
        ))

    results.sort(key=lambda r: r.bbox[1])
    return results
