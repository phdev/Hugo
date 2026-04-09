"""Worksheet layout analysis.

Detects individual problems, answer blanks, and spatial regions
on a worksheet page. Produces a structured map for downstream
classification and projection alignment.
"""

from dataclasses import dataclass, field

from hugo.ocr.extract import OcrResult


@dataclass
class Problem:
    """A single problem detected on the worksheet."""

    id: int
    text: str
    bbox: tuple[int, int, int, int]  # (x, y, width, height)
    answer_bbox: tuple[int, int, int, int] | None = None
    ocr_regions: list[OcrResult] = field(default_factory=list)


@dataclass
class WorksheetLayout:
    """Structured layout of a worksheet page."""

    problems: list[Problem]
    page_size: tuple[int, int]  # (width, height)


def analyze_layout(
    ocr_results: list[OcrResult],
    page_size: tuple[int, int],
) -> WorksheetLayout:
    """Analyze OCR results to detect individual problems and blanks.

    Groups nearby text regions into logical problems and identifies
    answer blanks (underlines, empty boxes, etc.).
    """
    raise NotImplementedError
