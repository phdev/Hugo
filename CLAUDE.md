# Hugo — Homework Helping Projector Box

## What Hugo Is

A dedicated physical device (not a screen app) that helps 4-7 year olds with homework.
Core loop: kid places worksheet → camera captures it → vision pipeline extracts
problems → classifier determines type → helper generates age-appropriate hints (never
answers) → projector displays visual help aligned to the physical page.

## Architecture

Mac mini M4 is the ONLY compute. Everything on the desk is a dumb sensor/output
that communicates over WiFi. No Raspberry Pi.

## Hardware

### On the desk (inside 6" acrylic display case)
- **Kodak Luma 350 projector** — receives AirPlay from Mac mini, USB-A powers sensors
- **XIAO ESP32-S3 Sense #1** — OV5640 120° camera + onboard MEMS mic (hugo-cam.local)
- **XIAO ESP32-S3 Sense #2** — VL53L7CX ToF sensor via I2C (hugo-tof.local)
- **Anker Nano 10K 30W** — battery, powers Luma via 15V PD trigger cable
- **Tiny USB-A hub** — Luma USB-A powers both XIAOs

### Off the desk
- **Mac mini M4 16GB** — all compute: vision, OCR, LLM, rendering, AirPlay output
- **Ollama** — Qwen 3 4B for classifier fallback
- **Anthropic API** (Sonnet/Opus) — complex fallback

## Data Flow

```
XIAO #1 (camera)  ──HTTP MJPEG──→  Mac mini (captures frames)
XIAO #1 (mic)     ──HTTP PCM──→    Mac mini (whisper.cpp STT)
XIAO #2 (ToF)     ──HTTP JSON──→   Mac mini (8×8 depth grid @ 15Hz)
Mac mini           ──AirPlay──→     Luma 350 (rendered overlay)
```

## Subject Scope

- **Math**: counting, add/subtract under 20, shapes, patterns
- **Reading**: phonics, sight words, letter recognition
- **General**: colors, sequencing, matching, basic science

## Module Structure

- `capture/` — HTTP MJPEG client, captures frames from XIAO #1 camera over WiFi
- `vision/` — Image preprocessing (lighting, perspective correction)
- `ocr/` — Text extraction (Tesseract)
- `layout/` — Worksheet layout analysis, detect individual problems and answer blanks
- `classifier/` — Problem type detection: regex → Ollama (Qwen 3 4B) → Anthropic API
- `helpers/` — Subject-specific hint generators (math, phonics, shapes)
- `projection/` — Render help frames via PIL, display via AirPlay screen mirror to Luma 350
- `interaction/` — Finger detection (background subtraction + ToF fusion), projected help buttons, dwell timer
- `voice/` — XIAO onboard mic over WiFi, wake word ("Hey Hugo"), voice commands, VAD
- `hardware/` — HTTP clients for XIAO ToF sensor
- `orchestrator/` — Main loop tying the pipeline together

## Key Rules

- **Hints not answers.** Always scaffold.
- **Visual-first output** — icons, arrows, animations, color. These kids can barely read.
- **Offline-capable** for basic math and letter recognition (regex classifier).
- Do **NOT** use LiteLLM. Direct SDK calls to Ollama and Anthropic only.
- No Comni integration — standalone project.
- Python 3.11+, pytest, snake_case.
- LLM routing: local pattern matching → Ollama (Mac mini) → Anthropic API.

## Development

```bash
# Install in dev mode
pip install -e ".[dev]"

# Run tests
pytest

# Run pipeline on a fixture image
python -m hugo.orchestrator --image tests/fixtures/math_worksheet.png

# Run the main loop (requires XIAO sensors on WiFi)
python -m hugo.orchestrator
```

## Current Phase

**Phase 0→5 complete**: Full pipeline working on laptop with fixture images.
Image → preprocess → OCR → layout → classify → generate hints → render overlay.
Classifier chain: regex → Ollama → Anthropic. Voice command parser implemented.
Interaction module with help buttons, ToF fusion, dwell timer.

**Next**: Flash XIAO firmware, verify WiFi streams, set up AirPlay to Luma 350.
