"""Math helper — generates visual hints for math problems.

Supports counting, addition, subtraction, shapes, and patterns.
Always scaffolds — never gives the answer directly.
"""

from dataclasses import dataclass

from hugo.classifier.classify import ProblemType
from hugo.layout.analyze import Problem


@dataclass
class Hint:
    """A visual hint to project onto the worksheet."""

    problem_id: int
    hint_type: str  # e.g. "number_line", "dot_count", "shape_highlight"
    content: dict  # rendering instructions for the projection module


def generate_math_hint(problem: Problem, problem_type: ProblemType) -> Hint:
    """Generate a visual hint for a math problem.

    Produces scaffolding like number lines, dot arrays, or shape
    outlines — never the answer itself.
    """
    raise NotImplementedError
