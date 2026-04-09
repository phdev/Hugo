"""VL53L7CX Time-of-Flight multizone ranging sensor.

8x8 grid of distance measurements over a 60°x60° FOV. Mounted
beside the projector looking down at the worksheet. Detects when
a finger rises from the table surface into the projection area,
independent of ambient light or projector output.

Hardware: VL53L7CX on I2C (SDA/SCL), optional LPn GPIO for
power control. Default I2C address 0x29.

The sensor returns a ZoneGrid — an 8x8 matrix of distances in mm.
Each cell covers roughly a 7.5°x7.5° slice of the FOV. When
mounted ~40cm above an 8.5x11" worksheet, each zone is about
5x5 cm — enough to tell which problem region a finger is in.
"""

from dataclasses import dataclass, field

import numpy as np


# ── Configuration ──

I2C_BUS: int = 1
I2C_ADDRESS: int = 0x29
# GPIO pin for LPn (low-power enable / reset), -1 = not connected
LPN_GPIO: int = -1

# Resolution: 16 (4x4) or 64 (8x8)
RESOLUTION: int = 64
# Ranging frequency in Hz (1–60, higher = more CPU)
RANGING_FREQ_HZ: int = 15


# ── Data types ──

@dataclass
class ZoneGrid:
    """One frame of ranging data from the VL53L7CX.

    Attributes:
        distances: 8x8 (or 4x4) grid of distances in mm. 0 = no target.
        statuses: Per-zone validity (0–255, 5 = valid, 9 = valid with
                  sigma clipping). Use is_valid() to check.
        resolution: 4 or 8 (side length of the grid).
        timestamp_ms: Sensor-reported timestamp in milliseconds.
    """

    distances: np.ndarray  # shape (resolution, resolution), dtype int16
    statuses: np.ndarray   # shape (resolution, resolution), dtype uint8
    resolution: int = 8
    timestamp_ms: int = 0

    def is_valid(self, row: int, col: int) -> bool:
        """Check if a zone measurement is valid."""
        return int(self.statuses[row, col]) in (5, 6, 9, 10)

    def valid_distances(self) -> np.ndarray:
        """Return distances with invalid zones masked as 0."""
        valid_mask = np.isin(self.statuses, [5, 6, 9, 10])
        return np.where(valid_mask, self.distances, 0)


@dataclass
class TouchZone:
    """A zone where a finger is detected close to the table surface.

    The sensor reads a baseline distance to the table/worksheet.
    When a finger is present, the distance in that zone drops
    significantly. This struct reports where and how close.
    """

    row: int
    col: int
    distance_mm: int
    delta_mm: int  # how much closer than the baseline


# ── Sensor lifecycle ──

def init(
    i2c_bus: int = I2C_BUS,
    i2c_address: int = I2C_ADDRESS,
    resolution: int = RESOLUTION,
    ranging_freq_hz: int = RANGING_FREQ_HZ,
    lpn_gpio: int = LPN_GPIO,
) -> None:
    """Initialize the VL53L7CX sensor.

    Configures I2C, sets resolution (4x4 or 8x8), ranging
    frequency, and starts continuous ranging. Call once at startup.

    Args:
        i2c_bus: I2C bus number (1 on most Pi models).
        i2c_address: 7-bit I2C address (default 0x29).
        resolution: 16 for 4x4 or 64 for 8x8.
        ranging_freq_hz: Measurements per second (1–60).
        lpn_gpio: BCM GPIO for LPn pin, -1 if not connected.
    """
    raise NotImplementedError


def shutdown() -> None:
    """Stop ranging and put the sensor into low-power mode."""
    raise NotImplementedError


def is_ready() -> bool:
    """Check if a new ranging frame is available."""
    raise NotImplementedError


# ── Reading data ──

def read_grid() -> ZoneGrid:
    """Read one frame of ranging data.

    Blocks until data is available (or times out). Returns the
    full zone grid with distances and validity statuses.
    """
    raise NotImplementedError


# ── Finger detection ──

def calibrate_baseline(num_frames: int = 10) -> np.ndarray:
    """Capture baseline distances to the table surface.

    Takes multiple frames with no hand present and averages them
    to establish the "empty table" distance for each zone.

    Args:
        num_frames: Number of frames to average.

    Returns:
        8x8 (or 4x4) array of baseline distances in mm.
    """
    raise NotImplementedError


def detect_touch_zones(
    grid: ZoneGrid,
    baseline: np.ndarray,
    threshold_mm: int = 40,
) -> list[TouchZone]:
    """Find zones where a finger is near the table surface.

    Compares current distances against the baseline. Zones where
    the distance is significantly shorter (a finger is closer to
    the sensor than the table) are returned as touch zones.

    Args:
        grid: Current ranging frame.
        baseline: Baseline from calibrate_baseline().
        threshold_mm: Minimum delta to consider a touch (default
                      40mm — a finger is ~10-15mm thick, plus margin).

    Returns:
        List of TouchZone objects for zones with detected fingers.
    """
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
                    row=r,
                    col=c,
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
    """Map a sensor zone (row, col) to worksheet pixel coordinates.

    Assumes the sensor FOV is aligned to cover the full worksheet.
    Returns the center point of the zone in worksheet space.

    Args:
        row: Zone row (0 = top).
        col: Zone column (0 = left).
        resolution: Grid side length (4 or 8).
        worksheet_width: Worksheet width in pixels.
        worksheet_height: Worksheet height in pixels.

    Returns:
        (x, y) in worksheet pixel coordinates.
    """
    zone_w = worksheet_width / resolution
    zone_h = worksheet_height / resolution
    x = int(col * zone_w + zone_w / 2)
    y = int(row * zone_h + zone_h / 2)
    return (x, y)
