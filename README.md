# Hugo

A homework helping projector box for 4-7 year olds.

Hugo uses a Raspberry Pi camera to see physical worksheets on a table, understands them
via vision/OCR, and projects scaffolded help back onto the page using a Kodak Luma 150
pico projector. It gives **hints, never answers**.

## Quick Start

```bash
pip install -e ".[dev]"
pytest
```

## How It Works

1. Kid places a worksheet on the table
2. Pi camera captures the page
3. Vision pipeline preprocesses and extracts problems via OCR
4. Classifier determines problem type (math, reading, etc.)
5. Subject-specific helper generates age-appropriate hints
6. Projector displays visual help aligned to the physical page

## Hardware

- Raspberry Pi 5
- Pi Camera Module
- Kodak Luma 150 projector (HDMI-CEC)
- Actuonix L12-50 + 2x MG90S servos (lift/pan/tilt)
- Mac mini M4 as remote LLM brain (Ollama)

## Project Structure

```
hugo/
├── capture/        # Camera interface (stubbed to file load for dev)
├── vision/         # Image preprocessing
├── ocr/            # Text extraction
├── layout/         # Worksheet layout analysis
├── classifier/     # Problem type detection
├── helpers/        # Subject-specific hint generators
├── projection/     # Render and project help frames
├── hardware/       # Projector and servo control
└── orchestrator/   # Main pipeline loop
```
