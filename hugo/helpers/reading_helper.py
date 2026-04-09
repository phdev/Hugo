"""Reading helper — generates visual hints for reading problems.

Parses phonics, sight word, and tracing problems and produces
visual scaffolding. Always hints, never answers.
"""

import re

from hugo.classifier.classify import ProblemType
from hugo.helpers.hint import COLORS, Hint
from hugo.layout.analyze import Problem


# "What sound does B make?"
_PHONICS_RE = re.compile(r"what\s+sound\s+does\s+(\w)\s+make", re.IGNORECASE)

# "Circle the word: cat"
_SIGHT_WORD_RE = re.compile(r"circle\s+the\s+word:?\s+(\w+)", re.IGNORECASE)

# "Trace the letter: S"
_TRACE_RE = re.compile(r"trace\s+the\s+letter:?\s+(\w)", re.IGNORECASE)

# Common word-picture associations for phonics.
# Maps uppercase letter to list of (emoji, word) tuples.
_PHONICS_WORDS: dict[str, list[tuple[str, str]]] = {
    "A": [("🍎", "Apple"), ("🐜", "Ant"), ("✈️", "Airplane")],
    "B": [("🐻", "Bear"), ("🏀", "Ball"), ("🍌", "Banana")],
    "C": [("🐱", "Cat"), ("🚗", "Car"), ("🧁", "Cake")],
    "D": [("🐕", "Dog"), ("🚪", "Door"), ("🦆", "Duck")],
    "E": [("🥚", "Egg"), ("🐘", "Elephant"), ("👁️", "Eye")],
    "F": [("🐟", "Fish"), ("🦊", "Fox"), ("🔥", "Fire")],
    "G": [("🍇", "Grapes"), ("🎸", "Guitar"), ("🐐", "Goat")],
    "H": [("🏠", "House"), ("🐴", "Horse"), ("❤️", "Heart")],
    "I": [("🍦", "Ice cream"), ("🏝️", "Island"), ("🪱", "Inchworm")],
    "J": [("🧃", "Juice"), ("🤹", "Juggle"), ("👖", "Jeans")],
    "K": [("🪁", "Kite"), ("🔑", "Key"), ("👑", "King")],
    "L": [("🦁", "Lion"), ("🍋", "Lemon"), ("🍃", "Leaf")],
    "M": [("🌙", "Moon"), ("🐭", "Mouse"), ("🥛", "Milk")],
    "N": [("👃", "Nose"), ("🥜", "Nut"), ("🌙", "Night")],
    "O": [("🐙", "Octopus"), ("🍊", "Orange"), ("🦉", "Owl")],
    "P": [("🐷", "Pig"), ("🍕", "Pizza"), ("✏️", "Pencil")],
    "Q": [("👸", "Queen"), ("❓", "Question"), ("🦆", "Quack")],
    "R": [("🐰", "Rabbit"), ("🌈", "Rainbow"), ("🤖", "Robot")],
    "S": [("☀️", "Sun"), ("⭐", "Star"), ("🐍", "Snake")],
    "T": [("🐢", "Turtle"), ("🌳", "Tree"), ("🚂", "Train")],
    "U": [("☂️", "Umbrella"), ("🦄", "Unicorn"), ("👆", "Up")],
    "V": [("🎻", "Violin"), ("🌋", "Volcano"), ("💜", "Violet")],
    "W": [("🐋", "Whale"), ("💧", "Water"), ("🪱", "Worm")],
    "X": [("❌", "X-ray"), ("🎸", "Xylophone")],
    "Y": [("💛", "Yellow"), ("🧶", "Yarn"), ("😋", "Yummy")],
    "Z": [("🦓", "Zebra"), ("⚡", "Zap"), ("🤐", "Zip")],
}

