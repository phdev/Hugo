"""Voice command parsing for kid-friendly spoken requests.

Parses transcribed speech into structured commands:
- "help me with number three"
- "next one"
- "what's this one?"
- "go away" / "hide" (dismiss hint)
- "read it to me"

Uses local keyword matching. Designed for 4-7 year olds —
tolerant of partial sentences and mispronunciations.
"""

import re
from dataclasses import dataclass
from enum import Enum


class CommandType(Enum):
    """Recognized voice commands."""

    HELP_WITH_NUMBER = "help_with_number"
    NEXT = "next"
    PREVIOUS = "previous"
    DISMISS = "dismiss"
    READ_PROBLEM = "read_problem"
    UNKNOWN = "unknown"


@dataclass
class VoiceCommand:
    """A parsed voice command."""

    command: CommandType
    problem_number: int | None = None
    raw_text: str = ""
    confidence: float = 0.0


_NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
    "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
}

_HELP_RE = re.compile(
    r"(?:help|hint|show)\s+(?:me\s+)?(?:with\s+)?(?:number\s+|problem\s+)?(\w+)",
    re.IGNORECASE,
)
_NEXT_RE = re.compile(r"(?:next|skip|forward)", re.IGNORECASE)
_PREV_RE = re.compile(r"(?:back|previous|before)", re.IGNORECASE)
_DISMISS_RE = re.compile(r"(?:go\s+away|hide|dismiss|done|stop|bye)", re.IGNORECASE)
_READ_RE = re.compile(r"(?:read|say|tell)\s+(?:it|me|this)", re.IGNORECASE)


def parse_command(text: str) -> VoiceCommand:
    """Parse transcribed speech into a VoiceCommand."""
    text = text.strip()
    if not text:
        return VoiceCommand(command=CommandType.UNKNOWN, raw_text=text)

    m = _HELP_RE.search(text)
    if m:
        num_word = m.group(1).lower()
        num = _NUMBER_WORDS.get(num_word)
        if num is not None:
            return VoiceCommand(
                command=CommandType.HELP_WITH_NUMBER,
                problem_number=num, raw_text=text, confidence=0.9,
            )
        return VoiceCommand(
            command=CommandType.HELP_WITH_NUMBER,
            raw_text=text, confidence=0.5,
        )

    if _DISMISS_RE.search(text):
        return VoiceCommand(command=CommandType.DISMISS, raw_text=text, confidence=0.9)

    if _READ_RE.search(text):
        return VoiceCommand(command=CommandType.READ_PROBLEM, raw_text=text, confidence=0.9)

    if _NEXT_RE.search(text):
        return VoiceCommand(command=CommandType.NEXT, raw_text=text, confidence=0.9)

    if _PREV_RE.search(text):
        return VoiceCommand(command=CommandType.PREVIOUS, raw_text=text, confidence=0.9)

    return VoiceCommand(command=CommandType.UNKNOWN, raw_text=text, confidence=0.0)
