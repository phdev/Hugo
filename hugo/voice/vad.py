"""Voice Activity Detection — detect when someone is speaking.

Uses webrtcvad for lightweight, low-latency speech detection.
This tells the pipeline "a kid is talking" so we can pause
projection updates and listen for commands.
"""

from dataclasses import dataclass

import numpy as np

from hugo.voice.mic import AudioChunk


@dataclass
class VADState:
    """Tracks voice activity over time.

    Uses a ring buffer of frame decisions to smooth out
    momentary silence gaps in natural speech.
    """

    is_speaking: bool = False
    # Number of consecutive voiced/unvoiced frames
    voiced_count: int = 0
    unvoiced_count: int = 0
    # Thresholds (in frames) for state transitions
    onset_frames: int = 3    # voiced frames to trigger speaking
    offset_frames: int = 15  # unvoiced frames to trigger silence


def detect_voice_activity(
    chunk: AudioChunk,
    state: VADState,
    aggressiveness: int = 2,
) -> VADState:
    """Update voice activity state with a new audio chunk.

    Args:
        chunk: Audio from the microphone.
        state: Current VAD state (mutated in place).
        aggressiveness: webrtcvad aggressiveness (0-3).
            0 = least aggressive (more false positives).
            3 = most aggressive (may clip speech).
            2 is a good default for kids in a room.

    Returns:
        Updated VADState (same object, mutated).
    """
    raise NotImplementedError
