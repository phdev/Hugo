"""Helpers module — subject-specific hint generators.

Each helper produces age-appropriate, visual-first scaffolding
for a specific subject area. Helpers never give answers directly.
"""

from hugo.classifier.classify import ProblemType
from hugo.helpers.hint import Hint
from hugo.helpers.math_helper import generate_math_hint
from hugo.helpers.reading_helper import generate_reading_hint
from hugo.layout.analyze import Problem


# Which problem types route to which helper
_MATH_TYPES = {
    ProblemType.ADDITION,
    ProblemType.SUBTRACTION,
    ProblemType.COUNTING,
}

_READING_TYPES = {
    ProblemType.PHONICS,
    ProblemType.SIGHT_WORDS,
    ProblemType.LETTER_RECOGNITION,
    ProblemType.TRACING,
}


def generate_hint(problem: Problem, problem_type: ProblemType) -> Hint:
    """Route a classified problem to the correct helper.

    Args:
        problem: The detected problem with text and bbox.
        problem_type: The classified type.

    Returns:
        A Hint with rendering instructions for the projection module.
    """
    if problem_type in _MATH_TYPES:
        return generate_math_hint(problem, problem_type)

    if problem_type in _READING_TYPES:
        return generate_reading_hint(problem, problem_type)

    # Unhandled types get a generic hint
    return Hint(
        problem_id=problem.id,
        hint_type="generic",
        label="let's think about this!",
        content={},
    )
