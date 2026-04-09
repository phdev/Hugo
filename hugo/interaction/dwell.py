"""Dwell timer — triggers a help button after sustained finger press.

Manages the state machine for each help button:
  idle → hover → pressing (with progress) → triggered

A finger must remain on the button for `dwell_ms` milliseconds
to trigger the hint. Visual feedback (button expansion) is
proportional to elapsed dwell time. If the finger leaves early
the button resets to idle.
"""

import time

from hugo.interaction.finger_detect import FingerDetection, point_in_circle
from hugo.interaction.help_buttons import HelpButton


# How long a finger must dwell to trigger (milliseconds)
DWELL_MS = 800

# How close the finger must be to start hover state (pixels)
HOVER_RADIUS_MULTIPLIER = 2.5


def update_button_states(
    buttons: list[HelpButton],
    finger: FingerDetection | None,
    dwell_ms: int = DWELL_MS,
) -> HelpButton | None:
    """Update all button states based on current finger position.

    Call this once per frame. Returns the button that was just
    triggered (transitioned to "triggered" state), or None.

    Args:
        buttons: All help buttons on the current worksheet.
        finger: Current finger detection, or None if no finger.
        dwell_ms: Required hold duration in milliseconds.

    Returns:
        The HelpButton that was triggered this frame, or None.
    """
    triggered = None
    now = time.monotonic() * 1000  # ms

    for btn in buttons:
        if finger is None:
            # No finger — reset everything
            btn.state = "idle"
            btn.press_progress = 0.0
            btn._press_start = None  # type: ignore[attr-defined]
            continue

        on_button = point_in_circle(
            finger.x, finger.y, btn.cx, btn.cy, btn.radius
        )
        near_button = point_in_circle(
            finger.x,
            finger.y,
            btn.cx,
            btn.cy,
            int(btn.radius * HOVER_RADIUS_MULTIPLIER),
        )

        if on_button:
            if btn.state in ("idle", "hover"):
                btn.state = "pressing"
                btn._press_start = now  # type: ignore[attr-defined]
                btn.press_progress = 0.0
            elif btn.state == "pressing":
                start = getattr(btn, "_press_start", now)
                elapsed = now - start
                btn.press_progress = min(elapsed / dwell_ms, 1.0)
                if btn.press_progress >= 1.0:
                    btn.state = "triggered"
                    triggered = btn
        elif near_button:
            btn.state = "hover"
            btn.press_progress = 0.0
            btn._press_start = None  # type: ignore[attr-defined]
        else:
            btn.state = "idle"
            btn.press_progress = 0.0
            btn._press_start = None  # type: ignore[attr-defined]

    return triggered
