# Hugo — Homework Helping Projector Box

## What Hugo Is

A dedicated physical device (not a screen app) that helps 4-7 year olds with homework.
Core loop: kid places worksheet → camera captures it → vision pipeline extracts
problems → classifier determines type → helper generates age-appropriate hints (never
answers) → projector displays visual help aligned to the physical page.

## Architecture

Raspberry Pi 5 on the desk handles all local I/O: camera, mic, ToF sensor, and HDMI
rendering to the projector (~80ms tap-to-visual latency). Mac mini M4 over WiFi handles
inference only: whisper.cpp, Claude Vision, Ollama, Groq.

## Hardware

### On the desk (inside 6" acrylic display case)
- **Raspberry Pi 5 (8GB)** — desk brain, renders locally
- **Arducam Pi Camera 3 Wide** — 120° FOV, 12MP IMX708, CSI connector
- **ReSpeaker 2-Mics Pi HAT V2.0** — TLV320AIC3104, AEC/NS, GPIO header
- **SparkFun Qwiic Mini VL53L5CX** — 8×8 ToF, 63° FOV, I2C via Qwiic cable
- **Kodak Luma 350 projector** — HDMI from Pi 5
- **Anker Nano 10K 30W** — 15V PD → Luma, 5V USB-A → Pi 5

### Off the desk
- **Mac mini M4 16GB** — inference server (whisper.cpp, Ollama, Claude API, Groq)

### Power chain
```
Anker Nano 10K 30W
├── USB-C PD 15V → barrel jack → Luma 350 (~15W)
└── USB-A 5V/3A → USB-C → Pi 5 (~8W)
```

## Data Flow

```
Arducam (CSI)     → Pi 5 → WiFi HTTP → Mac mini (Claude Vision analysis)
ReSpeaker (I2S)   → Pi 5 → WiFi HTTP → Mac mini (whisper.cpp STT)
VL53L5CX (I2C)    → Pi 5 (local tap detection, no network hop)
Pi 5 (PyGame)     → HDMI → Luma 350 (~80ms tap response)
Mac mini           → WiFi HTTP → Pi 5 (analysis results, hints)
```

## Latency

- **Tap detection**: ~80ms (ToF I2C → Pi 5 → PyGame → HDMI → Luma)
- **Voice response**: ~1-3s (mic → Pi → Mac mini whisper.cpp → LLM → Pi → HDMI)
- **Camera capture**: ~200ms (CSI frame → Pi → WiFi → Mac mini → Claude Vision)

## Subject Scope

- **Math**: counting, add/subtract under 20, shapes, patterns
- **Reading**: phonics, sight words, letter recognition
- **General**: colors, sequencing, matching, basic science

## Module Structure

### Pi 5 (desk)
- `pi/camera.py` — Picamera2 capture, sends frames to Mac mini for analysis
- `pi/tof.py` — VL53L5CX I2C polling, local tap detection + debounce
- `pi/voice.py` — ReSpeaker HAT audio, openWakeWord, sends audio to Mac mini
- `pi/renderer.py` — PyGame full-screen HDMI overlay (854×480 WVGA)
- `pi/orchestrator.py` — Pi-side main loop, event routing

### Mac mini (inference)
- `server/inference_api.py` — FastAPI: /analyze-homework, /transcribe, /get-help
- `server/cache.py` — Semantic cache (SQLite + MiniLM-L6)
- `server/config.py` — API keys, model settings

### Shared (pipeline core, called by server)
- `vision/` — Image preprocessing (lighting, perspective correction)
- `ocr/` — Text extraction (Tesseract)
- `layout/` — Worksheet layout analysis
- `classifier/` — Problem type detection: regex → Ollama (Qwen 3 4B) → Anthropic API
- `helpers/` — Subject-specific hint generators (math, phonics, shapes)

## Key Rules

- **Hints not answers.** Always scaffold.
- **Visual-first output** — icons, arrows, animations, color. These kids can barely read.
- **Offline-capable** for basic math and letter recognition (regex classifier on Pi).
- Do **NOT** use LiteLLM. Direct SDK calls to Ollama, Anthropic, and Groq only.
- No Comni integration — standalone project.
- Python 3.11+, pytest, snake_case.
- LLM routing: local pattern matching → Groq (fast) → Claude API (complex).
- Pi 5 renders locally via HDMI — no AirPlay, no network hop for display.

## Development

```bash
# Install in dev mode (laptop/Mac mini)
pip install -e ".[dev]"

# Run tests
pytest

# Run pipeline on a fixture image
python -m hugo.orchestrator --image tests/fixtures/math_worksheet.png

# On the Pi 5
pip install -r requirements-pi.txt
python3 -m hugo.pi.orchestrator

# On the Mac mini
pip install -e ".[server]"
uvicorn hugo.server.inference_api:app --host 0.0.0.0 --port 8000
```

## Current Phase

**Phase 0→5 complete**: Full pipeline working with fixture images.
Image → preprocess → OCR → layout → classify → generate hints → render overlay.
Classifier chain: regex → Ollama → Anthropic. Voice command parser implemented.

**Phase 6 (current)**: Pi 5 + HDMI architecture. Building pi/ and server/ modules.

**Next**: Flash Pi 5, verify hardware, test end-to-end with real worksheet.
