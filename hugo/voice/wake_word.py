"""Wake word detection — "Hey Hugo" activation.

Listens for the wake phrase to activate voice command mode.
Uses PocketSphinx for offline keyword spotting — no cloud
service needed, runs entirely on the Pi 5.

After wake word detection, the system enters command-listening
mode for a few seconds to hear what the kid wants.
"""

from dataclasses import dataclass

from hugo.voice.mic import AudioChunk


# The wake phrase. PocketSphinx does phonetic matching so
# slight mispronunciations ("hey hoo-go") still work.
WAKE_PHRASE: str = "hey hugo"

# How sensitive the detector is (lower = more sensitive,
# more false positives). Range roughly 1e-50 to 1e-1.
DEFAULT_SENSITIVITY: float = 1e-20


@dataclass
class WakeWordState:
    """Tracks wake word detection state."""

    detected: bool = False
    # Seconds since last detection (for timeout)
    time_since_detection: float = 0.0
    # How long command mode stays active after wake word
    command_timeout_sec: float = 5.0

    @property
    def in_command_mode(self) -> bool:
        """True if wake word was recently heard."""
        return self.detected and self.time_since_detection < self.command_timeout_sec


def init_detector(
    wake_phrase: str = WAKE_PHRASE,
    sensitivity: float = DEFAULT_SENSITIVITY,
) -> None:
    """Initialize the PocketSphinx keyword spotter.

    Call once at startup. Loads the acoustic model and
    configures the keyword with the given sensitivity.
    """
    raise NotImplementedError


def check_wake_word(
    chunk: AudioChunk,
    state: WakeWordState,
) -> WakeWordState:
    """Check an audio chunk for the wake word.

    Args:
        chunk: Audio from the microphone.
        state: Current detection state (mutated in place).

    Returns:
        Updated WakeWordState.
    """
    raise NotImplementedError
