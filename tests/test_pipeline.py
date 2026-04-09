"""Integration tests — full pipeline on fixture worksheets."""

import pytest
from pathlib import Path

from hugo.vision.preprocess import preprocess
from hugo.ocr.extract import extract_lines
from hugo.layout.analyze import analyze_layout
from hugo.classifier.classify import classify_problem, ProblemType

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def math_worksheet():
    from PIL import Image
    return Image.open(FIXTURES / "math_worksheet.png")


@pytest.fixture
def reading_worksheet():
    from PIL import Image
    return Image.open(FIXTURES / "reading_worksheet.png")


def test_math_pipeline(math_worksheet):
    """Full pipeline: math worksheet → 8 detected problems."""
    processed = preprocess(math_worksheet)
    lines = extract_lines(processed)
    layout = analyze_layout(lines, math_worksheet.size)

    assert len(layout.problems) >= 7  # Tesseract may miss one

    types = [classify_problem(p) for p in layout.problems]
    addition_count = types.count(ProblemType.ADDITION)
    subtraction_count = types.count(ProblemType.SUBTRACTION)

    # Should detect a mix of addition and subtraction
    assert addition_count >= 3
    assert subtraction_count >= 2


def test_reading_pipeline(reading_worksheet):
    """Full pipeline: reading worksheet → 5 detected problems."""
    processed = preprocess(reading_worksheet)
    lines = extract_lines(processed)
    layout = analyze_layout(lines, reading_worksheet.size)

    assert len(layout.problems) >= 4  # Tesseract may miss one

    types = [classify_problem(p) for p in layout.problems]
    phonics_count = types.count(ProblemType.PHONICS)
    sight_count = types.count(ProblemType.SIGHT_WORDS)

    assert phonics_count >= 2
    assert sight_count >= 1


def test_classifier_patterns():
    """Unit test classifier regex rules against known strings."""
    from hugo.layout.analyze import Problem

    cases = [
        ("3 + 2 = ___", ProblemType.ADDITION),
        ("6 - 2 = ___", ProblemType.SUBTRACTION),
        ("10 - 3 = ___", ProblemType.SUBTRACTION),
        ("What sound does B make?", ProblemType.PHONICS),
        ("Circle the word: cat", ProblemType.SIGHT_WORDS),
        ("Trace the letter: S", ProblemType.TRACING),
        ("How many sides?", ProblemType.SHAPES),
        ("How many corners?", ProblemType.SHAPES),
        ("What comes next?", ProblemType.PATTERNS),
        ("Match the shape to its name", ProblemType.MATCHING),
        ("something random", ProblemType.UNKNOWN),
    ]

    for text, expected in cases:
        p = Problem(id=1, text=text, bbox=(0, 0, 100, 30))
        result = classify_problem(p)
        assert result == expected, f"Expected {expected} for '{text}', got {result}"
