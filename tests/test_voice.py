"""Tests for voice command parsing."""

from hugo.voice.commands import CommandType, parse_command


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
