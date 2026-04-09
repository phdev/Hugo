"""ReSpeaker 2-Mics Pi HAT V2.0 — voice pipeline on Pi 5.

Local mic capture from the ReSpeaker HAT (I2S via GPIO).
Runs openWakeWord locally on the Pi for "Hey Hugo" detection.
Sends audio to the Mac mini for whisper.cpp transcription.
Parses commands locally via hugo.voice.commands.
"""

import io
import logging
import time
from dataclasses import dataclass

import httpx
import numpy as np

from hugo.pi.config import SAMPLE_RATE, SERVER_BASE_URL, WAKE_PHRASE
from hugo.voice.commands import CommandType, VoiceCommand, parse_command

logger = logging.getLogger(__name__)


@dataclass
class VoiceState:
    """Tracks the voice pipeline state."""

    listening: bool = False
    wake_detected: bool = False
    wake_time: float = 0.0
    command_timeout_sec: float = 5.0

    @property
    def in_command_mode(self) -> bool:
        return (
            self.wake_detected
            and (time.monotonic() - self.wake_time) < self.command_timeout_sec
        )


def open_mic():
    """Open the ReSpeaker HAT mic as a PyAudio stream.

    Returns a PyAudio stream object. The ReSpeaker HAT appears as
    "seeed2micvoicec" in ALSA. The HAT provides hardware AEC and
    noise suppression.
    """
    try:
        import pyaudio
    except ImportError:
        raise RuntimeError(
            "pyaudio not installed. Install on Pi 5: pip install pyaudio"
        )

    pa = pyaudio.PyAudio()

    # Find the ReSpeaker device
    device_index = None
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        if "seeed" in info["name"].lower() or "respeaker" in info["name"].lower():
            device_index = i
            break

    if device_index is None:
        raise RuntimeError(
            "ReSpeaker HAT not found. Check that the HAT is seated "
            "and the driver is loaded: sudo dtoverlay seeed-2mic-voicecard"
        )

    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        input_device_index=device_index,
        frames_per_buffer=1024,
    )
    logger.info("ReSpeaker mic opened (device %d)", device_index)
    return stream


def check_wake_word(audio_chunk: np.ndarray) -> bool:
    """Check an audio chunk for the wake word using openWakeWord.

    Runs locally on the Pi 5. Returns True if "Hey Hugo" detected.
    """
    try:
        import openwakeword
        # Lazy-init the model
        if not hasattr(check_wake_word, "_model"):
            check_wake_word._model = openwakeword.Model(
                wakeword_models=["hey_hugo"],
            )
        prediction = check_wake_word._model.predict(audio_chunk)
        return any(v > 0.5 for v in prediction.values())
    except ImportError:
        logger.debug("openwakeword not installed, wake word disabled")
        return False
    except Exception as e:
        logger.debug(f"Wake word check failed: {e}")
        return False


def transcribe_audio(
    audio: np.ndarray,
    server_url: str = SERVER_BASE_URL,
    timeout: float = 5.0,
) -> str:
    """Send audio to the Mac mini for whisper.cpp transcription.

    Args:
        audio: int16 PCM samples at 16kHz.
        server_url: Mac mini inference server URL.
        timeout: Request timeout.

    Returns:
        Transcribed text, or empty string on failure.
    """
    buf = io.BytesIO()
    # Send as raw PCM — server knows format (16kHz mono int16)
    buf.write(audio.tobytes())
    buf.seek(0)

    try:
        response = httpx.post(
            f"{server_url}/transcribe",
            files={"audio": ("audio.pcm", buf, "application/octet-stream")},
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json().get("text", "")
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return ""


def process_voice_command(
    text: str,
    homework: dict | None = None,
) -> VoiceCommand:
    """Parse transcribed text into a voice command.

    Uses the local regex command parser. Falls back to the
    Mac mini for ambiguous commands if homework context is needed.
    """
    return parse_command(text)
