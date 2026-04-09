"""Tests for voice module."""

import numpy as np

from hugo.voice.commands import CommandType, VoiceCommand, parse_command
from hugo.voice.mic import AudioChunk


# ── AudioChunk ──

def test_audio_chunk_duration():
    samples = np.zeros(16000, dtype=np.int16)  # 1 second at 16kHz
    chunk = AudioChunk(samples=samples, sample_rate=16000, channels=1)
    assert chunk.duration_ms == 1000.0


def test_audio_chunk_rms():
    samples = np.array([100, -100, 100, -100], dtype=np.int16)
    chunk = AudioChunk(samples=samples, sample_rate=16000, channels=1)
    assert chunk.rms == 100.0


def test_audio_chunk_rms_silence():
    samples = np.zeros(100, dtype=np.int16)
    chunk = AudioChunk(samples=samples, sample_rate=16000, channels=1)
    assert chunk.rms == 0.0


# ── Command parsing ──

def test_help_with_number():
    cmd = parse_command("help me with number three")
    assert cmd.command == CommandType.HELP_WITH_NUMBER
    assert cmd.problem_number == 3


def test_help_with_digit():
    cmd = parse_command("help with 5")
    assert cmd.command == CommandType.HELP_WITH_NUMBER
    assert cmd.problem_number == 5


def test_help_shorthand():
    cmd = parse_command("hint number two")
    assert cmd.command == CommandType.HELP_WITH_NUMBER
    assert cmd.problem_number == 2


def test_help_show():
    cmd = parse_command("show me number four")
    assert cmd.command == CommandType.HELP_WITH_NUMBER
    assert cmd.problem_number == 4


def test_help_no_number():
    cmd = parse_command("help me with this")
    assert cmd.command == CommandType.HELP_WITH_NUMBER
    assert cmd.problem_number is None
    assert cmd.confidence < 0.9


def test_next():
    cmd = parse_command("next one")
    assert cmd.command == CommandType.NEXT


def test_skip():
    cmd = parse_command("skip")
    assert cmd.command == CommandType.NEXT


def test_previous():
    cmd = parse_command("go back")
    assert cmd.command == CommandType.PREVIOUS


def test_dismiss():
    cmd = parse_command("go away")
    assert cmd.command == CommandType.DISMISS


def test_dismiss_done():
    cmd = parse_command("I'm done")
    assert cmd.command == CommandType.DISMISS


def test_read():
    cmd = parse_command("read it to me")
    assert cmd.command == CommandType.READ_PROBLEM


def test_unknown():
    cmd = parse_command("I like pizza")
    assert cmd.command == CommandType.UNKNOWN


def test_empty():
    cmd = parse_command("")
    assert cmd.command == CommandType.UNKNOWN


# ── Import smoke tests ──

def test_import_voice_mic():
    from hugo.voice import mic
    assert hasattr(mic, "AudioChunk")
    assert hasattr(mic, "audio_stream")
    assert hasattr(mic, "is_audio_available")


def test_import_voice_vad():
    from hugo.voice import vad
    assert hasattr(vad, "VADState")
    assert hasattr(vad, "detect_voice_activity")


def test_import_voice_wake_word():
    from hugo.voice import wake_word
    assert hasattr(wake_word, "WakeWordState")
    assert hasattr(wake_word, "check_wake_word")
    assert hasattr(wake_word, "WAKE_PHRASE")
    assert wake_word.WAKE_PHRASE == "hey hugo"


def test_import_voice_led():
    from hugo.voice import led
    assert hasattr(led, "LEDState")
    assert hasattr(led, "set_led")


def test_import_voice_commands():
    from hugo.voice import commands
    assert hasattr(commands, "CommandType")
    assert hasattr(commands, "parse_command")
