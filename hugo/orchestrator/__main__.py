"""Entry point: python -m hugo.orchestrator --image <path>"""

import argparse
import sys
from pathlib import Path

from hugo.orchestrator.pipeline import run_once


def main() -> None:
    parser = argparse.ArgumentParser(description="Hugo dev pipeline")
    parser.add_argument("--image", "-i", type=Path, required=True,
                        help="Path to a worksheet image")
    args = parser.parse_args()

    if not args.image.exists():
        print(f"Error: {args.image} does not exist")
        sys.exit(1)

    result = run_once(args.image)
    print(result.summary())


if __name__ == "__main__":
    main()
