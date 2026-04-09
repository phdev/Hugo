# Hugo

A homework helping projector box for 4-7 year olds.

Hugo uses a camera to see physical worksheets on a table, understands them via
vision/OCR/LLM, and projects scaffolded help back onto the page using a Kodak Luma 350
projector. It gives **hints, never answers**.

## Architecture

Raspberry Pi 5 on the desk handles local I/O and rendering via HDMI (~80ms latency).
Mac mini M4 over WiFi handles inference (whisper.cpp, Claude Vision, Ollama, Groq).

## Quick Start

```bash
pip install -e ".[dev]"
pytest
python -m hugo.orchestrator --image tests/fixtures/math_worksheet.png
```

## How It Works

1. Kid places a worksheet on the table
2. Arducam captures the page (CSI → Pi 5)
3. Pi sends frame to Mac mini for analysis (WiFi HTTP)
4. Mac mini runs vision → OCR → classify → generate hints
5. Pi receives hints, renders overlay via PyGame
6. Luma 350 projects hints onto the worksheet via HDMI

Tap a projected "?" button → hint appears in ~80ms (local on Pi, no network hop).

## Hardware

### On the desk (6" acrylic display case)
- Raspberry Pi 5 (8GB) — desk brain
- Arducam Pi Camera 3 Wide 120° (IMX708, CSI)
- ReSpeaker 2-Mics Pi HAT V2.0 (TLV320AIC3104, GPIO)
- SparkFun Qwiic Mini VL53L5CX (8×8 ToF, I2C)
- Kodak Luma 350 projector (HDMI from Pi)
- Anker Nano 10K 30W battery

### Off the desk
- Mac mini M4 16GB (inference server)

Zero soldering — all snap/plug connections.

## Project Structure

```
hugo/
├── pi/             # Runs on Pi 5: camera, mic, ToF, renderer, orchestrator
├── server/         # Runs on Mac mini: FastAPI inference endpoints
├── vision/         # Image preprocessing (used by server)
├── ocr/            # Text extraction via Tesseract (used by server)
├── layout/         # Worksheet layout analysis (used by server)
├── classifier/     # Problem type detection + LLM fallback (used by server)
├── helpers/        # Subject-specific hint generators (used by server)
├── shared/         # Pydantic models shared between Pi and server
├── tests/          # pytest suite
└── site/           # GitHub Pages demo
```
