"""Wake word detection — "Hey Hugo" via whisper.cpp on Mac mini.

Listens for the wake phrase in the audio stream. Uses whisper.cpp
running locally on the Mac mini for keyword spotting — more
accurate than PocketSphinx and runs fast on the M4.

After wake word detection, the system enters command-listening
mode for a few seconds to hear what the kid wants.
"""

from dataclasses import dataclass

from hugo.voice.mic import AudioChunk


WAKE_PHRASE: str = "hey hugo"

# How long command mode stays active after wake word (seconds)
COMMAND_TIMEOUT_SEC: float = 5.0


@dataclass
class WakeWordState:
    """Tracks wake word detection state."""

    detected: bool = False
    time_since_detection: float = 0.0
    command_timeout_sec: float = COMMAND_TIMEOUT_SEC

    @property
    def in_command_mode(self) -> bool:
        return self.detected and self.time_since_detection < self.command_timeout_sec


def check_wake_word(
    chunk: AudioChunk,
    state: WakeWordState,
) -> WakeWordState:
    """Check an audio chunk for the wake word.

    Uses whisper.cpp on the Mac mini for transcription, then
    checks if the wake phrase appears in the text.

    Args:
        chunk: Audio from the XIAO mic stream.
        state: Current detection state (mutated in place).

    Returns:
        Updated WakeWordState.
    """
    raise NotImplementedError
