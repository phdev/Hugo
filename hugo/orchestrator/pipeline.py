"""Main pipeline tying all Hugo modules together.

Capture → Vision → OCR → Layout → Classifier → Helpers → Projection.

In dev mode (source is a file path), runs the full pipeline on a
static image and saves/displays the overlay result. On the Pi,
would run a continuous loop with live camera capture.
"""

from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image

from hugo.capture.camera import capture_frame
from hugo.classifier.classify import ProblemType, classify_problem
from hugo.helpers import generate_hint
from hugo.helpers.hint import Hint
from hugo.layout.analyze import Problem, WorksheetLayout, analyze_layout
from hugo.ocr.extract import OcrResult, extract_lines
from hugo.projection.renderer import render_frame, render_overlay, show_frame
from hugo.vision.preprocess import preprocess


@dataclass
class PipelineResult:
    """Result of a single pipeline run."""

    worksheet: Image.Image
    processed: Image.Image
    ocr_lines: list[OcrResult]
    layout: WorksheetLayout
    classifications: dict[int, ProblemType]
    hints: list[Hint]
    overlay: Image.Image

    @property
    def problems(self) -> list[Problem]:
        return self.layout.problems

    def summary(self) -> str:
        """Human-readable summary of what was detected."""
        lines = [
            f"Worksheet: {self.worksheet.size[0]}x{self.worksheet.size[1]}",
            f"OCR lines: {len(self.ocr_lines)}",
            f"Problems detected: {len(self.problems)}",
            "",
        ]
        for p in self.problems:
            ptype = self.classifications.get(p.id, ProblemType.UNKNOWN)
            hint = next((h for h in self.hints if h.problem_id == p.id), None)
            hint_desc = f"{hint.hint_type}: \"{hint.label}\"" if hint else "none"
            lines.append(f"  #{p.id} [{ptype.value}] \"{p.text}\"")
            lines.append(f"       → {hint_desc}")
        return "\n".join(lines)


def run_once(source: str | Path | None = None) -> PipelineResult:
    """Run a single iteration of the Hugo pipeline.

    Args:
        source: Path to a worksheet image for dev/testing.
                If None, captures from the live camera.

    Returns:
        PipelineResult with all intermediate and final outputs.
    """
    # 1. Capture
    worksheet = capture_frame(source)

    # 2. Preprocess
    processed = preprocess(worksheet)

    # 3. OCR
    ocr_lines = extract_lines(processed)

    # 4. Layout analysis
    layout = analyze_layout(ocr_lines, worksheet.size)

    # 5. Classify + 6. Generate hints
    classifications: dict[int, ProblemType] = {}
    hints: list[Hint] = []
    positions: dict[int, tuple[int, int, int, int]] = {}

    for problem in layout.problems:
        ptype = classify_problem(problem)
        classifications[problem.id] = ptype
        hint = generate_hint(problem, ptype)
        hints.append(hint)
        positions[problem.id] = problem.bbox

    # 7. Render
    overlay = render_overlay(worksheet, hints, positions)

    return PipelineResult(
        worksheet=worksheet,
        processed=processed,
        ocr_lines=ocr_lines,
        layout=layout,
        classifications=classifications,
        hints=hints,
        overlay=overlay,
    )


def run_loop(source: str | Path | None = None) -> None:
    """Run the Hugo pipeline in a continuous loop.

    In dev mode with a source file, runs once and displays result.
    On the Pi with live camera, would loop continuously.

    Args:
        source: Path to a worksheet image for dev/testing.
                If None, captures from the live camera.
    """
    if source is not None:
        result = run_once(source)
        print(result.summary())
        show_frame(result.overlay)
        return

    # Live camera loop — requires Pi hardware
    raise NotImplementedError(
        "Live camera loop requires Pi hardware. "
        "Use --image <path> for dev mode."
    )
