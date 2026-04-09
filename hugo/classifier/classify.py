"""Problem type classifier.

Examines extracted text and layout to determine problem type
and route to the correct helper module.
"""

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
    UNKNOWN = "unknown"


def classify_problem(problem: Problem) -> ProblemType:
    """Classify a single worksheet problem by type.

    Uses local pattern matching first. Falls back to LLM-based
    classification for ambiguous cases.
    """
    raise NotImplementedError
