"""Integration tests — full pipeline on fixture worksheets."""

import pytest
from pathlib import Path

from hugo.classifier.classify import ProblemType
from hugo.helpers.hint import Hint
from hugo.orchestrator.pipeline import PipelineResult, run_once
from hugo.vision.preprocess import preprocess
from hugo.ocr.extract import extract_lines
from hugo.layout.analyze import analyze_layout
from hugo.classifier.classify import classify_problem

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


# ── Orchestrator end-to-end ──

def test_run_once_math():
    """run_once produces a complete PipelineResult from a fixture image."""
    result = run_once(FIXTURES / "math_worksheet.png")

    assert isinstance(result, PipelineResult)
    assert len(result.problems) >= 7
    assert len(result.hints) == len(result.problems)
    assert result.overlay.size == result.worksheet.size

    # Every problem should have a classification and a hint
    for p in result.problems:
        assert p.id in result.classifications
        hint = next(h for h in result.hints if h.problem_id == p.id)
        assert isinstance(hint, Hint)
        assert hint.label  # non-empty label


def test_run_once_reading():
    """run_once works on reading worksheets too."""
    result = run_once(FIXTURES / "reading_worksheet.png")

    assert len(result.problems) >= 4
    assert len(result.hints) == len(result.problems)

    # Check we got phonics and sight word hints
    types = set(h.hint_type for h in result.hints)
    assert "phonics" in types or "phonics_breakdown" in types


def test_pipeline_result_summary():
    """summary() produces readable output."""
    result = run_once(FIXTURES / "math_worksheet.png")
    text = result.summary()
    assert "Problems detected:" in text
    assert "addition" in text or "subtraction" in text
