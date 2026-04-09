"""SparkFun Qwiic Mini VL53L5CX — I2C tap detection on Pi 5.

Polls the 8×8 ToF sensor at 15Hz. Detects tap events: a zone's
distance drops >30mm below baseline then returns within 500ms.
Maps tapped zone to projected button position via calibration.

Wiring: Qwiic cable through ReSpeaker HAT pass-through header.
SDA=GPIO2 (Pin3), SCL=GPIO3 (Pin5), 3.3V=Pin1, GND=Pin6.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from hugo.pi.config import (
    TOF_DEBOUNCE_MS,
    TOF_I2C_ADDRESS,
    TOF_I2C_BUS,
    TOF_POLL_HZ,
    TOF_TAP_THRESHOLD_MM,
    TOF_TAP_TIMEOUT_MS,
)

logger = logging.getLogger(__name__)


@dataclass
class TapEvent:
    """A detected tap on the worksheet."""

    row: int
    col: int
    problem_id: int | None  # mapped via calibration, None if unmapped
    timestamp: float


@dataclass
class ZoneState:
    """Per-zone state for tap detection."""

    baseline_mm: int = 0
    pressed: bool = False
    press_time: float = 0.0
    last_tap_time: float = 0.0


@dataclass
class ToFState:
    """Full sensor state."""

    zones: list[list[ZoneState]] = field(default_factory=lambda: [
        [ZoneState() for _ in range(8)] for _ in range(8)
    ])
    calibrated: bool = False
    # Maps (row, col) → problem_id. Loaded from calibration.json.
    zone_map: dict[tuple[int, int], int] = field(default_factory=dict)


def calibrate(state: ToFState, num_frames: int = 30) -> ToFState:
    """Calibrate baseline distances from the desk surface.

    Reads num_frames over ~2 seconds with no hand present,
    averages per-zone distances.

    Args:
        state: ToF state (mutated in place).
        num_frames: Frames to average.

    Returns:
        Updated state with baselines set.
    """
    try:
        sensor = _get_sensor()
    except RuntimeError:
        logger.warning("ToF sensor not available, using stub baselines")
        for r in range(8):
            for c in range(8):
                state.zones[r][c].baseline_mm = 400  # default desk height
        state.calibrated = True
        return state

    frames = []
    for _ in range(num_frames):
        grid = _read_grid(sensor)
        if grid is not None:
            frames.append(grid)
        time.sleep(1.0 / TOF_POLL_HZ)

    if frames:
        avg = np.mean(frames, axis=0)
        for r in range(8):
            for c in range(8):
                state.zones[r][c].baseline_mm = int(avg[r][c])

    state.calibrated = True
    logger.info("ToF calibrated with %d frames", len(frames))
    return state


def poll_once(state: ToFState) -> TapEvent | None:
    """Read one frame and check for tap events.

    A tap is: zone drops >threshold below baseline, then returns
    within timeout. Debounced per zone.

    Returns:
        TapEvent if a tap was detected this frame, None otherwise.
    """
    try:
        sensor = _get_sensor()
        grid = _read_grid(sensor)
    except RuntimeError:
        return None

    if grid is None:
        return None

    now = time.monotonic()

    for r in range(8):
        for c in range(8):
            zs = state.zones[r][c]
            dist = int(grid[r][c])
            delta = zs.baseline_mm - dist

            if not zs.pressed and delta >= TOF_TAP_THRESHOLD_MM:
                # Finger down
                zs.pressed = True
                zs.press_time = now

            elif zs.pressed and delta < TOF_TAP_THRESHOLD_MM:
                # Finger up — was it a tap?
                zs.pressed = False
                hold_ms = (now - zs.press_time) * 1000
                since_last = (now - zs.last_tap_time) * 1000

                if hold_ms < TOF_TAP_TIMEOUT_MS and since_last > TOF_DEBOUNCE_MS:
                    zs.last_tap_time = now
                    problem_id = state.zone_map.get((r, c))
                    return TapEvent(
                        row=r, col=c,
                        problem_id=problem_id,
                        timestamp=now,
                    )

    return None


def load_zone_map(path: str = "calibration.json") -> dict[tuple[int, int], int]:
    """Load zone-to-problem mapping from calibration file.

    Format: {"zone_map": {"3,4": 1, "3,5": 1, "5,4": 2, ...}}
    """
    import json
    from pathlib import Path

    p = Path(path)
    if not p.exists():
        logger.warning(f"No calibration file at {path}")
        return {}

    data = json.loads(p.read_text())
    mapping = {}
    for key, pid in data.get("zone_map", {}).items():
        r, c = key.split(",")
        mapping[(int(r), int(c))] = pid
    return mapping


# ── Sensor access (lazy init) ──

_sensor = None


def _get_sensor():
    """Lazy-init the VL53L5CX sensor."""
    global _sensor
    if _sensor is not None:
        return _sensor

    try:
        import qwiic_vl53l5cx
        _sensor = qwiic_vl53l5cx.QwiicVL53L5CX()
        if not _sensor.is_connected():
            raise RuntimeError("VL53L5CX not found on I2C bus")
        _sensor.begin()
        _sensor.set_resolution(64)  # 8×8
        _sensor.set_ranging_frequency_hz(TOF_POLL_HZ)
        _sensor.start_ranging()
        logger.info("VL53L5CX initialized at 0x%02x, %dHz", TOF_I2C_ADDRESS, TOF_POLL_HZ)
        return _sensor
    except ImportError:
        raise RuntimeError(
            "sparkfun-qwiic-vl53l5cx not installed. "
            "Install on Pi 5: pip install sparkfun-qwiic-vl53l5cx"
        )


def _read_grid(sensor) -> np.ndarray | None:
    """Read one 8×8 distance grid from the sensor."""
    try:
        if sensor.check_for_data_ready():
            data = sensor.get_ranging_data()
            distances = np.array(
                data.distance_mm[:64], dtype=np.int16
            ).reshape(8, 8)
            return distances
    except Exception as e:
        logger.debug(f"ToF read error: {e}")
    return None
