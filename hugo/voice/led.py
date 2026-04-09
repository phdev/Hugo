"""ReSpeaker Lite LED control.

The ReSpeaker Lite has a WS2812 RGB LED. We use it to give
visual feedback for voice interaction state:
- Off: idle, not listening
- Pulsing cyan: listening for wake word
- Solid green: wake word detected, listening for command
- Yellow flash: processing command
- Red flash: didn't understand
"""

from enum import Enum


class LEDState(Enum):
    """LED feedback states."""

    OFF = "off"
    LISTENING = "listening"         # pulsing cyan
    COMMAND_MODE = "command_mode"   # solid green
    PROCESSING = "processing"       # yellow flash
    ERROR = "error"                 # red flash
    SUCCESS = "success"             # green flash


def set_led(state: LEDState) -> None:
    """Set the ReSpeaker LED to reflect the current voice state.

    Uses the ReSpeaker's USB HID interface to control the
    onboard WS2812 LED.
    """
    raise NotImplementedError
