"""Projected help buttons — rendered into the worksheet margin.

Each detected problem gets a small help icon projected into the
left margin beside its first line. The icon serves as both a
visual affordance ("press here for help") and a detection target
(the camera watches for occlusion at known pixel coordinates).
"""

from dataclasses import dataclass

from PIL import Image

from hugo.layout.analyze import Problem


@dataclass
class HelpButton:
    """A projected help-button target on the worksheet."""

    problem_id: int
    # Center of the button in worksheet pixel coordinates
    cx: int
    cy: int
    # Radius in pixels (base size when idle)
    radius: int = 18
    # Current visual state
    state: str = "idle"  # "idle" | "hover" | "pressing" | "triggered"
    # 0.0–1.0 progress toward trigger while pressing
    press_progress: float = 0.0


def create_help_buttons(
    problems: list[Problem],
    margin_x: int = 30,
) -> list[HelpButton]:
    """Create a help button for each problem, positioned in the left margin.

    Args:
        problems: Detected problems with bounding boxes.
        margin_x: X coordinate for button centers (in the margin area).

    Returns:
        One HelpButton per problem, vertically aligned to each
        problem's first line.
    """
    buttons = []
    for p in problems:
        # Place button vertically centered on the problem's top edge
        x, y, _w, _h = p.bbox
        btn_cy = y + 14  # slightly below the top of the problem bbox
        buttons.append(HelpButton(problem_id=p.id, cx=margin_x, cy=btn_cy))
    return buttons


def render_help_button(button: HelpButton) -> dict:
    """Return rendering instructions for a single help button.

    The projection module uses these to draw the button. The icon
    expands smoothly from base radius as press_progress increases,
    giving visual feedback that a press is being registered.

    Returns:
        Dict with keys: cx, cy, radius, color, opacity, icon.
    """
    base = button.radius
    if button.state == "idle":
        return {
            "cx": button.cx,
            "cy": button.cy,
            "radius": base,
            "color": "#00cfff",  # cyan — visible on projector
            "opacity": 0.7,
            "icon": "?",
        }
    elif button.state == "hover":
        return {
            "cx": button.cx,
            "cy": button.cy,
            "radius": base + 2,
            "color": "#00e660",  # green — finger detected nearby
            "opacity": 0.85,
            "icon": "?",
        }
    elif button.state == "pressing":
        # Expand from base to 2x as progress goes 0→1
        expanded = base + int(base * button.press_progress)
        return {
            "cx": button.cx,
            "cy": button.cy,
            "radius": expanded,
            "color": "#ffe600",  # yellow — actively pressing
            "opacity": 0.9,
            "icon": "?",
        }
    else:  # triggered
        return {
            "cx": button.cx,
            "cy": button.cy,
            "radius": base * 2,
            "color": "#00e660",  # green — success
            "opacity": 1.0,
            "icon": "✓",
        }
