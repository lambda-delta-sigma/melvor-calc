from __future__ import annotations

from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal

_UNITS = (
    ("day", 86_400),
    ("hour", 3_600),
    ("minute", 60),
    ("second", 1),
)


def format_duration(total_seconds: Decimal) -> str:
    """Render ``total_seconds`` as a human-readable duration.

    Rounds up to the next whole second so a sub-second remainder is never
    reported as "0 seconds" or silently dropped.
    """
    whole_seconds = int(
        total_seconds.to_integral_value(rounding=ROUND_CEILING)
    )

    if whole_seconds == 0:
        return "0 seconds"

    remaining = whole_seconds
    parts: list[str] = []
    for name, unit_seconds in _UNITS:
        value, remaining = divmod(remaining, unit_seconds)
        if value:
            plural = "" if value == 1 else "s"
            parts.append(f"{value} {name}{plural}")

    return ", ".join(parts)


def format_int(value: int) -> str:
    return f"{value:,}"


def format_decimal(value: Decimal) -> str:
    """Render a Decimal with thousands separators, rounded for display only."""
    quantized = value.to_integral_value(rounding=ROUND_HALF_UP)
    return f"{int(quantized):,}"
