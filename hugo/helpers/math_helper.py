"""Math helper — generates visual hints for math problems.

Parses addition and subtraction expressions and produces visual
scaffolding: dot arrays, number lines, or finger counting.
Always hints, never answers.
"""

import re

from hugo.classifier.classify import ProblemType
from hugo.helpers.hint import COLORS, Hint
from hugo.layout.analyze import Problem


# Parse "3 + 2 = ___" or garbled variants like "54+3=__"
_ADD_RE = re.compile(r"(\d+)\s*\+\s*(\d+)")
_SUB_RE = re.compile(r"(\d+)\s*[-−]\s*(\d+)")


def _parse_operands(text: str, problem_type: ProblemType) -> tuple[int, int] | None:
    """Extract (a, b) operands from the problem text."""
    if problem_type == ProblemType.ADDITION:
        m = _ADD_RE.search(text)
    elif problem_type == ProblemType.SUBTRACTION:
        m = _SUB_RE.search(text)
    else:
        return None
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


def _dot_count_hint(problem_id: int, a: int, b: int, op: str) -> Hint:
    """Dot array: show groups of dots for each operand.

    Addition: two groups side by side, different colors.
    Subtraction: one group with some dots crossed out.
    """
    if op == "+":
        return Hint(
            problem_id=problem_id,
            hint_type="dot_count",
            label=f"count them all!",
            content={
                "groups": [
                    {"count": a, "color": COLORS["orange"]},
                    {"count": b, "color": COLORS["cyan"]},
                ],
                "operator": "+",
                "operator_color": COLORS["magenta"],
            },
        )
    else:  # subtraction
        return Hint(
            problem_id=problem_id,
            hint_type="dot_count",
            label=f"start with {a}, cross out {b}!",
            content={
                "groups": [
                    {"count": a - b, "color": COLORS["orange"]},
                    {"count": b, "color": COLORS["red"], "crossed": True},
                ],
                "operator": "−",
                "operator_color": COLORS["magenta"],
            },
        )


def _number_line_hint(problem_id: int, a: int, b: int, op: str) -> Hint:
    """Number line with hop arcs from start to result.

    Addition: start at a, hop forward b times.
    Subtraction: start at a, hop backward b times.
    """
    if op == "+":
        end = a + b
        max_val = end + 1
        direction = "forward"
        hop_color = COLORS["orange"]
        label = f"start at {a}, hop {b}!"
    else:
        end = a - b
        max_val = a + 1
        direction = "backward"
        hop_color = COLORS["magenta"]
        label = f"start at {a}, hop back {b}!"

    return Hint(
        problem_id=problem_id,
        hint_type="number_line",
        label=label,
        content={
            "range": [0, max(max_val, 13)],
            "start": a,
            "end": end,
            "hops": b,
            "direction": direction,
            "start_color": COLORS["green"],
            "hop_color": hop_color,
            "end_color": hop_color,
        },
    )


def _finger_count_hint(problem_id: int, a: int, b: int) -> Hint:
    """Finger counting: show fingers for each operand."""
    return Hint(
        problem_id=problem_id,
        hint_type="finger_count",
        label=f"{a} fingers + {b} fingers!",
        content={
            "left_hand": min(a, 5),
            "right_hand": min(b, 5),
            "operator_color": COLORS["magenta"],
        },
    )


def generate_math_hint(problem: Problem, problem_type: ProblemType) -> Hint:
    """Generate a visual hint for a math problem.

    Strategy selection:
    - Small operands (both ≤ 5): dot counting (most concrete)
    - Medium operands or result > 10: number line (visual counting)
    - Both operands ≤ 5 and addition: finger counting (alternate)

    Falls back to number line for any parsed math expression.
    """
    operands = _parse_operands(problem.text, problem_type)

    if operands is None:
        # Can't parse — generic hint
        return Hint(
            problem_id=problem.id,
            hint_type="generic",
            label="try counting!",
            content={"color": COLORS["cyan"]},
        )

    a, b = operands
    op = "+" if problem_type == ProblemType.ADDITION else "−"

    if problem_type == ProblemType.SUBTRACTION:
        # Subtraction: dot crossing for small numbers, number line for larger
        if a <= 10:
            return _dot_count_hint(problem.id, a, b, "-")
        return _number_line_hint(problem.id, a, b, "-")

    # Addition
    if a <= 5 and b <= 5:
        # Small: dot counting
        return _dot_count_hint(problem.id, a, b, "+")

    if a + b <= 20:
        # Medium: number line
        return _number_line_hint(problem.id, a, b, "+")

    # Fallback: number line works for everything
    return _number_line_hint(problem.id, a, b, "+")
