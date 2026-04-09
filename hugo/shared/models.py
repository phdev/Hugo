"""Shared data models for Pi ↔ server communication."""

from dataclasses import dataclass, field


@dataclass
class HomeworkProblem:
    """A problem detected on the worksheet."""

    id: int
    text: str
    type: str  # ProblemType.value
    bbox: list[int]  # [x, y, w, h]
    hint: dict = field(default_factory=dict)


@dataclass
class HomeworkResult:
    """Full homework analysis result."""

    problems: list[HomeworkProblem] = field(default_factory=list)
    title: str = ""


@dataclass
class TranscriptionResult:
    """Speech-to-text result."""

    text: str
    error: str = ""
