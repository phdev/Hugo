"""Integration tests — full pipeline on fixture worksheets."""

import pytest
from pathlib import Path

from hugo.classifier.classify import ProblemType
from hugo.orchestrator.pipeline import PipelineResult, run_once
from hugo.vision.preprocess import preprocess
from hugo.ocr.extract import extract_lines
from hugo.layout.analyze import analyze_layout, Problem
from hugo.classifier.classify import classify_problem

FIXTURES = Path(__file__).parent / "fixtures"


def test_math_pipeline():
    """Full pipeline: math worksheet → problems detected."""
    result = run_once(FIXTURES / "math_worksheet.png")
    assert len(result.problems) >= 7

    types = [result.classifications[p.id] for p in result.problems]
    assert types.count(ProblemType.ADDITION) >= 3
    assert types.count(ProblemType.SUBTRACTION) >= 2


def test_reading_pipeline():
    """Full pipeline: reading worksheet → problems detected."""
    result = run_once(FIXTURES / "reading_worksheet.png")
    assert len(result.problems) >= 4

    types = [result.classifications[p.id] for p in result.problems]
    phonics = types.count(ProblemType.PHONICS)
    sight = types.count(ProblemType.SIGHT_WORDS)
    assert phonics >= 2
    assert sight >= 1


def test_classifier_patterns():
    """Classifier regex rules against known strings."""
    cases = [
        ("3 + 2 = ___", ProblemType.ADDITION),
        ("6 - 2 = ___", ProblemType.SUBTRACTION),
        ("What sound does B make?", ProblemType.PHONICS),
        ("Circle the word: cat", ProblemType.SIGHT_WORDS),
        ("Trace the letter: S", ProblemType.TRACING),
        ("How many sides?", ProblemType.SHAPES),
        ("What comes next?", ProblemType.PATTERNS),
        ("Match the shape to its name", ProblemType.MATCHING),
        ("something random", ProblemType.UNKNOWN),
    ]

    for text, expected in cases:
        p = Problem(id=1, text=text, bbox=(0, 0, 100, 30))
        result = classify_problem(p, use_llm=False)
        assert result == expected, f"Expected {expected} for '{text}', got {result}"


def test_pipeline_result_summary():
    """summary() produces readable output."""
    result = run_once(FIXTURES / "math_worksheet.png")
    text = result.summary()
    assert "Problems detected:" in text
    assert "addition" in text or "subtraction" in text
