"""Shared Hint dataclass for all helper modules.

Defines the rendering instructions that the projection module
uses to draw visual scaffolding onto the worksheet.
"""

from dataclasses import dataclass, field


@dataclass
class Hint:
    """A visual hint to project onto the worksheet.

    Attributes:
        problem_id: Which problem this hint is for.
        hint_type: The visualization strategy — determines how
                   the projection module renders it.
        label: Short text label projected near the hint.
        content: Rendering instructions (type-specific dict).
        bbox: Where on the worksheet to project, in pixels.
               (x, y, width, height). If None, uses the
               problem's work-area below its bounding box.
    """

    problem_id: int
    hint_type: str
    label: str
    content: dict = field(default_factory=dict)
    bbox: tuple[int, int, int, int] | None = None


# ── Projector color palette (Kodak Luma 150) ──
# High-saturation, high-luminance colors that show on a
# low-lumen pico projector adding light to white paper.

COLORS = {
    "green":   "#00e660",
    "cyan":    "#00cfff",
    "magenta": "#ff2fa8",
    "orange":  "#ff8800",
    "yellow":  "#ffe600",
    "red":     "#ff3333",
}
