"""Hardware module — projector and ToF sensor control.

Manages the Kodak Luma 150 via HDMI-CEC (cec-client) and the
VL53L7CX ToF sensor via I2C. The projector, camera, and ToF
sensor are fixed-mounted inside the enclosure with pre-angled
cutouts — no servos or moving parts.
"""
