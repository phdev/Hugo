"""Generate synthetic worksheet images for testing.

Creates clean, consistent worksheet images with known content
so we can validate the full pipeline (vision → OCR → layout →
classifier) against ground truth.
"""

from PIL import Image, ImageDraw, ImageFont


def _get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Try to load a clean font, fall back to default."""
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _get_bold_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return _get_font(size)


def generate_math_worksheet(
    problems: list[str] | None = None,
    width: int = 640,
    height: int = 828,
) -> tuple[Image.Image, list[dict]]:
    """Generate a math worksheet image with known problems.

    Args:
        problems: List of problem strings like "3 + 2 = ___".
                  If None, uses a default set.
        width: Image width in pixels.
        height: Image height in pixels.

    Returns:
        (image, ground_truth) where ground_truth is a list of dicts
        with keys: id, text, y_top, y_bottom.
    """
    if problems is None:
        problems = [
            "3 + 2 = ___",
            "5 + 3 = ___",
            "7 + 5 = ___",
            "4 + 4 = ___",
            "6 - 2 = ___",
            "9 - 4 = ___",
            "2 + 6 = ___",
            "10 - 3 = ___",
        ]

    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    title_font = _get_bold_font(32)
    meta_font = _get_font(16)
    problem_font = _get_font(28)
    num_font = _get_font(28)

    # Title
    draw.text((width // 2, 25), "Math Practice", anchor="mt",
              fill="black", font=title_font)

    # Name / Date
    draw.text((60, 65), "Name: ________________", fill="#666",
              font=meta_font)
    draw.text((400, 65), "Date: ________", fill="#666", font=meta_font)

    # Divider
    draw.line([(40, 92), (width - 40, 92)], fill="black", width=2)

    # Red margin line
    draw.line([(52, 0), (52, height)], fill="#e8a0a0", width=1)

    # Problems — draw number and expression separately with clear gap
    ground_truth = []
    y = 110
    line_height = (height - 130) // len(problems)

    for i, text in enumerate(problems):
        y_top = y
        # Draw problem number and expression with wide gap
        num_str = f"{i + 1}."
        draw.text((65, y), num_str, fill="#333", font=num_font)
        draw.text((140, y), text, fill="#333", font=problem_font)
        y_bottom = y + 34
        ground_truth.append({
            "id": i + 1,
            "text": text,
            "y_top": y_top,
            "y_bottom": y_bottom,
        })

        # Faint ruled line
        rule_y = y + line_height - 2
        draw.line([(40, rule_y), (width - 40, rule_y)], fill="#d4e4f7",
                  width=1)
        y += line_height

    return img, ground_truth


def generate_reading_worksheet(
    width: int = 640,
    height: int = 828,
) -> tuple[Image.Image, list[dict]]:
    """Generate a reading worksheet image."""
    problems = [
        "What sound does B make? ___",
        "What sound does M make? ___",
        "Circle the word: cat",
        "Circle the word: sun",
        "What sound does D make? ___",
    ]

    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    title_font = _get_bold_font(32)
    meta_font = _get_font(16)
    problem_font = _get_font(26)
    num_font = _get_font(26)

    draw.text((width // 2, 25), "Letter Sounds", anchor="mt",
              fill="black", font=title_font)
    draw.text((60, 65), "Name: ________________", fill="#666",
              font=meta_font)
    draw.text((400, 65), "Date: ________", fill="#666", font=meta_font)
    draw.line([(40, 92), (width - 40, 92)], fill="black", width=2)
    draw.line([(52, 0), (52, height)], fill="#e8a0a0", width=1)

    ground_truth = []
    y = 110
    line_height = (height - 130) // len(problems)

    for i, text in enumerate(problems):
        y_top = y
        num_str = f"{i + 1}."
        draw.text((65, y), num_str, fill="#333", font=num_font)
        draw.text((115, y), text, fill="#333", font=problem_font)
        y_bottom = y + 32
        ground_truth.append({
            "id": i + 1,
            "text": text,
            "y_top": y_top,
            "y_bottom": y_bottom,
        })
        rule_y = y + line_height - 2
        draw.line([(40, rule_y), (width - 40, rule_y)], fill="#d4e4f7",
                  width=1)
        y += line_height

    return img, ground_truth


if __name__ == "__main__":
    import sys
    from pathlib import Path

    out = Path("tests/fixtures")
    out.mkdir(parents=True, exist_ok=True)

    img, gt = generate_math_worksheet()
    img.save(out / "math_worksheet.png")
    print(f"Saved math worksheet with {len(gt)} problems")

    img, gt = generate_reading_worksheet()
    img.save(out / "reading_worksheet.png")
    print(f"Saved reading worksheet with {len(gt)} problems")
