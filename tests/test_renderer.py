"""Tests for the projection renderer."""

from PIL import Image

from hugo.helpers.hint import COLORS, Hint
from hugo.projection.renderer import render_frame, render_overlay


def test_render_frame_creates_image():
    """render_frame returns an image of the correct size."""
    hints = [
        Hint(
            problem_id=1,
            hint_type="dot_count",
            label="count them all!",
            content={
                "groups": [
                    {"count": 3, "color": COLORS["orange"]},
                    {"count": 2, "color": COLORS["cyan"]},
                ],
                "operator": "+",
                "operator_color": COLORS["magenta"],
            },
        ),
    ]
    img = render_frame(hints, (640, 828))
    assert isinstance(img, Image.Image)
    assert img.size == (640, 828)


def test_render_frame_with_positions():
    """Hints render at specified problem positions."""
    hints = [
        Hint(problem_id=1, hint_type="generic", label="test",
             content={"color": COLORS["cyan"]}),
    ]
    positions = {1: (60, 100, 300, 30)}
    img = render_frame(hints, (640, 828), positions)
    assert img.size == (640, 828)


def test_render_all_hint_types():
    """Every hint type renders without errors."""
    all_hints = [
        Hint(problem_id=1, hint_type="dot_count", label="dots",
             content={"groups": [{"count": 3, "color": "#ff8800"}],
                       "operator": "+", "operator_color": "#ff2fa8"}),
        Hint(problem_id=2, hint_type="number_line", label="hop",
             content={"range": [0, 13], "start": 7, "end": 12,
                       "hops": 5, "direction": "forward",
                       "start_color": "#00e660", "hop_color": "#ff8800",
                       "end_color": "#ff8800"}),
        Hint(problem_id=3, hint_type="finger_count", label="fingers",
             content={"left_hand": 4, "right_hand": 4,
                       "operator_color": "#ff2fa8"}),
        Hint(problem_id=4, hint_type="phonics", label="sounds",
             content={"letter": "B", "letter_color": "#ff2fa8",
                       "words": [{"emoji": "x", "word": "Bear",
                                   "highlight": "B"}],
                       "arrow_color": "#ffe600"}),
        Hint(problem_id=5, hint_type="phonics_breakdown", label="split",
             content={"parts": [{"letter": "c", "sound": "cuh",
                                  "color": "#00cfff"}],
                       "word": "cat"}),
        Hint(problem_id=6, hint_type="trace", label="trace it",
             content={"letter": "S", "start_color": "#00e660",
                       "path_color": "#00cfff", "arrow_color": "#ff2fa8"}),
        Hint(problem_id=7, hint_type="generic", label="think!",
             content={"color": "#00cfff"}),
    ]
    img = render_frame(all_hints, (640, 828))
    assert img.size == (640, 828)


def test_render_overlay():
    """Overlay composites hints onto a worksheet image."""
    worksheet = Image.new("RGB", (640, 828), "white")
    hints = [
        Hint(problem_id=1, hint_type="generic", label="hello",
             content={"color": COLORS["cyan"]}),
    ]
    positions = {1: (60, 100, 300, 30)}
    result = render_overlay(worksheet, hints, positions)
    assert isinstance(result, Image.Image)
    assert result.size == (640, 828)


def test_render_empty_hints():
    """Empty hint list produces a blank image."""
    img = render_frame([], (640, 828))
    assert img.size == (640, 828)
