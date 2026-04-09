"""Smoke tests — verify every Hugo module is importable."""


def test_import_capture():
    from hugo.capture import camera
    assert hasattr(camera, "capture_frame")


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
    assert hasattr(math_helper, "Hint")


def test_import_helpers_reading():
    from hugo.helpers import reading_helper
    assert hasattr(reading_helper, "generate_reading_hint")


def test_import_projection():
    from hugo.projection import renderer
    assert hasattr(renderer, "render_frame")
    assert hasattr(renderer, "show_frame")


def test_import_hardware_projector():
    from hugo.hardware import projector
    assert hasattr(projector, "power_on")
    assert hasattr(projector, "power_off")


def test_import_hardware_servos():
    from hugo.hardware import servos
    assert hasattr(servos, "set_lift")
    assert hasattr(servos, "set_pan")
    assert hasattr(servos, "set_tilt")
    assert hasattr(servos, "home")


def test_import_orchestrator():
    from hugo.orchestrator import pipeline
    assert hasattr(pipeline, "run_once")
    assert hasattr(pipeline, "run_loop")


def test_capture_from_file(tmp_path):
    """Test that capture_frame can load an image from a file."""
    from PIL import Image
    from hugo.capture.camera import capture_frame

    # Create a small test image
    img = Image.new("RGB", (100, 100), color="white")
    path = tmp_path / "test_worksheet.png"
    img.save(path)

    result = capture_frame(path)
    assert isinstance(result, Image.Image)
    assert result.size == (100, 100)
