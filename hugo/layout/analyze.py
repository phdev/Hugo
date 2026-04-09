"""Worksheet layout analysis.

Groups OCR lines into logical problems by detecting numbered
prefixes (1., 2., etc.) and collecting subsequent non-numbered
lines as part of the same problem. Produces a structured
WorksheetLayout for downstream classification.
"""

import re
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
    title: str = ""


# Pattern for problem numbers: "1.", "2.", "10." etc.
# Also matches without period ("1 3+2=") since OCR sometimes drops it.
_PROBLEM_NUM_RE = re.compile(r"^(\d{1,2})\.?\s+(.*)")

# OCR often merges digits with operators in math expressions.
# "342=__" is really "3 + 2 = ___" where + was read as 4.
# "54+3=__" is really "5 + 3 = ___" where the first digit
# appeared to merge with an OCR-garbled operator.
# Strategy: if we see a pattern like "XY+Z=" or "XYZ=" where
# Y looks like it could be an operator, split it.
_MATH_WITH_OP_RE = re.compile(r"(\d+)\s*([+\-−])\s*(\d+)\s*=\s*(.*)")
_GARBLED_MATH_RE = re.compile(r"^(\d)(\d)(\d)\s*=\s*(.*)")  # "342=" → 3+2=

# A lone number on a line is likely a problem number with the
# expression on a separate OCR line or missed entirely.
_LONE_NUM_RE = re.compile(r"^(\d{1,2})\.?$")


def _is_header_line(text: str) -> bool:
    """Check if a line is a title, name/date, or instructions."""
    lower = text.lower()
    return any(kw in lower for kw in [
        "name:", "date:", "practice", "sounds", "shapes",
        "patterns", "instructions", "show your work",
    ])


def _extract_answer_blank(text: str) -> bool:
    """Check if a problem line contains an answer blank."""
    return "___" in text or "____" in text or "= _" in text


def _is_continuation(text: str, current: Problem) -> bool:
    """Check if a non-numbered line belongs to the current problem."""
    # If it contains math symbols or equals sign, it's likely a
    # math expression that got split from its problem number
    if re.search(r"[+\-−=]", text):
        return True
    # If it's all digits and symbols, likely garbled math
    if re.match(r"^[\d+\-−=_ ]+$", text):
        return True
    return False


def _fix_math_ocr(text: str) -> str:
    """Fix common Tesseract misreads in math expressions.

    Tesseract frequently garbles math operators:
    - "54+3=__" is really "5 + 3 = ___" (operator partially read)
    - "342=__" is really "3 + 2 = ___" (+ read as digit 4)
    - "74+5=__" is really "7 + 5 = ___"

    If the text already has a clean operator, return as-is.
    """
    # Already has a clean operator → fine
    m = _MATH_WITH_OP_RE.match(text)
    if m:
        return text

    # "XYZ=..." where middle digit is a garbled operator
    # e.g. "342=__" → 3 ? 2 = __  (we can't know +/- so leave as "3 ? 2 =")
    # But we do know it's a math problem, which is enough for classification.
    m = _GARBLED_MATH_RE.match(text)
    if m:
        a, _op, b, rest = m.groups()
        # We can't recover the operator but we can mark it as math
        return f"{a} + {b} = {rest}"  # assume addition; classifier just needs the pattern

    return text


def analyze_layout(
    ocr_results: list[OcrResult],
    page_size: tuple[int, int],
) -> WorksheetLayout:
    """Analyze OCR results to detect individual problems.

    Strategy:
    1. Skip header lines (title, name/date).
    2. Lines starting with "N." begin a new problem.
    3. Non-numbered lines are appended to the current problem.
    4. Bounding boxes are the union of all OCR regions in a problem.

    Args:
        ocr_results: Line-level OCR results sorted top-to-bottom.
        page_size: (width, height) of the worksheet image.

    Returns:
        WorksheetLayout with detected problems.
    """
    problems: list[Problem] = []
    title = ""
    current: Problem | None = None

    for region in ocr_results:
        text = region.text.strip()
        if not text:
            continue

        # Detect header
        if _is_header_line(text):
            if not title and not problems:
                title = text
            continue

        # Check for lone problem number ("1" or "1.")
        lone_match = _LONE_NUM_RE.match(text)
        if lone_match:
            if current is not None:
                problems.append(current)
            num = int(lone_match.group(1))
            current = Problem(
                id=num,
                text="",
                bbox=region.bbox,
                ocr_regions=[region],
            )
            continue

        # Check for problem number with expression
        match = _PROBLEM_NUM_RE.match(text)
        if match:
            # Save previous problem
            if current is not None:
                problems.append(current)

            num = int(match.group(1))
            rest = match.group(2).strip()

            # Fix OCR merge artifacts in math expressions
            rest = _fix_math_ocr(rest)

            current = Problem(
                id=num,
                text=rest,
                bbox=region.bbox,
                answer_bbox=region.bbox if _extract_answer_blank(rest) else None,
                ocr_regions=[region],
            )
        elif current is not None and (current.text == "" or _is_continuation(text, current)):
            # Continuation line — either the current problem has no
            # text yet (lone number), or this line is clearly part
            # of the same problem (close vertically)
            fixed = _fix_math_ocr(text)
            if current.text:
                current.text += " " + fixed
            else:
                current.text = fixed
            current.ocr_regions.append(region)
            # Expand bounding box
            cx, cy, cw, ch = current.bbox
            rx, ry, rw, rh = region.bbox
            new_x = min(cx, rx)
            new_y = min(cy, ry)
            new_w = max(cx + cw, rx + rw) - new_x
            new_h = max(cy + ch, ry + rh) - new_y
            current.bbox = (new_x, new_y, new_w, new_h)
            if _extract_answer_blank(text) and current.answer_bbox is None:
                current.answer_bbox = region.bbox

    # Don't forget the last problem
    if current is not None:
        problems.append(current)

    return WorksheetLayout(
        problems=problems,
        page_size=page_size,
        title=title,
    )
