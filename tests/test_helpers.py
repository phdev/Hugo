"""Tests for hint generation helpers."""

from hugo.classifier.classify import ProblemType
from hugo.helpers import generate_hint
from hugo.helpers.math_helper import generate_math_hint
from hugo.helpers.reading_helper import generate_reading_hint
from hugo.layout.analyze import Problem


def _make_problem(id: int, text: str) -> Problem:
    return Problem(id=id, text=text, bbox=(60, 100, 300, 30))


# ── Math hints ──

def test_addition_dot_count():
    """Small addition → dot counting hint."""
    p = _make_problem(1, "3 + 2 = ___")
    hint = generate_math_hint(p, ProblemType.ADDITION)
    assert hint.hint_type == "dot_count"
    assert hint.content["operator"] == "+"
    groups = hint.content["groups"]
    assert groups[0]["count"] == 3
    assert groups[1]["count"] == 2
    assert "crossed" not in groups[0]


def test_addition_number_line():
    """Larger addition → number line hint."""
    p = _make_problem(1, "7 + 5 = ___")
    hint = generate_math_hint(p, ProblemType.ADDITION)
    assert hint.hint_type == "number_line"
    assert hint.content["start"] == 7
    assert hint.content["hops"] == 5
    assert hint.content["direction"] == "forward"


def test_subtraction_dot_count():
    """Subtraction → dot counting with crossed-out dots."""
    p = _make_problem(1, "6 - 2 = ___")
    hint = generate_math_hint(p, ProblemType.SUBTRACTION)
    assert hint.hint_type == "dot_count"
    groups = hint.content["groups"]
    assert groups[0]["count"] == 4  # remaining
    assert groups[1]["count"] == 2  # crossed out
    assert groups[1]["crossed"] is True


def test_subtraction_number_line():
    """Large subtraction → number line hopping backward."""
    p = _make_problem(1, "15 - 6 = ___")
    hint = generate_math_hint(p, ProblemType.SUBTRACTION)
    assert hint.hint_type == "number_line"
    assert hint.content["start"] == 15
    assert hint.content["direction"] == "backward"


def test_unparseable_math():
    """Unparseable text → generic hint."""
    p = _make_problem(1, "solve this puzzle")
    hint = generate_math_hint(p, ProblemType.ADDITION)
    assert hint.hint_type == "generic"


# ── Reading hints ──

def test_phonics_hint():
    """'What sound does B make?' → phonics word-picture hint."""
    p = _make_problem(1, "What sound does B make?")
    hint = generate_reading_hint(p, ProblemType.PHONICS)
    assert hint.hint_type == "phonics"
    assert hint.content["letter"] == "B"
    assert len(hint.content["words"]) == 3
    assert hint.content["words"][0]["emoji"] == "🐻"


def test_sight_word_hint():
    """'Circle the word: cat' → phonics breakdown hint."""
    p = _make_problem(1, "Circle the word: cat")
    hint = generate_reading_hint(p, ProblemType.SIGHT_WORDS)
    assert hint.hint_type == "phonics_breakdown"
    parts = hint.content["parts"]
    assert len(parts) == 3
    assert parts[0]["letter"] == "c"
    assert parts[0]["sound"] == "cuh"


def test_sight_word_unknown():
    """Unknown sight word → letter-by-letter breakdown."""
    p = _make_problem(1, "Circle the word: zog")
    hint = generate_reading_hint(p, ProblemType.SIGHT_WORDS)
    assert hint.hint_type == "phonics_breakdown"
    parts = hint.content["parts"]
    assert len(parts) == 3
    assert parts[0]["letter"] == "z"


def test_trace_hint():
    """'Trace the letter: S' → tracing guide hint."""
    p = _make_problem(1, "Trace the letter: S")
    hint = generate_reading_hint(p, ProblemType.TRACING)
    assert hint.hint_type == "trace"
    assert hint.content["letter"] == "S"


# ── Router ──

def test_route_addition():
    p = _make_problem(1, "3 + 2 = ___")
    hint = generate_hint(p, ProblemType.ADDITION)
    assert hint.hint_type == "dot_count"


def test_route_phonics():
    p = _make_problem(1, "What sound does B make?")
    hint = generate_hint(p, ProblemType.PHONICS)
    assert hint.hint_type == "phonics"


def test_route_unknown():
    p = _make_problem(1, "something unknown")
    hint = generate_hint(p, ProblemType.UNKNOWN)
    assert hint.hint_type == "generic"
