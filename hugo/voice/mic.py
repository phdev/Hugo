"""Microphone interface — XIAO ESP32-S3 onboard MEMS mic over WiFi.

The XIAO #1 streams raw PCM audio on :8081/audio (16kHz mono
16-bit). The Mac mini consumes this stream for wake word
detection and voice commands.
"""

import io
import logging
from dataclasses import dataclass

import httpx
import numpy as np

logger = logging.getLogger(__name__)

# ── Configuration ──

XIAO_CAM_HOST: str = "hugo-cam.local"  # same XIAO as camera
AUDIO_PORT: int = 8081
SAMPLE_RATE: int = 16000   # 16kHz
CHANNELS: int = 1          # mono
CHUNK_SIZE: int = 1024     # frames per chunk (~64ms at 16kHz)


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


def audio_stream(
    host: str = XIAO_CAM_HOST,
    port: int = AUDIO_PORT,
    chunk_size: int = CHUNK_SIZE,
):
    """Stream audio chunks from the XIAO over HTTP.

    The XIAO serves raw 16-bit PCM at 16kHz mono on :8081/audio.

    Yields:
        AudioChunk objects.
    """
    url = f"http://{host}:{port}/audio"
    bytes_per_chunk = chunk_size * 2  # 16-bit = 2 bytes per sample

    with httpx.stream("GET", url, timeout=None) as response:
        buffer = b""
        for data in response.iter_bytes():
            buffer += data
            while len(buffer) >= bytes_per_chunk:
                raw = buffer[:bytes_per_chunk]
                buffer = buffer[bytes_per_chunk:]
                samples = np.frombuffer(raw, dtype=np.int16)
                yield AudioChunk(
                    samples=samples,
                    sample_rate=SAMPLE_RATE,
                    channels=CHANNELS,
                )


def is_audio_available(
    host: str = XIAO_CAM_HOST,
    port: int = AUDIO_PORT,
) -> bool:
    """Check if the XIAO audio stream is reachable."""
    try:
        r = httpx.get(f"http://{host}:{port}/status", timeout=2.0)
        return r.status_code == 200
    except Exception:
        return False
