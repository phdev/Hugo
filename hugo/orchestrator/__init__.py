"""Orchestrator module — main pipeline loop.

Ties together capture → vision → OCR → layout → classifier →
helpers → projection into a continuous loop. Manages state
transitions and error recovery.
"""
