"""PyGame full-screen HDMI renderer for Pi 5 → Luma 350.

Renders overlay frames directly to the HDMI-connected projector.
No AirPlay, no network hop — ~80ms from event to pixels.

Overlay layers:
1. Transparent background (desk visible through projector)
2. Help buttons beside each problem ("?" icons)
3. Active help: hint visualization
4. Status indicators (listening, thinking, ready)
5. Debug: ToF 8×8 heatmap (toggle)
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from hugo.helpers.hint import COLORS, Hint
from hugo.pi.config import DISPLAY_HEIGHT, DISPLAY_WIDTH

logger = logging.getLogger(__name__)

# ── Projector neon palette ──
BG_COLOR = (0, 0, 0)  # black = transparent on projector


@dataclass
class RendererState:
    """Current display state."""

    problems: list[dict] = field(default_factory=list)
    active_problem_id: int | None = None
    active_hint: Hint | None = None
    status: str = "ready"  # ready, listening, thinking
    show_debug: bool = False
    tof_grid: list[list[int]] | None = None


def _font(size: int):
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _bold(size: int):
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return _font(size)


def render_frame(state: RendererState) -> Image.Image:
    """Render the current overlay frame.

    Returns a PIL Image (854×480) with black background.
    Black pixels are transparent when projected.
    """
    img = Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Help buttons for each problem
    for prob in state.problems:
        pid = prob.get("id", 0)
        bbox = prob.get("bbox", [0, 0, 100, 30])

        # Scale bbox from worksheet coords to display coords
        bx, by, bw, bh = bbox
        # Draw "?" button in the margin
        btn_x = max(bx - 30, 5)
        btn_y = by + bh // 2

        if state.active_problem_id == pid:
            # Active — green checkmark
            color = COLORS["green"]
            draw.ellipse(
                [btn_x - 12, btn_y - 12, btn_x + 12, btn_y + 12],
                fill=color,
            )
            draw.text((btn_x - 5, btn_y - 8), "✓", fill="white", font=_bold(14))
        else:
            # Idle — cyan question mark
            color = COLORS["cyan"]
            draw.ellipse(
                [btn_x - 10, btn_y - 10, btn_x + 10, btn_y + 10],
                fill=color,
            )
            draw.text((btn_x - 4, btn_y - 7), "?", fill="white", font=_bold(12))

    # Active hint
    if state.active_hint and state.active_problem_id is not None:
        _draw_hint(draw, state.active_hint, state.problems)

    # Status indicator (top-right corner)
    if state.status == "listening":
        draw.ellipse([DISPLAY_WIDTH - 25, 5, DISPLAY_WIDTH - 5, 25],
                      fill=COLORS["green"])
    elif state.status == "thinking":
        draw.ellipse([DISPLAY_WIDTH - 25, 5, DISPLAY_WIDTH - 5, 25],
                      fill=COLORS["yellow"])

    # Debug: ToF heatmap
    if state.show_debug and state.tof_grid:
        _draw_tof_debug(draw, state.tof_grid)

    return img


def _draw_hint(draw: ImageDraw.ImageDraw, hint: Hint, problems: list[dict]) -> None:
    """Draw the active hint below its problem."""
    # Find the problem's bbox
    prob = next((p for p in problems if p.get("id") == hint.problem_id), None)
    if not prob:
        return

    bbox = prob.get("bbox", [0, 0, 100, 30])
    x = bbox[0]
    y = bbox[1] + bbox[3] + 5

    # Label
    draw.text((x, y), hint.label, fill=COLORS["cyan"], font=_bold(14))


def _draw_tof_debug(draw: ImageDraw.ImageDraw, grid: list[list[int]]) -> None:
    """Draw 8×8 ToF heatmap in bottom-right corner."""
    ox, oy = DISPLAY_WIDTH - 90, DISPLAY_HEIGHT - 90
    cell = 10
    for r in range(8):
        for c in range(8):
            dist = grid[r][c] if r < len(grid) and c < len(grid[r]) else 0
            # Color: closer = brighter green
            intensity = max(0, min(255, 255 - dist // 2))
            color = (0, intensity, 0)
            draw.rectangle(
                [ox + c * cell, oy + r * cell,
                 ox + (c + 1) * cell - 1, oy + (r + 1) * cell - 1],
                fill=color,
            )


def show_frame(frame: Image.Image, output_path: str | None = None) -> None:
    """Display a frame on the HDMI-connected projector.

    Uses PyGame for full-screen display. In dev mode (no display),
    saves to a file instead.

    Args:
        frame: PIL Image to display.
        output_path: If set, save to file instead of PyGame display.
    """
    if output_path:
        frame.save(output_path)
        return

    try:
        import pygame
        if not pygame.get_init():
            pygame.init()
            pygame.display.set_mode(
                (DISPLAY_WIDTH, DISPLAY_HEIGHT),
                pygame.FULLSCREEN | pygame.NOFRAME,
            )

        surface = pygame.display.get_surface()
        mode = frame.mode
        size = frame.size
        data = frame.tobytes()
        pg_image = pygame.image.fromstring(data, size, mode)
        surface.blit(pg_image, (0, 0))
        pygame.display.flip()
    except ImportError:
        # No PyGame — save to file as fallback
        frame.save(output_path or "/tmp/hugo_frame.png")
