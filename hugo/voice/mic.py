"""ReSpeaker Lite microphone interface.

Handles audio capture from the ReSpeaker Lite USB device.
The XMOS XU316 chip provides hardware noise suppression and
echo cancellation — important since the kid is sitting right
next to the device and ambient room noise is typical.
"""

from dataclasses import dataclass

import numpy as np


# ── Configuration ──

# ReSpeaker Lite appears as a USB audio device.
# Find the right device index with: python -m pyaudio
DEVICE_NAME: str = "ReSpeaker"
SAMPLE_RATE: int = 16000   # 16kHz is standard for speech
CHANNELS: int = 1          # mono (mixed from 2-mic array)
CHUNK_SIZE: int = 1024     # frames per read


@dataclass
class AudioChunk:
    """A chunk of audio from the microphone."""

    samples: np.ndarray  # int16 PCM samples
    sample_rate: int
    channels: int

    @property
    def duration_ms(self) -> float:
        return len(self.samples) / self.sample_rate * 1000

    @property
    def rms(self) -> float:
        """Root mean square — rough loudness measure."""
        return float(np.sqrt(np.mean(self.samples.astype(np.float32) ** 2)))


def find_device_index(name: str = DEVICE_NAME) -> int | None:
    """Find the PyAudio device index for the ReSpeaker.

    Scans available audio input devices for one matching the name.
    Returns None if not found (e.g., running on a laptop without
    the hardware).
    """
    raise NotImplementedError


def open_stream(
    device_index: int | None = None,
    sample_rate: int = SAMPLE_RATE,
    channels: int = CHANNELS,
    chunk_size: int = CHUNK_SIZE,
):
    """Open a PyAudio input stream from the ReSpeaker.

    Returns a context manager that yields AudioChunk objects.
    If device_index is None, attempts to auto-detect the ReSpeaker.
    """
    raise NotImplementedError


def read_chunk(stream) -> AudioChunk:
    """Read one chunk of audio from an open stream."""
    raise NotImplementedError
