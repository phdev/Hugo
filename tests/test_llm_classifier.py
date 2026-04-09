"""Tests for LLM classifier (Ollama + Anthropic fallback)."""

from unittest.mock import patch, MagicMock

from hugo.classifier.classify import ProblemType, classify_problem
from hugo.classifier.llm import classify_with_ollama, is_ollama_available
from hugo.classifier.anthropic_fallback import classify_with_anthropic
from hugo.layout.analyze import Problem


def _make_problem(text: str) -> Problem:
    return Problem(id=1, text=text, bbox=(0, 0, 100, 30))


# ── Regex still wins when it matches ──

def test_regex_takes_priority():
    """Known patterns should never hit the LLM."""
    p = _make_problem("3 + 2 = ___")
    result = classify_problem(p, use_llm=True)
    assert result == ProblemType.ADDITION


# ── use_llm=False returns UNKNOWN ──

def test_no_llm_returns_unknown():
    p = _make_problem("something weird")
    result = classify_problem(p, use_llm=False)
    assert result == ProblemType.UNKNOWN


# ── Ollama mock tests ──

def test_ollama_success():
    """Ollama returns a valid type."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "addition"}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.post", return_value=mock_response):
        result = classify_with_ollama("three plus two equals blank")
    assert result == ProblemType.ADDITION


def test_ollama_with_extra_text():
    """Ollama returns type buried in a sentence."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "This is clearly subtraction."}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.post", return_value=mock_response):
        result = classify_with_ollama("take away four")
    assert result == ProblemType.SUBTRACTION


def test_ollama_unreachable():
    """Ollama not running → UNKNOWN, no exception."""
    import httpx
    with patch("httpx.post", side_effect=httpx.ConnectError("refused")):
        result = classify_with_ollama("test")
    assert result == ProblemType.UNKNOWN


def test_ollama_timeout():
    """Ollama too slow → UNKNOWN."""
    import httpx
    with patch("httpx.post", side_effect=httpx.TimeoutException("timeout")):
        result = classify_with_ollama("test")
    assert result == ProblemType.UNKNOWN


def test_ollama_garbage_response():
    """Ollama returns nonsense → UNKNOWN."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "I like turtles"}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.post", return_value=mock_response):
        result = classify_with_ollama("test")
    assert result == ProblemType.UNKNOWN


def test_is_ollama_available_true():
    mock_response = MagicMock()
    mock_response.status_code = 200
    with patch("httpx.get", return_value=mock_response):
        assert is_ollama_available() is True


def test_is_ollama_available_false():
    import httpx
    with patch("httpx.get", side_effect=httpx.ConnectError("refused")):
        assert is_ollama_available() is False


# ── Anthropic mock tests ──

def test_anthropic_no_key():
    """No API key → UNKNOWN."""
    with patch.dict("os.environ", {}, clear=True):
        result = classify_with_anthropic("test")
    assert result == ProblemType.UNKNOWN


def test_anthropic_success():
    """Anthropic returns a valid type."""
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="phonics")]
    mock_client.messages.create.return_value = mock_message

    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}), \
         patch("anthropic.Anthropic", return_value=mock_client):
        result = classify_with_anthropic("What sound does B make?")
    assert result == ProblemType.PHONICS


# ── Full chain ──

def test_chain_regex_then_ollama():
    """Regex miss → Ollama hit."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "shapes"}
    mock_response.raise_for_status = MagicMock()

    p = _make_problem("draw a hexagon")
    with patch("httpx.post", return_value=mock_response):
        result = classify_problem(p, use_llm=True)
    assert result == ProblemType.SHAPES


def test_chain_all_fail():
    """Regex miss → Ollama miss → Anthropic miss → UNKNOWN."""
    import httpx
    p = _make_problem("gibberish xyz")
    with patch("httpx.post", side_effect=httpx.ConnectError("refused")), \
         patch.dict("os.environ", {}, clear=True):
        result = classify_problem(p, use_llm=True)
    assert result == ProblemType.UNKNOWN
