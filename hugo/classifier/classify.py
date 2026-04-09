"""Problem type classifier.

Uses local pattern matching to classify worksheet problems by type.
Handles the common K-2 patterns without needing an LLM. Falls back
to UNKNOWN for ambiguous cases (which would route to Ollama/Anthropic
in production).
"""

import re
from enum import Enum

from hugo.layout.analyze import Problem


class ProblemType(Enum):
    """Known problem types Hugo can help with."""

    COUNTING = "counting"
    ADDITION = "addition"
    SUBTRACTION = "subtraction"
    SHAPES = "shapes"
    PATTERNS = "patterns"
    PHONICS = "phonics"
    SIGHT_WORDS = "sight_words"
    LETTER_RECOGNITION = "letter_recognition"
    COLORS = "colors"
    SEQUENCING = "sequencing"
    MATCHING = "matching"
    TRACING = "tracing"
    UNKNOWN = "unknown"


# ── Pattern rules (checked in order, first match wins) ──

_RULES: list[tuple[re.Pattern, ProblemType]] = [
    # Math: addition  "3 + 2 ="
    (re.compile(r"\d+\s*\+\s*\d+\s*=", re.IGNORECASE), ProblemType.ADDITION),
    # Math: subtraction  "6 - 2 ="  or  "6 − 2 ="
    (re.compile(r"\d+\s*[-−]\s*\d+\s*=", re.IGNORECASE), ProblemType.SUBTRACTION),
    # Reading: "circle the word"
    (re.compile(r"circle\s+the\s+word", re.IGNORECASE), ProblemType.SIGHT_WORDS),
    # Reading: "what sound does X make"
    (re.compile(r"what\s+sound\s+does", re.IGNORECASE), ProblemType.PHONICS),
    # Reading: "trace the letter"
    (re.compile(r"trace\s+the\s+letter", re.IGNORECASE), ProblemType.TRACING),
    # Shapes: "how many sides"
    (re.compile(r"how\s+many\s+sides", re.IGNORECASE), ProblemType.SHAPES),
    # Shapes: "how many corners"
    (re.compile(r"how\s+many\s+corners", re.IGNORECASE), ProblemType.SHAPES),
    # Patterns: "what comes next"
    (re.compile(r"what\s+comes\s+next", re.IGNORECASE), ProblemType.PATTERNS),
    # Matching: "match" or "draw a line"
    (re.compile(r"match\s+(the|each)\s+shape", re.IGNORECASE), ProblemType.MATCHING),
    (re.compile(r"draw\s+a\s+line\s+to\s+match", re.IGNORECASE), ProblemType.MATCHING),
    # Shapes: "color the circles/squares/triangles"
    (re.compile(r"color\s+the\s+(circle|square|triangle)", re.IGNORECASE), ProblemType.SHAPES),
    # Counting: "how many" (generic)
    (re.compile(r"how\s+many", re.IGNORECASE), ProblemType.COUNTING),
    # Counting: "count the"
    (re.compile(r"count\s+the", re.IGNORECASE), ProblemType.COUNTING),
]


def classify_problem(problem: Problem) -> ProblemType:
    """Classify a single worksheet problem by type.

    Uses local regex pattern matching. Returns ProblemType.UNKNOWN
    if no rule matches (would route to LLM in production).

    Args:
        problem: A Problem with extracted text.

    Returns:
        The detected ProblemType.
    """
    text = problem.text
    for pattern, ptype in _RULES:
        if pattern.search(text):
            return ptype
    return ProblemType.UNKNOWN
