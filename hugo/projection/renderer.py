"""Render help frames for projection onto the worksheet.

Generates visual overlays (icons, arrows, animations, color cues)
aligned to problem positions on the physical page. In dev mode,
renders to a desktop window instead of HDMI out.
"""

from PIL import Image


def render_frame(
    hints: list,
    page_size: tuple[int, int],
    dev_mode: bool = True,
) -> Image.Image:
    """Render a frame with visual hints overlaid on the worksheet area.

    Args:
        hints: List of Hint objects from helper modules.
        page_size: (width, height) of the worksheet in pixels.
        dev_mode: If True, renders to a PIL Image for display in
                  a desktop window. If False, targets HDMI output.

    Returns:
        A PIL Image of the rendered overlay frame.
    """
    raise NotImplementedError


def show_frame(frame: Image.Image) -> None:
    """Display a rendered frame.

    In dev mode, opens a desktop window. On the Pi, pushes to
    the HDMI-connected projector.
    """
    raise NotImplementedError
