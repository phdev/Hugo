"""Render help frames for projection onto the worksheet.

Generates visual overlays using PIL/Pillow — draws dots, number
lines, phonics breakdowns, etc. onto a transparent image that
represents what the projector casts onto the paper.

In dev mode, renders onto a white background for desktop viewing.
On the Pi, the overlay would composite onto the HDMI output
with a black (transparent-to-projector) background.
"""

import math

from PIL import Image, ImageDraw, ImageFont

from hugo.helpers.hint import COLORS, Hint

# ── Fonts ──

def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _bold(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return _font(size)


# ── Individual hint renderers ──

def _render_dot_count(
    draw: ImageDraw.ImageDraw,
    hint: Hint,
    x: int,
    y: int,
    max_width: int,
) -> int:
    """Draw dot groups for addition/subtraction. Returns height used."""
    groups = hint.content.get("groups", [])
    op = hint.content.get("operator", "+")
    op_color = hint.content.get("operator_color", COLORS["magenta"])

    dot_r = 10
    gap = 6
    cx = x + 10
    cy = y + dot_r + 4

    for gi, group in enumerate(groups):
        count = group["count"]
        color = group["color"]
        crossed = group.get("crossed", False)

        for i in range(count):
            draw.ellipse(
                [cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r],
                fill=color,
            )
            if crossed:
                # Draw X over the dot
                draw.line(
                    [cx - 6, cy - 6, cx + 6, cy + 6],
                    fill=COLORS["red"], width=3,
                )
                draw.line(
                    [cx + 6, cy - 6, cx - 6, cy + 6],
                    fill=COLORS["red"], width=3,
                )
            cx += dot_r * 2 + gap

        # Draw operator between groups (not after last)
        if gi < len(groups) - 1:
            cx += 4
            draw.text(
                (cx, cy - 10), op,
                fill=op_color, font=_bold(20),
            )
            cx += 20

    # Label below
    label_y = cy + dot_r + 8
    draw.text((x + 10, label_y), hint.label, fill=COLORS["cyan"], font=_font(14))
    return label_y - y + 20


def _render_number_line(
    draw: ImageDraw.ImageDraw,
    hint: Hint,
    x: int,
    y: int,
    max_width: int,
) -> int:
    """Draw a number line with hop arcs. Returns height used."""
    content = hint.content
    nl_range = content.get("range", [0, 13])
    start = content["start"]
    end = content["end"]
    hops = content["hops"]
    direction = content["direction"]
    start_color = content["start_color"]
    hop_color = content["hop_color"]

    lo, hi = nl_range
    num_marks = min(hi - lo, 20)  # cap at 20 marks
    if num_marks <= 0:
        num_marks = 13

    line_y = y + 30
    line_x0 = x + 15
    line_x1 = x + max_width - 15
    line_len = line_x1 - line_x0
    step = line_len / num_marks

    # Base line
    draw.line([(line_x0, line_y), (line_x1, line_y)], fill="#cccccc", width=2)

    # Tick marks and numbers
    small_font = _font(10)
    for i in range(num_marks + 1):
        tx = line_x0 + i * step
        val = lo + i
        draw.line([(tx, line_y - 4), (tx, line_y + 4)], fill="#cccccc", width=1)

        # Highlight start and end
        if val == start:
            draw.ellipse(
                [tx - 5, line_y - 5, tx + 5, line_y + 5],
                fill=start_color,
            )
            draw.text((tx - 3, line_y + 8), str(val),
                       fill=start_color, font=_bold(11))
        elif val == end:
            draw.ellipse(
                [tx - 5, line_y - 5, tx + 5, line_y + 5],
                fill=hop_color,
            )
            draw.text((tx - 3, line_y + 8), str(val),
                       fill=hop_color, font=_bold(11))
        else:
            draw.text((tx - 3, line_y + 8), str(val),
                       fill="#bbbbbb", font=small_font)

    # Hop arcs
    for h in range(hops):
        if direction == "forward":
            from_val = start + h
            to_val = start + h + 1
        else:
            from_val = start - h
            to_val = start - h - 1

        from_x = line_x0 + (from_val - lo) * step
        to_x = line_x0 + (to_val - lo) * step
        mid_x = (from_x + to_x) / 2
        arc_top = line_y - 16

        # Draw arc as a series of line segments
        points = []
        for t in range(11):
            frac = t / 10
            px = from_x + (to_x - from_x) * frac
            py = line_y + (arc_top - line_y) * math.sin(frac * math.pi)
            points.append((px, py))
        if len(points) >= 2:
            draw.line(points, fill=hop_color, width=3)

    # Label
    label_y = line_y + 24
    draw.text((x + 10, label_y), hint.label, fill=COLORS["cyan"], font=_font(14))
    return label_y - y + 20


def _render_finger_count(
    draw: ImageDraw.ImageDraw,
    hint: Hint,
    x: int,
    y: int,
    max_width: int,
) -> int:
    """Draw finger counting hint. Returns height used."""
    left = hint.content.get("left_hand", 0)
    right = hint.content.get("right_hand", 0)
    op_color = hint.content.get("operator_color", COLORS["magenta"])

    emoji_font = _font(22)
    cx = x + 10
    cy = y + 4

    # Left hand fingers
    for i in range(left):
        draw.text((cx, cy), "☝", font=emoji_font)
        cx += 22

    # Operator
    cx += 6
    draw.text((cx, cy), "+", fill=op_color, font=_bold(20))
    cx += 24

    # Right hand fingers
    for i in range(right):
        draw.text((cx, cy), "☝", font=emoji_font)
        cx += 22

    label_y = cy + 32
    draw.text((x + 10, label_y), hint.label, fill=COLORS["cyan"], font=_font(14))
    return label_y - y + 20


def _render_phonics(
    draw: ImageDraw.ImageDraw,
    hint: Hint,
    x: int,
    y: int,
    max_width: int,
) -> int:
    """Draw letter + word-picture associations. Returns height used."""
    content = hint.content
    letter = content["letter"]
    letter_color = content["letter_color"]
    words = content["words"]
    arrow_color = content["arrow_color"]

    # Big letter
    draw.text((x + 10, y), letter, fill=letter_color, font=_bold(36))

    # Arrow
    draw.text((x + 50, y + 8), "→", fill=arrow_color, font=_bold(20))

    # Word-picture list
    wx = x + 80
    for w in words:
        emoji = w["emoji"]
        word = w["word"]
        draw.text((wx, y + 2), emoji, font=_font(18))
        draw.text((wx + 22, y + 4), word, fill=COLORS["cyan"], font=_font(14))
        wx += 80

    label_y = y + 40
    draw.text((x + 10, label_y), hint.label, fill=COLORS["cyan"], font=_font(14))
    return label_y - y + 20


def _render_phonics_breakdown(
    draw: ImageDraw.ImageDraw,
    hint: Hint,
    x: int,
    y: int,
    max_width: int,
) -> int:
    """Draw phonics letter-by-letter breakdown. Returns height used."""
    parts = hint.content.get("parts", [])

    cx = x + 10
    cy = y + 4
    big_font = _bold(30)
    sep_font = _font(24)

    for i, part in enumerate(parts):
        color = part["color"]
        letter = part["letter"]
        draw.text((cx, cy), letter, fill=color, font=big_font)
        cx += 28
        if i < len(parts) - 1:
            draw.text((cx, cy + 2), "·", fill="#cccccc", font=sep_font)
            cx += 16

    label_y = cy + 38
    draw.text((x + 10, label_y), hint.label, fill=COLORS["cyan"], font=_font(14))
    return label_y - y + 20


def _render_trace(
    draw: ImageDraw.ImageDraw,
    hint: Hint,
    x: int,
    y: int,
    max_width: int,
) -> int:
    """Draw letter tracing guide. Returns height used."""
    content = hint.content
    letter = content["letter"]
    start_color = content["start_color"]
    path_color = content["path_color"]

    # Ghost letter
    draw.text((x + 20, y - 5), letter, fill="#e0e0e0", font=_bold(60))

    # Start dot
    draw.ellipse([x + 55, y + 2, x + 67, y + 14], fill=start_color)

    # Arrow indicator
    draw.text((x + 72, y + 2), "↓", fill=path_color, font=_bold(16))

    label_y = y + 58
    draw.text((x + 10, label_y), hint.label, fill=COLORS["cyan"], font=_font(14))
    return label_y - y + 20


def _render_generic(
    draw: ImageDraw.ImageDraw,
    hint: Hint,
    x: int,
    y: int,
    max_width: int,
) -> int:
    """Generic hint — just the label text."""
    color = hint.content.get("color", COLORS["cyan"])
    draw.text((x + 10, y + 4), hint.label, fill=color, font=_bold(16))
    return 30


# ── Renderer dispatch ──

_RENDERERS = {
    "dot_count": _render_dot_count,
    "number_line": _render_number_line,
    "finger_count": _render_finger_count,
    "phonics": _render_phonics,
    "phonics_breakdown": _render_phonics_breakdown,
    "trace": _render_trace,
    "generic": _render_generic,
}


def render_frame(
    hints: list[Hint],
    page_size: tuple[int, int],
    problem_positions: dict[int, tuple[int, int, int, int]] | None = None,
    dev_mode: bool = True,
) -> Image.Image:
    """Render a frame with visual hints.

    Args:
        hints: Hint objects from helper modules.
        page_size: (width, height) of the worksheet in pixels.
        problem_positions: Map of problem_id → (x, y, w, h) bounding
            box. Used to position each hint below its problem. If
            None, hints are stacked vertically.
        dev_mode: If True, renders on white background. If False,
            renders on black (projector-transparent).

    Returns:
        A PIL Image of the rendered overlay frame.
    """
    w, h = page_size
    bg = "white" if dev_mode else "black"
    img = Image.new("RGB", (w, h), bg)
    draw = ImageDraw.Draw(img)

    # Determine Y position for each hint
    y_cursor = 20

    for hint in hints:
        # Get position from problem bounding box
        if problem_positions and hint.problem_id in problem_positions:
            px, py, pw, ph = problem_positions[hint.problem_id]
            hx = px
            hy = py + ph + 4  # just below the problem
            max_w = pw
        else:
            hx = 10
            hy = y_cursor
            max_w = w - 20

        renderer = _RENDERERS.get(hint.hint_type, _render_generic)
        used_h = renderer(draw, hint, hx, hy, max_w)
        y_cursor = hy + used_h + 8

    return img


def render_overlay(
    worksheet: Image.Image,
    hints: list[Hint],
    problem_positions: dict[int, tuple[int, int, int, int]],
) -> Image.Image:
    """Render hints overlaid on a worksheet image for dev preview.

    Composites the hint overlay on top of the worksheet so you
    can see exactly what the projected result would look like.

    Args:
        worksheet: The original worksheet image.
        hints: Hint objects to render.
        problem_positions: Map of problem_id → bbox.

    Returns:
        Composite image (worksheet + hints).
    """
    overlay = render_frame(
        hints, worksheet.size, problem_positions, dev_mode=True,
    )

    # Composite: keep worksheet pixels where overlay is white
    result = worksheet.copy().convert("RGB")
    overlay_px = overlay.load()
    result_px = result.load()
    w, h = result.size

    for py in range(h):
        for px in range(w):
            r, g, b = overlay_px[px, py]
            # If the overlay pixel isn't white, it's a hint element
            if (r, g, b) != (255, 255, 255):
                result_px[px, py] = (r, g, b)

    return result


def show_frame(frame: Image.Image, output_path: str = "/tmp/hugo_frame.png") -> None:
    """Display a rendered frame.

    In dev mode, saves to a file. In production, the Mac mini
    displays the frame on its AirPlay-mirrored display which
    the Kodak Luma 350 receives wirelessly.

    For AirPlay: use macOS screen mirroring (System Settings →
    Displays → mirror to Luma 350). This function just needs to
    update the full-screen window on that mirrored display.
    """
    frame.save(output_path)
