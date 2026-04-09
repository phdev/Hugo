"""Pi-side orchestrator — main event loop on the Raspberry Pi 5.

Startup:
1. Camera init
2. ToF calibration (~2s)
3. Voice mic open
4. Renderer init (PyGame fullscreen)
5. Initial desk scan → analyze homework → cache results

Event loop:
- Camera re-scan every 30s (or on "scan" voice command)
- Voice: continuous wake word listening
- ToF: 15Hz tap polling
- Tap or voice → lookup problem → show cached hint → render

Run: python3 -m hugo.pi.orchestrator
"""

import argparse
import logging
import sys
import time
from pathlib import Path

from hugo.pi.camera import analyze_homework, capture_frame
from hugo.pi.config import DESK_SCAN_INTERVAL_SEC, SERVER_BASE_URL
from hugo.pi.renderer import RendererState, render_frame, show_frame
from hugo.pi.tof import TapEvent, ToFState, calibrate, load_zone_map, poll_once

logger = logging.getLogger(__name__)


def run_dev(image_path: Path, output_path: Path | None = None) -> None:
    """Dev mode: analyze a fixture image, render overlay, save to file."""
    logger.info("Dev mode: %s", image_path)

    # Capture
    frame = capture_frame(source=image_path)

    # Analyze via server (or local pipeline fallback)
    homework = analyze_homework(frame)
    if not homework.get("problems"):
        # Server unreachable — run local pipeline
        logger.info("Server unreachable, running local pipeline")
        from hugo.server.inference_api import _analyze_image
        homework = _analyze_image(frame)

    # Render
    state = RendererState(problems=homework["problems"])
    overlay = render_frame(state)
    out = str(output_path or "/tmp/hugo_frame.png")
    show_frame(overlay, output_path=out)
    logger.info("Saved overlay to %s", out)

    # Print summary
    for p in homework["problems"]:
        hint = p.get("hint", {})
        print(f"  #{p['id']} [{p.get('type', '?')}] \"{p['text']}\"")
        print(f"       → {hint.get('hint_type', '?')}: \"{hint.get('label', '')}\"")


def run_live() -> None:
    """Live mode: full event loop with hardware.

    Requires Pi 5 with camera, ToF sensor, ReSpeaker HAT,
    and HDMI connected to Luma 350.
    """
    logger.info("Starting Hugo live mode...")

    # Init ToF
    tof_state = ToFState()
    tof_state.zone_map = load_zone_map()
    logger.info("Calibrating ToF sensor...")
    calibrate(tof_state)

    # Init renderer
    state = RendererState(status="thinking")
    overlay = render_frame(state)
    show_frame(overlay)

    # Initial desk scan
    logger.info("Scanning desk...")
    frame = capture_frame(full_res=True)
    homework = analyze_homework(frame)
    state.problems = homework.get("problems", [])
    state.status = "ready"
    overlay = render_frame(state)
    show_frame(overlay)
    logger.info("Found %d problems", len(state.problems))

    # Main loop
    last_scan = time.monotonic()
    try:
        while True:
            # ToF polling
            tap = poll_once(tof_state)
            if tap and tap.problem_id is not None:
                logger.info("Tap on problem %d", tap.problem_id)
                _handle_tap(tap, state)
                overlay = render_frame(state)
                show_frame(overlay)

            # Periodic re-scan
            if time.monotonic() - last_scan > DESK_SCAN_INTERVAL_SEC:
                frame = capture_frame(full_res=True)
                homework = analyze_homework(frame)
                state.problems = homework.get("problems", [])
                last_scan = time.monotonic()

            time.sleep(1.0 / 15)  # ~15Hz loop

    except KeyboardInterrupt:
        logger.info("Shutting down")


def _handle_tap(tap: TapEvent, state: RendererState) -> None:
    """Handle a tap event — toggle hint for the tapped problem."""
    if state.active_problem_id == tap.problem_id:
        # Dismiss
        state.active_problem_id = None
        state.active_hint = None
    else:
        # Activate
        state.active_problem_id = tap.problem_id
        prob = next(
            (p for p in state.problems if p.get("id") == tap.problem_id),
            None,
        )
        if prob and prob.get("hint"):
            from hugo.helpers.hint import Hint
            h = prob["hint"]
            state.active_hint = Hint(
                problem_id=tap.problem_id,
                hint_type=h.get("hint_type", "generic"),
                label=h.get("label", ""),
                content=h.get("content", {}),
            )


def main() -> None:
    """CLI entry point."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(description="Hugo Pi orchestrator")
    parser.add_argument("--image", "-i", type=Path, help="Dev mode: fixture image")
    parser.add_argument("--output", "-o", type=Path, help="Dev mode: output path")
    args = parser.parse_args()

    if args.image:
        run_dev(args.image, args.output)
    else:
        run_live()


if __name__ == "__main__":
    main()
