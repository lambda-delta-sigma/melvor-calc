from melvor_calc.cli import run


class ScriptedInput:
    """Feeds queued answers to prompts; raises EOFError once exhausted."""

    def __init__(self, answers):
        self._answers = list(answers)

    def __call__(self, prompt: str) -> str:
        if not self._answers:
            raise EOFError
        return self._answers.pop(0)


class RaisingInput:
    """Raises the given exception on the Nth call (0-indexed)."""

    def __init__(self, answers, raise_at, exc):
        self._answers = list(answers)
        self._raise_at = raise_at
        self._exc = exc
        self._calls = 0

    def __call__(self, prompt: str) -> str:
        if self._calls == self._raise_at:
            self._calls += 1
            raise self._exc
        value = self._answers[self._calls]
        self._calls += 1
        return value


def _run(reader):
    """Run the CLI against ``reader``; returns (exit_code, output_text)."""
    lines = []
    exit_code = run(reader, lines.append)
    return exit_code, "\n".join(lines)


def test_exact_xp_happy_path():
    exit_code, text = _run(ScriptedInput(["1", "1000", "10", "100", "2.5"]))

    assert exit_code == 0
    assert "Target XP:       1,154" in text
    assert "Remaining XP:    154" in text
    assert "Actions needed:  2" in text
    assert "Estimated time:  5 seconds" in text
    assert "Estimate assumption" not in text


def test_level_only_happy_path_shows_assumption():
    exit_code, text = _run(ScriptedInput(["2", "2", "3", "50", "3"]))

    assert exit_code == 0
    assert "Estimate assumption: current level was treated as exactly 0% complete." in text
    assert "Enter exact XP for a more accurate result." in text
    assert "Remaining XP:    91" in text
    assert "Actions needed:  2" in text
    assert "Estimated time:  6 seconds" in text


def test_already_at_target():
    exit_code, text = _run(ScriptedInput(["1", "13034431", "99", "100", "2"]))

    assert exit_code == 0
    assert "Target already reached." in text
    assert "Actions needed: 0" in text
    assert "Estimated time: 0 seconds" in text


def test_invalid_menu_choice_retries_only_choice():
    exit_code, text = _run(ScriptedInput(["7", "1", "1000", "10", "100", "2.5"]))

    assert exit_code == 0
    assert "Enter one of: 1, 2." in text


def test_invalid_numeric_input_retries_only_that_field():
    # Target level 120.5 invalid, then 120 valid.
    exit_code, text = _run(ScriptedInput(["1", "1000", "120.5", "120", "100", "2.5"]))

    assert exit_code == 0
    assert "Enter a whole-number level" in text


def test_comma_formatted_current_xp_accepted():
    exit_code, text = _run(ScriptedInput(["1", "13,034,431", "99", "100", "2"]))

    assert exit_code == 0
    assert "Target already reached." in text


def test_malformed_commas_rejected_then_corrected():
    exit_code, text = _run(ScriptedInput(["1", "1,2,3", "1000", "10", "100", "2.5"]))

    assert exit_code == 0
    assert "Current XP must be a whole number of 0 or more." in text


def test_full_input_correction_scenario():
    answers = [
        "7",
        "1",
        "-1",
        "1000",
        "120.5",
        "120",
        "0",
        "25.5",
        "NaN",
        "1.2",
    ]
    exit_code, text = _run(ScriptedInput(answers))

    assert exit_code == 0
    assert "Enter one of: 1, 2." in text
    assert "Current XP must be a whole number of 0 or more." in text
    assert "Enter a whole-number level" in text
    assert "XP per action must be a number greater than 0." in text
    assert "Action time must be a number of seconds greater than 0." in text
    assert "Actions needed:" in text


def test_keyboard_interrupt_cancels_without_traceback():
    exit_code, text = _run(RaisingInput(["1"], raise_at=1, exc=KeyboardInterrupt()))

    assert exit_code != 0
    assert "Cancelled." in text


def test_eof_cancels_without_traceback():
    # ScriptedInput exhausts after the menu choice, so the next read hits EOF.
    exit_code, text = _run(ScriptedInput(["1"]))

    assert exit_code != 0
    assert "Cancelled." in text
