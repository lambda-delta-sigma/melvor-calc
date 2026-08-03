from decimal import Decimal

import pytest

from melvor_calc.formatting import format_decimal, format_duration, format_int

DURATION_EXAMPLES = [
    (Decimal(0), "0 seconds"),
    (Decimal(1), "1 second"),
    (Decimal(60), "1 minute"),
    (Decimal(61), "1 minute, 1 second"),
    (Decimal(3_661), "1 hour, 1 minute, 1 second"),
    (Decimal(90_061), "1 day, 1 hour, 1 minute, 1 second"),
    (Decimal("0.1"), "1 second"),
]


@pytest.mark.parametrize("seconds,expected", DURATION_EXAMPLES)
def test_duration_examples(seconds, expected):
    assert format_duration(seconds) == expected


def test_exact_day_boundary():
    assert format_duration(Decimal(86_400)) == "1 day"


def test_plural_days():
    assert format_duration(Decimal(2 * 86_400)) == "2 days"


def test_zero_valued_middle_units_omitted():
    # 1 day and 1 second, no hours or minutes.
    assert format_duration(Decimal(86_401)) == "1 day, 1 second"


def test_sub_second_input_rounds_up():
    assert format_duration(Decimal("59.001")) == "1 minute"


def test_large_duration_does_not_wrap_after_24_hours():
    # 30 hours should show as 1 day, 6 hours, not 30 hours.
    assert format_duration(Decimal(30 * 3_600)) == "1 day, 6 hours"


def test_format_int_thousands_separator():
    assert format_int(13_034_431) == "13,034,431"


def test_format_int_small_value_no_separator():
    assert format_int(83) == "83"


def test_format_decimal_thousands_separator():
    assert format_decimal(Decimal("120000")) == "120,000"


def test_format_decimal_rounds_for_display():
    assert format_decimal(Decimal("120000.4")) == "120,000"
    assert format_decimal(Decimal("120000.5")) == "120,001"


def test_format_decimal_handles_scientific_notation_result():
    # Decimal division can produce a value like Decimal("1.4400E+5"); the
    # grouped-digit formatting must not leak that exponent notation.
    value = Decimal(100) * Decimal(3600) / Decimal("2.5")
    assert format_decimal(value) == "144,000"
