"""Entry point for running Hugo via `python -m hugo.orchestrator`.

Usage:
    python -m hugo.orchestrator --image tests/fixtures/math_worksheet.png
    python -m hugo.orchestrator --image worksheet.png --output result.png
"""

import argparse
import sys
from pathlib import Path

from hugo.orchestrator.pipeline import run_once


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Hugo — homework helping projector box",
    )
    parser.add_argument(
        "--image", "-i",
        type=Path,
        help="Path to a worksheet image (dev mode)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Save overlay result to this path (default: /tmp/hugo_frame.png)",
    )

    args = parser.parse_args()

    if args.image is None:
        parser.print_help()
        print("\nError: --image is required for dev mode (no Pi camera available)")
        sys.exit(1)

    if not args.image.exists():
        print(f"Error: {args.image} does not exist")
        sys.exit(1)

    result = run_once(args.image)
    print(result.summary())

    output = args.output or Path("/tmp/hugo_frame.png")
    result.overlay.save(output)
    print(f"\nOverlay saved to {output}")


if __name__ == "__main__":
    main()
