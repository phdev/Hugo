"""Smoke tests — verify every Hugo module is importable."""


def test_import_vision():
    from hugo.vision import preprocess
    assert hasattr(preprocess, "preprocess")


def test_import_ocr():
    from hugo.ocr import extract
    assert hasattr(extract, "extract_text")
    assert hasattr(extract, "OcrResult")


def test_import_layout():
    from hugo.layout import analyze
    assert hasattr(analyze, "analyze_layout")
    assert hasattr(analyze, "WorksheetLayout")
    assert hasattr(analyze, "Problem")


def test_import_classifier():
    from hugo.classifier import classify
    assert hasattr(classify, "classify_problem")
    assert hasattr(classify, "ProblemType")


def test_import_helpers_math():
    from hugo.helpers import math_helper
    assert hasattr(math_helper, "generate_math_hint")


def test_import_helpers_reading():
    from hugo.helpers import reading_helper
    assert hasattr(reading_helper, "generate_reading_hint")


def test_import_helpers_router():
    from hugo.helpers import generate_hint
    assert callable(generate_hint)


def test_import_orchestrator():
    from hugo.orchestrator import pipeline
    assert hasattr(pipeline, "run_once")
    assert hasattr(pipeline, "PipelineResult")


def test_import_pi_camera():
    from hugo.pi import camera
    assert hasattr(camera, "capture_frame")
    assert hasattr(camera, "analyze_homework")


def test_import_pi_tof():
    from hugo.pi import tof
    assert hasattr(tof, "TapEvent")
    assert hasattr(tof, "ToFState")
    assert hasattr(tof, "calibrate")
    assert hasattr(tof, "poll_once")


def test_import_pi_voice():
    from hugo.pi import voice
    assert hasattr(voice, "VoiceState")
    assert hasattr(voice, "transcribe_audio")
    assert hasattr(voice, "process_voice_command")


def test_import_pi_renderer():
    from hugo.pi import renderer
    assert hasattr(renderer, "RendererState")
    assert hasattr(renderer, "render_frame")
    assert hasattr(renderer, "show_frame")


def test_import_pi_config():
    from hugo.pi import config
    assert hasattr(config, "SERVER_BASE_URL")
    assert hasattr(config, "DISPLAY_WIDTH")
    assert hasattr(config, "TOF_POLL_HZ")


def test_import_server_inference():
    from hugo.server import inference_api
    assert hasattr(inference_api, "_analyze_image")


def test_import_shared_models():
    from hugo.shared import models
    assert hasattr(models, "HomeworkProblem")
    assert hasattr(models, "HomeworkResult")


def test_import_voice_commands():
    from hugo.voice import commands
    assert hasattr(commands, "parse_command")
    assert hasattr(commands, "CommandType")


def test_dev_pipeline():
    """Dev pipeline runs on a fixture image."""
    from pathlib import Path
    from hugo.orchestrator.pipeline import run_once
    result = run_once(Path("tests/fixtures/math_worksheet.png"))
    assert len(result.problems) >= 7
    assert len(result.hints) == len(result.problems)
