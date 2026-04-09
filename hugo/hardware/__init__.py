"""Hardware module — WiFi sensor clients.

All desk hardware is XIAO ESP32-S3 boards streaming over WiFi.
The Mac mini consumes these streams via HTTP. No direct I2C,
no CEC, no HDMI — everything is networked.

Desk sensors:
- XIAO #1: OV5640 camera + onboard MEMS mic (hugo-cam.local)
- XIAO #2: VL53L7CX ToF sensor (hugo-tof.local)
- Kodak Luma 350: receives AirPlay from Mac mini
"""
