"""Interaction module — finger detection and help button triggers.

Combines projected help-button targets with camera-based finger
detection and dwell timing. The projector places a small help icon
in the left margin next to each problem. The camera watches for a
finger occluding (pressing) that icon. A dwell timer triggers the
hint after a sustained press, with visual feedback (the icon
expands while the finger is held).
"""
