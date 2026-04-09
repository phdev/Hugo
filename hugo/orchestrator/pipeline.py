"""Dev-mode pipeline — runs the full analysis locally.

For dev/testing on a laptop without Pi hardware. Loads a fixture
image, runs vision → OCR → layout → classify → hints, and saves
the overlay. Uses the same pipeline that the server exposes.
"""

from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image

from hugo.classifier.classify import ProblemType, classify_problem
from hugo.helpers import generate_hint
from hugo.helpers.hint import Hint
from hugo.layout.analyze import Problem, WorksheetLayout, analyze_layout
from hugo.ocr.extract import OcrResult, extract_lines
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

    @property
    def problems(self) -> list[Problem]:
        return self.layout.problems

    def summary(self) -> str:
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


def run_once(source: str | Path) -> PipelineResult:
    """Run the full pipeline on a fixture image.

    Args:
        source: Path to a worksheet image.

    Returns:
        PipelineResult with all intermediate outputs.
    """
    worksheet = Image.open(source)
    processed = preprocess(worksheet)
    ocr_lines = extract_lines(processed)
    layout = analyze_layout(ocr_lines, worksheet.size)

    classifications: dict[int, ProblemType] = {}
    hints: list[Hint] = []

    for problem in layout.problems:
        ptype = classify_problem(problem, use_llm=False)
        classifications[problem.id] = ptype
        hint = generate_hint(problem, ptype)
        hints.append(hint)

    return PipelineResult(
        worksheet=worksheet,
        processed=processed,
        ocr_lines=ocr_lines,
        layout=layout,
        classifications=classifications,
        hints=hints,
    )
