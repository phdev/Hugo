# Hugo — Homework Helping Projector Box

## What Hugo Is

A dedicated physical device (not a screen app) that helps 4-7 year olds with homework.
Core loop: kid places worksheet → Pi camera captures it → vision pipeline extracts
problems → classifier determines type → helper generates age-appropriate hints (never
answers) → projector displays visual help aligned to the physical page.

## Hardware

- **Raspberry Pi 5** — compute
- **Pi Camera Module** — captures worksheets
- **Kodak Luma 150 projector** — HDMI-CEC via `cec-client`
- **Actuonix L12-50 linear servo + 2x MG90S servos** — lift/pan/tilt
- **Mac mini M4 16GB** — remote LLM brain (Qwen 3 8B via Ollama)
- **Anthropic API** (Sonnet/Opus) — complex fallback

## Subject Scope

- **Math**: counting, add/subtract under 20, shapes, patterns
- **Reading**: phonics, sight words, letter recognition
- **General**: colors, sequencing, matching, basic science

## Module Structure

- `capture/` — Pi camera interface, stubbed to load from file for dev
- `vision/` — Image preprocessing (lighting, perspective correction)
- `ocr/` — Text extraction (Tesseract or PaddleOCR)
- `layout/` — Worksheet layout analysis, detect individual problems and answer blanks
- `classifier/` — Problem type detection, routes to correct helper
- `helpers/` — Subject-specific agents (math, phonics, shapes)
- `projection/` — Render help frames, calibration, page alignment. Pygame or Cairo → HDMI out, stubbed to desktop window for dev
- `hardware/` — `cec-client` projector control, servo control via gpiozero/pigpio
- `orchestrator/` — Main loop tying the pipeline together

## Key Rules

- **Hints not answers.** Always scaffold.
- **Visual-first output** — icons, arrows, animations, color. These kids can barely read.
- **Offline-capable** for basic math and letter recognition.
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

# Run the main loop (dev mode — loads from file, renders to desktop window)
python -m hugo.orchestrator
```

## Current Phase

**Phase 0**: Project scaffolding, directory structure, stubbed modules, vision pipeline
with test fixture worksheet images, basic OCR extraction, worksheet classifier prototype.
Everything testable on a laptop with sample images — no hardware required.
