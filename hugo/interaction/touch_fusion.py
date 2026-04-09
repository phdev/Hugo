"""Fused touch detection — combines camera + VL53L7CX ToF sensor.

The camera provides fine-grained fingertip position via background
subtraction. The ToF sensor provides lighting-independent zone
detection. This module fuses both signals:

- ToF alone: coarse zone detection (which problem area), reliable
  even with projector light that confuses the camera.
- Camera alone: precise fingertip position, works in good lighting.
- Both: ToF confirms a finger is present, camera refines position.

The fused result feeds into the dwell timer as a FingerDetection.
"""

from hugo.hardware.tof_sensor import (
    TouchZone,
    ZoneGrid,
    detect_touch_zones,
    zone_to_worksheet_xy,
)
from hugo.interaction.finger_detect import FingerDetection, detect_finger

import numpy as np
from PIL import Image


def fuse_detections(
    # Camera inputs
    camera_frame: Image.Image | None,
    camera_reference: np.ndarray | None,
    # ToF inputs
    tof_grid: ZoneGrid | None,
    tof_baseline: np.ndarray | None,
    # Config
    tof_threshold_mm: int = 40,
    worksheet_size: tuple[int, int] = (640, 828),
) -> FingerDetection | None:
    """Combine camera and ToF sensor to detect a fingertip.

    Priority logic:
    1. If both camera and ToF detect a finger, use camera position
       (more precise) with boosted confidence.
    2. If only ToF detects, map zone center to worksheet coords.
       Lower confidence but lighting-independent.
    3. If only camera detects, use as-is.
    4. If neither detects, return None.

    Args:
        camera_frame: Current camera frame (None to skip camera).
        camera_reference: Camera background reference (None to skip).
        tof_grid: Current ToF ranging frame (None to skip ToF).
        tof_baseline: ToF baseline distances (None to skip ToF).
        tof_threshold_mm: Minimum depth delta for ToF touch.
        worksheet_size: (width, height) of worksheet in pixels.

    Returns:
        Fused FingerDetection or None.
    """
    cam_finger = None
    tof_touches: list[TouchZone] = []

    # Camera detection
    if camera_frame is not None and camera_reference is not None:
        cam_finger = detect_finger(camera_frame, camera_reference)

    # ToF detection
    if tof_grid is not None and tof_baseline is not None:
        tof_touches = detect_touch_zones(
            tof_grid, tof_baseline, tof_threshold_mm
        )

    # Fusion
    if cam_finger and tof_touches:
        # Both agree — boost confidence
        return FingerDetection(
            x=cam_finger.x,
            y=cam_finger.y,
            confidence=min(cam_finger.confidence + 0.2, 1.0),
            contour_area=cam_finger.contour_area,
        )

    if tof_touches:
        # ToF only — pick the touch zone closest to the sensor
        # (smallest distance = most prominent finger)
        best = min(tof_touches, key=lambda t: t.distance_mm)
        x, y = zone_to_worksheet_xy(
            best.row,
            best.col,
            resolution=tof_grid.resolution,  # type: ignore[union-attr]
            worksheet_width=worksheet_size[0],
            worksheet_height=worksheet_size[1],
        )
        return FingerDetection(
            x=x,
            y=y,
            confidence=0.7,  # lower than camera — coarse position
            contour_area=0,
        )

    if cam_finger:
        # Camera only
        return cam_finger

    return None