# Simple phonetic breakdowns for common sight words
_PHONICS_BREAKDOWNS: dict[str, list[tuple[str, str]]] = {
    "cat": [("c", "cuh"), ("a", "aah"), ("t", "tuh")],
    "dog": [("d", "duh"), ("o", "ahh"), ("g", "guh")],
    "sun": [("s", "sss"), ("u", "uhh"), ("n", "nnn")],
    "bat": [("b", "buh"), ("a", "aah"), ("t", "tuh")],
    "hat": [("h", "huh"), ("a", "aah"), ("t", "tuh")],
    "mat": [("m", "mmm"), ("a", "aah"), ("t", "tuh")],
    "sat": [("s", "sss"), ("a", "aah"), ("t", "tuh")],
    "ran": [("r", "rrr"), ("a", "aah"), ("n", "nnn")],
    "sit": [("s", "sss"), ("i", "ihh"), ("t", "tuh")],
    "run": [("r", "rrr"), ("u", "uhh"), ("n", "nnn")],
    "fun": [("f", "fff"), ("u", "uhh"), ("n", "nnn")],
    "big": [("b", "buh"), ("i", "ihh"), ("g", "guh")],
    "red": [("r", "rrr"), ("e", "ehh"), ("d", "duh")],
    "bed": [("b", "buh"), ("e", "ehh"), ("d", "duh")],
    "pig": [("p", "puh"), ("i", "ihh"), ("g", "guh")],
    "log": [("l", "lll"), ("o", "ahh"), ("g", "guh")],
    "car": [("c", "cuh"), ("a", "aah"), ("r", "rrr")],
    "the": [("th", "thh"), ("e", "uhh")],
}

# Alternate colors for phonics letter breakdown
_PHON_COLORS = [COLORS["cyan"], COLORS["orange"], COLORS["green"]]


def _phonics_hint(problem_id: int, letter: str) -> Hint:
    """Generate word-picture association hint for a letter sound."""
    letter = letter.upper()
    words = _PHONICS_WORDS.get(letter, [("❓", f"{letter}...")])

    return Hint(
        problem_id=problem_id,
        hint_type="phonics",
        label="what sound starts them all?",
        content={
            "letter": letter,
            "letter_color": COLORS["magenta"],
            "words": [
                {"emoji": emoji, "word": word, "highlight": letter}
                for emoji, word in words
            ],
            "arrow_color": COLORS["yellow"],
        },
    )


def _sight_word_hint(problem_id: int, word: str) -> Hint:
    """Generate phonics breakdown hint for a sight word."""
    word_lower = word.lower()
    breakdown = _PHONICS_BREAKDOWNS.get(word_lower)

    if breakdown:
        parts = []
        for i, (letter, sound) in enumerate(breakdown):
            color = _PHON_COLORS[i % len(_PHON_COLORS)]
            parts.append({
                "letter": letter,
                "sound": sound,
                "color": color,
            })
        label_parts = " · ".join(f'"{s}"' for _, s in breakdown)
        return Hint(
            problem_id=problem_id,
            hint_type="phonics_breakdown",
            label=label_parts,
            content={"parts": parts, "word": word_lower},
        )

    # Unknown word — just break into individual letters
    parts = []
    for i, ch in enumerate(word_lower):
        color = _PHON_COLORS[i % len(_PHON_COLORS)]
        parts.append({"letter": ch, "sound": ch, "color": color})
    return Hint(
        problem_id=problem_id,
        hint_type="phonics_breakdown",
        label=f"sound out each letter!",
        content={"parts": parts, "word": word_lower},
    )


def _trace_hint(problem_id: int, letter: str) -> Hint:
    """Generate tracing guide hint for a letter."""
    return Hint(
        problem_id=problem_id,
        hint_type="trace",
        label="start at the green dot, follow the arrow!",
        content={
            "letter": letter.upper(),
            "start_color": COLORS["green"],
            "path_color": COLORS["cyan"],
            "arrow_color": COLORS["magenta"],
        },
    )


def generate_reading_hint(problem: Problem, problem_type: ProblemType) -> Hint:
    """Generate a visual hint for a reading problem.

    Routes to the appropriate sub-hint based on problem type.
    """
    text = problem.text

    if problem_type == ProblemType.PHONICS:
        m = _PHONICS_RE.search(text)
        if m:
            return _phonics_hint(problem.id, m.group(1))

    if problem_type == ProblemType.SIGHT_WORDS:
        m = _SIGHT_WORD_RE.search(text)
        if m:
            return _sight_word_hint(problem.id, m.group(1))

    if problem_type == ProblemType.TRACING:
        m = _TRACE_RE.search(text)
        if m:
            return _trace_hint(problem.id, m.group(1))

    # Fallback
    return Hint(
        problem_id=problem.id,
        hint_type="generic",
        label="sound it out!",
        content={"color": COLORS["cyan"]},
    )
