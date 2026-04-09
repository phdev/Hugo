"""Anthropic API fallback classifier.

Last resort when both regex and Ollama fail to classify a problem.
Uses Claude Sonnet for reliable classification at the cost of
latency and API usage. Should rarely be called in practice.
"""

import logging
import os

from hugo.classifier.classify import ProblemType

logger = logging.getLogger(__name__)

_CLASSIFY_PROMPT = """You are classifying a worksheet problem for a 4-7 year old.
Given the problem text, respond with EXACTLY one word from this list:
addition, subtraction, counting, shapes, patterns, phonics, sight_words, letter_recognition, tracing, colors, sequencing, matching

Problem: "{text}"
"""

_TYPE_MAP: dict[str, ProblemType] = {
    "addition": ProblemType.ADDITION,
    "subtraction": ProblemType.SUBTRACTION,
    "counting": ProblemType.COUNTING,
    "shapes": ProblemType.SHAPES,
    "patterns": ProblemType.PATTERNS,
    "phonics": ProblemType.PHONICS,
    "sight_words": ProblemType.SIGHT_WORDS,
    "letter_recognition": ProblemType.LETTER_RECOGNITION,
    "tracing": ProblemType.TRACING,
    "colors": ProblemType.COLORS,
    "sequencing": ProblemType.SEQUENCING,
    "matching": ProblemType.MATCHING,
}


def classify_with_anthropic(text: str) -> ProblemType:
    """Classify a problem using the Anthropic API (Claude Sonnet).

    Requires ANTHROPIC_API_KEY environment variable. Returns
    UNKNOWN if the key is missing or the call fails — never raises.

    Args:
        text: The problem text to classify.

    Returns:
        Classified ProblemType, or UNKNOWN on failure.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logger.debug("No ANTHROPIC_API_KEY set — skipping Anthropic fallback")
        return ProblemType.UNKNOWN

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=20,
            messages=[{
                "role": "user",
                "content": _CLASSIFY_PROMPT.format(text=text),
            }],
        )

        raw = message.content[0].text.strip().lower()
        for word in raw.split():
            word = word.strip(".,;:!?\"'")
            if word in _TYPE_MAP:
                logger.info(f"Anthropic classified '{text}' as {word}")
                return _TYPE_MAP[word]

        logger.warning(f"Anthropic response unparseable: '{raw}'")
        return ProblemType.UNKNOWN

    except Exception as e:
        logger.warning(f"Anthropic error: {e}")
        return ProblemType.UNKNOWN
