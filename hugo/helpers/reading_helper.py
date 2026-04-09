"""Reading helper — generates visual hints for reading problems.

Supports phonics, sight words, and letter recognition.
Always scaffolds — never gives the answer directly.
"""

from dataclasses import dataclass

from hugo.classifier.classify import ProblemType
from hugo.layout.analyze import Problem


@dataclass
class Hint:
    """A visual hint to project onto the worksheet."""

    problem_id: int
    hint_type: str  # e.g. "phonics_breakdown", "letter_trace"
    content: dict


def generate_reading_hint(problem: Problem, problem_type: ProblemType) -> Hint:
    """Generate a visual hint for a reading problem.

    Produces scaffolding like letter highlighting, phonics
    breakdowns, or word-picture associations.
    """
    raise NotImplementedError
