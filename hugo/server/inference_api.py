"""FastAPI inference server — runs on Mac mini M4.

The Pi 5 calls these endpoints over WiFi. All heavy compute
(vision, OCR, LLM inference) runs here.

Endpoints:
  POST /analyze-homework  — JPEG → vision → OCR → classify → hints
  POST /transcribe         — PCM audio → whisper.cpp → text
  POST /get-help           — problem text → tiered LLM → hint
  GET  /health             — liveness check

Run: uvicorn hugo.server.inference_api:app --host 0.0.0.0 --port 8000
"""

import io
import logging
import tempfile

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# Lazy import FastAPI so the module is importable without it installed
try:
    from fastapi import FastAPI, File, UploadFile
    from fastapi.responses import JSONResponse
except ImportError:
    FastAPI = None  # type: ignore

from hugo.classifier.classify import ProblemType, classify_problem
from hugo.helpers import generate_hint
from hugo.helpers.hint import Hint
from hugo.layout.analyze import analyze_layout
from hugo.ocr.extract import extract_lines
from hugo.vision.preprocess import preprocess

if FastAPI:
    app = FastAPI(title="Hugo Inference Server")
else:
    app = None


def _analyze_image(image: Image.Image) -> dict:
    """Run the full vision pipeline on an image.

    Returns structured homework data with hints pre-generated.
    """
    processed = preprocess(image)
    lines = extract_lines(processed)
    layout = analyze_layout(lines, image.size)

    problems = []
    for p in layout.problems:
        ptype = classify_problem(p, use_llm=True)
        hint = generate_hint(p, ptype)

        problems.append({
            "id": p.id,
            "text": p.text,
            "type": ptype.value,
            "bbox": list(p.bbox),
            "hint": {
                "hint_type": hint.hint_type,
                "label": hint.label,
                "content": hint.content,
            },
        })

    return {"problems": problems, "title": layout.title}


if app:

    @app.post("/analyze-homework")
    async def analyze_homework(image: UploadFile = File(...)):
        """Analyze a worksheet image for homework problems."""
        contents = await image.read()
        img = Image.open(io.BytesIO(contents))
        result = _analyze_image(img)
        return JSONResponse(content=result)

    @app.post("/transcribe")
    async def transcribe(audio: UploadFile = File(...)):
        """Transcribe audio using whisper.cpp.

        Expects raw PCM: 16kHz, 16-bit, mono.
        """
        contents = await audio.read()
        samples = np.frombuffer(contents, dtype=np.int16)

        try:
            from whispercpp import Whisper

            if not hasattr(transcribe, "_model"):
                from hugo.server.config import WHISPER_MODEL
                transcribe._model = Whisper.from_pretrained(WHISPER_MODEL)

            # whisper.cpp expects float32 normalized to [-1, 1]
            audio_f32 = samples.astype(np.float32) / 32768.0

            with tempfile.NamedTemporaryFile(suffix=".wav") as f:
                import wave
                with wave.open(f.name, "w") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(16000)
                    wf.writeframes(samples.tobytes())
                text = transcribe._model.transcribe(f.name)

            return {"text": text}

        except ImportError:
            logger.warning("whispercpp not installed, transcription unavailable")
            return {"text": "", "error": "whisper not available"}
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {"text": "", "error": str(e)}

    @app.post("/get-help")
    async def get_help(problem: dict):
        """Generate a hint for a specific problem.

        Tiered routing: regex → Ollama → Anthropic.
        """
        from hugo.layout.analyze import Problem

        p = Problem(
            id=problem.get("id", 0),
            text=problem.get("text", ""),
            bbox=tuple(problem.get("bbox", [0, 0, 100, 30])),
        )
        ptype = classify_problem(p, use_llm=True)
        hint = generate_hint(p, ptype)

        return {
            "problem_id": p.id,
            "type": ptype.value,
            "hint": {
                "hint_type": hint.hint_type,
                "label": hint.label,
                "content": hint.content,
            },
        }

    @app.get("/health")
    async def health():
        return {"status": "ok", "service": "hugo-inference"}
