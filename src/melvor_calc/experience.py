"""Melvor Idle skill experience curve.

Source: https://wiki.melvoridle.com/w/Experience_Table
"""

from __future__ import annotations

from math import floor

MIN_SUPPORTED_LEVEL = 1
MAX_SUPPORTED_LEVEL = 120


class ExperienceValidationError(ValueError):
    """Raised when a level value violates the domain contract."""


def _validate_level(level: int) -> None:
    if isinstance(level, bool) or not isinstance(level, int):
        raise ExperienceValidationError(
            f"level must be an int, got {type(level).__name__}"
        )
    if not (MIN_SUPPORTED_LEVEL <= level <= MAX_SUPPORTED_LEVEL):
        raise ExperienceValidationError(
            f"level must be between {MIN_SUPPORTED_LEVEL} and "
            f"{MAX_SUPPORTED_LEVEL}, got {level}"
        )


def xp_for_level(level: int) -> int:
    """Return the minimum cumulative XP required to reach ``level``.

    Preconditions:
        1 <= level <= MAX_SUPPORTED_LEVEL, level is an int (not bool).

    Raises:
        ExperienceValidationError: if level is not a valid int in range.
    """
    _validate_level(level)

    points = 0
    for n in range(1, level):
        points += floor(n + 300 * (2 ** (n / 7)))
    return floor(points / 4)
