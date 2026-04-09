"""LLM-based classifier fallback via Ollama.

When regex rules can't classify a problem, this module calls
Qwen 3 4B running on the Mac mini via Ollama's HTTP API.

Routing: regex (instant) → Ollama (fast, local network) → Anthropic API (last resort).
"""

import logging

import httpx

from hugo.classifier.classify import ProblemType

logger = logging.getLogger(__name__)

# ── Configuration ──

OLLAMA_BASE_URL: str = "http://localhost:11434"
OLLAMA_MODEL: str = "qwen3:4b"
OLLAMA_TIMEOUT: float = 10.0  # seconds

_CLASSIFY_PROMPT = """You are classifying a worksheet problem for a 4-7 year old.
Given the problem text, respond with EXACTLY one of these types:
addition, subtraction, counting, shapes, patterns, phonics, sight_words, letter_recognition, tracing, colors, sequencing, matching

Problem: "{text}"

Type:"""

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


def classify_with_ollama(
    text: str,
    base_url: str = OLLAMA_BASE_URL,
    model: str = OLLAMA_MODEL,
    timeout: float = OLLAMA_TIMEOUT,
) -> ProblemType:
    """Classify a problem using Ollama (Qwen 3 4B).

    Makes a synchronous HTTP call to the Ollama API. Returns
    UNKNOWN if the model is unreachable or gives an unparseable
    response — never raises.

    Args:
        text: The problem text to classify.
        base_url: Ollama server URL (default localhost:11434).
        model: Model name (default qwen3:4b).
        timeout: Request timeout in seconds.

    Returns:
        Classified ProblemType, or UNKNOWN on failure.
    """
    try:
        response = httpx.post(
            f"{base_url}/api/generate",
            json={
                "model": model,
                "prompt": _CLASSIFY_PROMPT.format(text=text),
                "stream": False,
                "options": {
                    "temperature": 0.0,
                    "num_predict": 20,
                },
            },
            timeout=timeout,
        )
        response.raise_for_status()

        raw = response.json().get("response", "").strip().lower()
        # Extract the first word that matches a known type
        for word in raw.split():
            word = word.strip(".,;:!?\"'")
            if word in _TYPE_MAP:
                logger.info(f"Ollama classified '{text}' as {word}")
                return _TYPE_MAP[word]

        logger.warning(f"Ollama response unparseable: '{raw}' for '{text}'")
        return ProblemType.UNKNOWN

    except httpx.ConnectError:
        logger.debug("Ollama not reachable — returning UNKNOWN")
        return ProblemType.UNKNOWN
    except httpx.TimeoutException:
        logger.warning(f"Ollama timed out after {timeout}s")
        return ProblemType.UNKNOWN
    except Exception as e:
        logger.warning(f"Ollama error: {e}")
        return ProblemType.UNKNOWN


def is_ollama_available(base_url: str = OLLAMA_BASE_URL) -> bool:
    """Check if Ollama is reachable."""
    try:
        r = httpx.get(f"{base_url}/api/tags", timeout=2.0)
        return r.status_code == 200
    except Exception:
        return False
