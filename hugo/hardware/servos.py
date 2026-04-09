"""Servo control for lift/pan/tilt mechanism.

Controls the Actuonix L12-50 linear servo (lift) and two MG90S
micro servos (pan/tilt) via gpiozero/pigpio.
"""


def set_lift(position: float) -> None:
    """Set the lift servo position.

    Args:
        position: 0.0 (fully retracted) to 1.0 (fully extended).
    """
    raise NotImplementedError


def set_pan(angle: float) -> None:
    """Set the pan servo angle.

    Args:
        angle: Angle in degrees, centered at 0.
    """
    raise NotImplementedError


def set_tilt(angle: float) -> None:
    """Set the tilt servo angle.

    Args:
        angle: Angle in degrees, centered at 0.
    """
    raise NotImplementedError


def home() -> None:
    """Move all servos to their home/default positions."""
    raise NotImplementedError
