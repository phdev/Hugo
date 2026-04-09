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
- Pi Camera 3 (wide, 120° FOV)
- Kodak Luma 150 projector (HDMI-CEC)
- VL53L7CX ToF sensor (finger detection)
- Mac mini M4 as remote LLM brain (Ollama)

All sensors are fixed-mounted inside the enclosure with pre-angled cutouts — no moving parts.

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
├── hardware/       # Projector control, ToF sensor
└── orchestrator/   # Main pipeline loop
```
