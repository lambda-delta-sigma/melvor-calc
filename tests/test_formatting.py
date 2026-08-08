from decimal import Decimal

import pytest

from melvor_calc.formatting import format_decimal, format_duration, format_int

_DURATION_EXAMPLES = [
    pytest.param(Decimal(0), "0 seconds", id="zero_seconds"),
    pytest.param(Decimal(1), "1 second", id="one_second"),
    pytest.param(Decimal(60), "1 minute", id="one_minute"),
    pytest.param(Decimal(61), "1 minute, 1 second", id="minute_and_second"),
    pytest.param(Decimal(3_661), "1 hour, 1 minute, 1 second", id="hour_minute_second"),
    pytest.param(Decimal(90_061), "1 day, 1 hour, 1 minute, 1 second", id="day_hour_minute_second"),
    pytest.param(Decimal("0.1"), "1 second", id="sub_second_rounds_up_to_one_second"),
    pytest.param(Decimal(86_400), "1 day", id="exact_day_boundary"),
    pytest.param(Decimal(2 * 86_400), "2 days", id="plural_days"),
    pytest.param(Decimal(86_401), "1 day, 1 second", id="zero_valued_middle_units_omitted"),
    pytest.param(Decimal("59.001"), "1 minute", id="sub_second_input_rounds_up_across_minute_boundary"),
    pytest.param(Decimal(30 * 3_600), "1 day, 6 hours", id="large_duration_does_not_wrap_after_24_hours"),
]


@pytest.mark.parametrize("seconds,expected", _DURATION_EXAMPLES)
def test_duration_examples(seconds, expected):
    assert format_duration(seconds) == expected


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
