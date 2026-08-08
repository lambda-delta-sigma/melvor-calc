from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Callable

from melvor_calc.calculator import (
    calculate_training,
    request_from_current_level,
    request_from_exact_xp,
)
from melvor_calc.experience import (
    MAX_SUPPORTED_LEVEL,
    MIN_SUPPORTED_LEVEL,
    ExperienceValidationError,
)
from melvor_calc.formatting import format_decimal, format_duration, format_int
from melvor_calc.models import CalculationValidationError, ProgressSource, TrainingResult

ReadFunc = Callable[[str], str]
WriteFunc = Callable[[str], None]

_CHOICE_EXACT_XP = "1"
_CHOICE_LEVEL_ONLY = "2"

_LEVEL_ERROR = f"Enter a whole-number level from {MIN_SUPPORTED_LEVEL} through {MAX_SUPPORTED_LEVEL}."
_CURRENT_XP_ERROR = "Current XP must be a whole number of 0 or more."
_XP_PER_ACTION_ERROR = "XP per action must be a number greater than 0."
_ACTION_SECONDS_ERROR = "Action time must be a number of seconds greater than 0."

_XP_TEXT_PATTERN = re.compile(r"^(\d+|\d{1,3}(,\d{3})+)$")


class _Cancelled(Exception):
    """Raised internally when the user cancels via Ctrl+C or EOF."""


def _read(read: ReadFunc, prompt: str) -> str:
    try:
        return read(prompt)
    except (EOFError, KeyboardInterrupt):
        raise _Cancelled from None


def _prompt_choice(read: ReadFunc, write: WriteFunc, prompt: str, valid: tuple[str, ...]) -> str:
    while True:
        raw = _read(read, prompt).strip()
        if raw in valid:
            return raw
        write(f"Enter one of: {', '.join(valid)}.")


def _parse_level(raw: str) -> int:
    text = raw.strip()
    try:
        value = int(text)
    except ValueError:
        raise ExperienceValidationError(_LEVEL_ERROR) from None
    if not (MIN_SUPPORTED_LEVEL <= value <= MAX_SUPPORTED_LEVEL):
        raise ExperienceValidationError(_LEVEL_ERROR)
    return value


def _parse_current_xp(raw: str) -> int:
    text = raw.strip()
    if not _XP_TEXT_PATTERN.match(text):
        raise CalculationValidationError(_CURRENT_XP_ERROR)
    value = int(text.replace(",", ""))
    if value < 0:
        raise CalculationValidationError(_CURRENT_XP_ERROR)
    return value


def _parse_positive_decimal(raw: str, error_message: str) -> Decimal:
    text = raw.strip()
    try:
        value = Decimal(text)
    except InvalidOperation:
        raise CalculationValidationError(error_message) from None
    if not value.is_finite() or value <= 0:
        raise CalculationValidationError(error_message)
    return value


def _prompt_value(read: ReadFunc, write: WriteFunc, prompt: str, parse: Callable[[str], object]):
    while True:
        raw = _read(read, prompt)
        try:
            return parse(raw)
        except ValueError as exc:
            write(str(exc))


def _render_result(write: WriteFunc, result: TrainingResult) -> None:
    if result.progress_source is ProgressSource.LEVEL_MINIMUM:
        write(
            "Estimate assumption: current level was treated as exactly 0% "
            "complete."
        )
        write("Enter exact XP for a more accurate result.")
        write("")

    write(f"Target XP:       {format_int(result.target_xp)}")
    write(f"Current XP:      {format_int(result.current_xp)}")
    write(f"Remaining XP:    {format_int(result.remaining_xp)}")
    write(f"XP per hour:     {format_decimal(result.xp_per_hour)}")

    if result.actions_required == 0:
        write("Target already reached.")
        write("Actions needed: 0")
        write("Estimated time: 0 seconds")
        return

    write(f"Actions needed:  {format_int(result.actions_required)}")
    write(f"Estimated time:  {format_duration(result.total_seconds)}")


def run(read: ReadFunc, write: WriteFunc) -> int:
    """Run one interactive calculation. Returns a process exit code."""
    try:
        write("Melvor Idle Training Calculator")
        write("")
        write("How do you want to enter current progress?")
        write("  1. Exact current XP (recommended)")
        write("  2. Current level only")
        choice = _prompt_choice(
            read, write, "Choice: ", (_CHOICE_EXACT_XP, _CHOICE_LEVEL_ONLY)
        )

        if choice == _CHOICE_EXACT_XP:
            current_xp = _prompt_value(
                read, write, "Current cumulative XP: ", _parse_current_xp
            )
        else:
            current_level = _prompt_value(
                read,
                write,
                f"Current level ({MIN_SUPPORTED_LEVEL}-{MAX_SUPPORTED_LEVEL}): ",
                _parse_level,
            )

        target_level = _prompt_value(
            read,
            write,
            f"Target level ({MIN_SUPPORTED_LEVEL}-{MAX_SUPPORTED_LEVEL}): ",
            _parse_level,
        )
        xp_per_action = _prompt_value(
            read,
            write,
            "XP gained per completed action: ",
            lambda raw: _parse_positive_decimal(raw, _XP_PER_ACTION_ERROR),
        )
        action_seconds = _prompt_value(
            read,
            write,
            "Time per action in seconds: ",
            lambda raw: _parse_positive_decimal(raw, _ACTION_SECONDS_ERROR),
        )

        if choice == _CHOICE_EXACT_XP:
            request = request_from_exact_xp(
                current_xp, target_level, xp_per_action, action_seconds
            )
        else:
            request = request_from_current_level(
                current_level, target_level, xp_per_action, action_seconds
            )

        result = calculate_training(request)
        write("")
        _render_result(write, result)
        return 0
    except _Cancelled:
        write("Cancelled.")
        return 1


def main() -> int:
    return run(input, print)
