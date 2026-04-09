"""VL53L7CX ToF sensor via XIAO ESP32-S3 over WiFi.

The XIAO #2 reads the VL53L7CX over I2C and exposes an HTTP
JSON endpoint at :8080/depth. The Mac mini polls this at ~15Hz.

8x8 grid of distance measurements over a 90° diagonal FOV.
Mounted inside the enclosure looking down at the worksheet.
Detects when a finger touches the projected help buttons.
"""

import logging
from dataclasses import dataclass

import httpx
import numpy as np

logger = logging.getLogger(__name__)

# ── Configuration ──

XIAO_TOF_HOST: str = "hugo-tof.local"
XIAO_TOF_PORT: int = 8080
POLL_TIMEOUT: float = 0.5  # fast timeout for 15Hz polling


# ── Data types ──

@dataclass
class ZoneGrid:
    """One frame of ranging data from the VL53L7CX.

    Attributes:
        distances: 8x8 grid of distances in mm. 0 = no target.
        statuses: Per-zone validity. 5 = valid, 9 = valid with clipping.
        resolution: 4 or 8 (side length of the grid).
        timestamp_ms: Sensor-reported timestamp in milliseconds.
    """

    distances: np.ndarray  # shape (resolution, resolution), dtype int16
    statuses: np.ndarray   # shape (resolution, resolution), dtype uint8
    resolution: int = 8
    timestamp_ms: int = 0

    def is_valid(self, row: int, col: int) -> bool:
        return int(self.statuses[row, col]) in (5, 6, 9, 10)

    def valid_distances(self) -> np.ndarray:
        valid_mask = np.isin(self.statuses, [5, 6, 9, 10])
        return np.where(valid_mask, self.distances, 0)


@dataclass
class TouchZone:
    """A zone where a finger is detected close to the table."""

    row: int
    col: int
    distance_mm: int
    delta_mm: int  # how much closer than baseline


# ── HTTP interface ──

def read_grid(
    host: str = XIAO_TOF_HOST,
    port: int = XIAO_TOF_PORT,
) -> ZoneGrid:
    """Read one frame of ranging data from the XIAO over HTTP.

    The XIAO serves JSON: {"zones": [[d00..d07], ...], "fps": 15.2}

    Returns:
        ZoneGrid with distances and all-valid statuses.
    """
    url = f"http://{host}:{port}/depth"
    try:
        response = httpx.get(url, timeout=POLL_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        zones = data["zones"]
        res = len(zones)
        distances = np.array(zones, dtype=np.int16)
        # XIAO firmware doesn't report per-zone status, assume all valid
        statuses = np.full((res, res), 5, dtype=np.uint8)

        return ZoneGrid(
            distances=distances,
            statuses=statuses,
            resolution=res,
        )
    except httpx.ConnectError:
        raise ConnectionError(
            f"Cannot reach XIAO ToF at {url}. "
            "Check WiFi and that the XIAO is powered on."
        )
    except (httpx.TimeoutException, Exception) as e:
        logger.warning(f"ToF read failed: {e}")
        # Return empty grid
        return ZoneGrid(
            distances=np.zeros((8, 8), dtype=np.int16),
            statuses=np.zeros((8, 8), dtype=np.uint8),
        )


def is_available(
    host: str = XIAO_TOF_HOST,
    port: int = XIAO_TOF_PORT,
) -> bool:
    """Check if the XIAO ToF sensor is reachable."""
    try:
        r = httpx.get(f"http://{host}:{port}/status", timeout=2.0)
        return r.status_code == 200
    except Exception:
        return False


# ── Finger detection (runs on Mac mini, pure computation) ──

def calibrate_baseline(
    num_frames: int = 10,
    host: str = XIAO_TOF_HOST,
    port: int = XIAO_TOF_PORT,
) -> np.ndarray:
    """Capture baseline distances to the table surface.

    Takes multiple frames with no hand present and averages them.

    Args:
        num_frames: Number of frames to average.
        host: XIAO ToF hostname.
        port: XIAO ToF port.

    Returns:
        8x8 array of baseline distances in mm.
    """
    import time
    frames = []
    for _ in range(num_frames):
        grid = read_grid(host, port)
        valid = grid.valid_distances()
        if valid.any():
            frames.append(valid.astype(np.float32))
        time.sleep(1.0 / 15)  # match 15Hz polling rate

    if not frames:
        return np.zeros((8, 8), dtype=np.int16)

    return np.mean(frames, axis=0).astype(np.int16)


def detect_touch_zones(
    grid: ZoneGrid,
    baseline: np.ndarray,
    threshold_mm: int = 40,
) -> list[TouchZone]:
    """Find zones where a finger is near the table surface."""
    touches = []
    valid = grid.valid_distances()
    res = grid.resolution

    for r in range(res):
        for c in range(res):
            if valid[r, c] == 0:
                continue
            delta = int(baseline[r, c]) - int(valid[r, c])
            if delta >= threshold_mm:
                touches.append(TouchZone(
                    row=r, col=c,
                    distance_mm=int(valid[r, c]),
                    delta_mm=delta,
                ))
    return touches


def zone_to_worksheet_xy(
    row: int,
    col: int,
    resolution: int = 8,
    worksheet_width: int = 640,
    worksheet_height: int = 828,
) -> tuple[int, int]:
    """Map a sensor zone (row, col) to worksheet pixel coordinates."""
    zone_w = worksheet_width / resolution
    zone_h = worksheet_height / resolution
    x = int(col * zone_w + zone_w / 2)
    y = int(row * zone_h + zone_h / 2)
    return (x, y)
