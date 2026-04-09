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


def test_import_interaction_help_buttons():
    from hugo.interaction import help_buttons
    assert hasattr(help_buttons, "HelpButton")
    assert hasattr(help_buttons, "create_help_buttons")
    assert hasattr(help_buttons, "render_help_button")


def test_import_interaction_finger_detect():
    from hugo.interaction import finger_detect
    assert hasattr(finger_detect, "FingerDetection")
    assert hasattr(finger_detect, "set_reference_frame")
    assert hasattr(finger_detect, "detect_finger")
    assert hasattr(finger_detect, "point_in_circle")


def test_import_interaction_dwell():
    from hugo.interaction import dwell
    assert hasattr(dwell, "update_button_states")
    assert hasattr(dwell, "DWELL_MS")


def test_import_interaction_touch_fusion():
    from hugo.interaction import touch_fusion
    assert hasattr(touch_fusion, "fuse_detections")


def test_import_hardware_tof():
    from hugo.hardware import tof_sensor
    assert hasattr(tof_sensor, "ZoneGrid")
    assert hasattr(tof_sensor, "TouchZone")
    assert hasattr(tof_sensor, "init")
    assert hasattr(tof_sensor, "read_grid")
    assert hasattr(tof_sensor, "detect_touch_zones")
    assert hasattr(tof_sensor, "zone_to_worksheet_xy")
    assert hasattr(tof_sensor, "calibrate_baseline")


def test_tof_zone_grid():
    """Test ZoneGrid validity checking and masking."""
    import numpy as np
    from hugo.hardware.tof_sensor import ZoneGrid

    distances = np.full((8, 8), 400, dtype=np.int16)
    statuses = np.full((8, 8), 5, dtype=np.uint8)  # all valid
    statuses[0, 0] = 0  # invalid zone

    grid = ZoneGrid(distances=distances, statuses=statuses)
    assert grid.is_valid(1, 1) is True
    assert grid.is_valid(0, 0) is False

    valid = grid.valid_distances()
    assert valid[0, 0] == 0      # masked out
    assert valid[1, 1] == 400    # kept


def test_tof_detect_touch_zones():
    """Test finger detection against a baseline."""
    import numpy as np
    from hugo.hardware.tof_sensor import ZoneGrid, detect_touch_zones

    baseline = np.full((8, 8), 400, dtype=np.int16)  # table at 400mm

    # Current frame: one zone much closer (finger)
    distances = np.full((8, 8), 400, dtype=np.int16)
    distances[3, 4] = 350  # finger 50mm closer
    statuses = np.full((8, 8), 5, dtype=np.uint8)

    grid = ZoneGrid(distances=distances, statuses=statuses)
    touches = detect_touch_zones(grid, baseline, threshold_mm=40)

    assert len(touches) == 1
    assert touches[0].row == 3
    assert touches[0].col == 4
    assert touches[0].delta_mm == 50


def test_tof_no_touch():
    """No touch when distances match baseline."""
    import numpy as np
    from hugo.hardware.tof_sensor import ZoneGrid, detect_touch_zones

    baseline = np.full((8, 8), 400, dtype=np.int16)
    distances = np.full((8, 8), 395, dtype=np.int16)  # 5mm noise
    statuses = np.full((8, 8), 5, dtype=np.uint8)

    grid = ZoneGrid(distances=distances, statuses=statuses)
    touches = detect_touch_zones(grid, baseline, threshold_mm=40)
    assert len(touches) == 0


def test_tof_zone_to_worksheet_xy():
    """Test zone-to-pixel coordinate mapping."""
    from hugo.hardware.tof_sensor import zone_to_worksheet_xy

    # Center of zone (0,0) in an 8x8 grid on a 640x828 worksheet
    x, y = zone_to_worksheet_xy(0, 0, resolution=8,
                                worksheet_width=640, worksheet_height=828)
    assert x == 40   # 640/8/2
    assert y == 51    # 828/8/2 ≈ 51

    # Last zone (7,7)
    x, y = zone_to_worksheet_xy(7, 7, resolution=8,
                                worksheet_width=640, worksheet_height=828)
    assert x == 600   # 7 * 80 + 40
    assert y == 776    # 7 * 103.5 + 51


def test_help_button_creation():
    """Test that help buttons are created from problem bounding boxes."""
    from hugo.layout.analyze import Problem
    from hugo.interaction.help_buttons import create_help_buttons

    problems = [
        Problem(id=1, text="3 + 2 =", bbox=(60, 100, 300, 40)),
        Problem(id=2, text="7 + 5 =", bbox=(60, 200, 300, 40)),
        Problem(id=3, text="4 + 4 =", bbox=(60, 300, 300, 40)),
    ]
    buttons = create_help_buttons(problems, margin_x=30)

    assert len(buttons) == 3
    assert buttons[0].problem_id == 1
    assert buttons[0].cx == 30
    assert buttons[0].cy == 114  # y + 14
    assert buttons[1].cy == 214
    assert all(b.state == "idle" for b in buttons)


def test_help_button_render_states():
    """Test rendering for each button state."""
    from hugo.interaction.help_buttons import HelpButton, render_help_button

    btn = HelpButton(problem_id=1, cx=30, cy=100)

    idle = render_help_button(btn)
    assert idle["icon"] == "?"
    assert idle["radius"] == 18

    btn.state = "pressing"
    btn.press_progress = 0.5
    pressing = render_help_button(btn)
    assert pressing["radius"] > idle["radius"]
    assert pressing["color"] == "#ffe600"

    btn.state = "triggered"
    triggered = render_help_button(btn)
    assert triggered["icon"] == "✓"
    assert triggered["radius"] == 36


def test_point_in_circle():
    from hugo.interaction.finger_detect import point_in_circle

    assert point_in_circle(30, 100, 30, 100, 18) is True   # center
    assert point_in_circle(48, 100, 30, 100, 18) is True   # on edge
    assert point_in_circle(49, 100, 30, 100, 18) is False   # just outside
    assert point_in_circle(0, 0, 30, 100, 18) is False      # far away


def test_dwell_state_machine():
    """Test the idle→hover→pressing→triggered state transitions."""
    from hugo.interaction.help_buttons import HelpButton
    from hugo.interaction.finger_detect import FingerDetection
    from hugo.interaction.dwell import update_button_states

    btn = HelpButton(problem_id=1, cx=30, cy=100, radius=18)
    buttons = [btn]

    # No finger → stays idle
    result = update_button_states(buttons, None)
    assert result is None
    assert btn.state == "idle"

    # Finger far away → stays idle
    far = FingerDetection(x=200, y=200, confidence=0.9, contour_area=500)
    result = update_button_states(buttons, far)
    assert btn.state == "idle"

    # Finger near but not on → hover
    near = FingerDetection(x=55, y=100, confidence=0.9, contour_area=500)
    result = update_button_states(buttons, near)
    assert btn.state == "hover"

    # Finger directly on → pressing
    on = FingerDetection(x=30, y=100, confidence=0.9, contour_area=500)
    result = update_button_states(buttons, on)
    assert btn.state == "pressing"


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
