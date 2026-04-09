"""Kodak Luma 150 projector control via HDMI-CEC.

Uses cec-client to power on/off the projector and manage
HDMI input selection.
"""


def power_on() -> None:
    """Power on the projector via CEC."""
    raise NotImplementedError


def power_off() -> None:
    """Power off the projector via CEC."""
    raise NotImplementedError


def is_powered_on() -> bool:
    """Check if the projector is currently powered on."""
    raise NotImplementedError
