# Hugo

A homework helping projector box for 4-7 year olds.

Hugo uses a camera to see physical worksheets on a table, understands them via
vision/OCR, and projects scaffolded help back onto the page using a Kodak Luma 350
pico projector. It gives **hints, never answers**.

## Architecture

Mac mini M4 is the only compute. Desk sensors are XIAO ESP32-S3 boards streaming
over WiFi. The Luma 350 receives AirPlay from the Mac mini.

## Quick Start

```bash
pip install -e ".[dev]"
pytest
python -m hugo.orchestrator --image tests/fixtures/math_worksheet.png
```

## How It Works

1. Kid places a worksheet on the table
2. XIAO camera captures the page (MJPEG over WiFi)
3. Mac mini preprocesses and extracts problems via OCR
4. Classifier determines problem type (regex → Ollama → Anthropic)
5. Subject-specific helper generates age-appropriate hints
6. Mac mini renders overlay and sends to projector via AirPlay

## Hardware

### On the desk
- Kodak Luma 350 projector (AirPlay from Mac mini)
- XIAO ESP32-S3 #1 + OV5640 120° camera + onboard mic
- XIAO ESP32-S3 #2 + VL53L7CX ToF sensor (finger detection)
- Anker Nano 10K 30W battery
- All inside 6" acrylic display case, no moving parts

### Off the desk
- Mac mini M4 16GB (Qwen 3 4B via Ollama, Anthropic API)

## Project Structure

```
hugo/
├── capture/        # XIAO camera HTTP client
├── vision/         # Image preprocessing
├── ocr/            # Text extraction (Tesseract)
├── layout/         # Worksheet layout analysis
├── classifier/     # Problem type detection + LLM fallback
├── helpers/        # Subject-specific hint generators
├── projection/     # Render overlays, AirPlay to Luma 350
├── interaction/    # Finger detection, help buttons, dwell timer
├── voice/          # XIAO mic, wake word, voice commands
├── hardware/       # XIAO ToF HTTP client
└── orchestrator/   # Main pipeline loop
```
