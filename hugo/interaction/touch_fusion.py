"""Fused touch detection — combines camera + ToF sensor over WiFi.

Both sensors stream to the Mac mini over HTTP:
- Camera: MJPEG from XIAO #1 (fine-grained fingertip position)
- ToF: JSON depth grid from XIAO #2 (lighting-independent zone detection)

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

    Both sensors stream over WiFi to the Mac mini. Priority:
    1. Both detect → camera position with boosted confidence.
    2. ToF only → coarse zone center (lighting-independent).
    3. Camera only → as-is.
    4. Neither → None.
    """
    cam_finger = None
    tof_touches: list[TouchZone] = []

    if camera_frame is not None and camera_reference is not None:
        cam_finger = detect_finger(camera_frame, camera_reference)

    if tof_grid is not None and tof_baseline is not None:
        tof_touches = detect_touch_zones(
            tof_grid, tof_baseline, tof_threshold_mm
        )

    if cam_finger and tof_touches:
        return FingerDetection(
            x=cam_finger.x,
            y=cam_finger.y,
            confidence=min(cam_finger.confidence + 0.2, 1.0),
            contour_area=cam_finger.contour_area,
        )

    if tof_touches:
        best = min(tof_touches, key=lambda t: t.distance_mm)
        x, y = zone_to_worksheet_xy(
            best.row,
            best.col,
            resolution=tof_grid.resolution,  # type: ignore[union-attr]
            worksheet_width=worksheet_size[0],
            worksheet_height=worksheet_size[1],
        )
        return FingerDetection(
            x=x, y=y, confidence=0.7, contour_area=0,
        )

    if cam_finger:
        return cam_finger

    return None
