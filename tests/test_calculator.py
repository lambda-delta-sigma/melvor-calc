from decimal import Decimal

import pytest

from melvor_calc.calculator import (
    calculate_training,
    request_from_current_level,
    request_from_exact_xp,
)
from melvor_calc.experience import xp_for_level
from melvor_calc.models import CalculationValidationError, ProgressSource, TrainingRequest


def _request(**overrides):
    defaults = dict(
        current_xp=0,
        target_level=10,
        xp_per_action=Decimal(100),
        action_seconds=Decimal(1),
        progress_source=ProgressSource.EXACT_XP,
    )
    defaults.update(overrides)
    return TrainingRequest(**defaults)


def test_exact_division():
    result = calculate_training(
        _request(current_xp=xp_for_level(10) - 1_000, xp_per_action=Decimal(100))
    )
    assert result.remaining_xp == 1_000
    assert result.actions_required == 10


def test_fractional_final_action_rounds_up():
    target_xp = xp_for_level(10)
    result = calculate_training(
        _request(current_xp=target_xp - 1_001, xp_per_action=Decimal(100))
    )
    assert result.remaining_xp == 1_001
    assert result.actions_required == 11


def test_xp_per_action_greater_than_remaining_xp():
    target_xp = xp_for_level(2)
    result = calculate_training(
        _request(
            target_level=2,
            current_xp=target_xp - 1,
            xp_per_action=Decimal(1_000_000),
        )
    )
    assert result.actions_required == 1


def test_current_xp_equals_target_xp():
    target_xp = xp_for_level(10)
    result = calculate_training(_request(target_level=10, current_xp=target_xp))
    assert result.remaining_xp == 0
    assert result.actions_required == 0
    assert result.total_seconds == Decimal(0)


def test_current_xp_exceeds_target_xp():
    target_xp = xp_for_level(10)
    result = calculate_training(_request(target_level=10, current_xp=target_xp + 5_000))
    assert result.remaining_xp == 0
    assert result.actions_required == 0
    assert result.total_seconds == Decimal(0)


def test_decimal_xp_per_action_rounds_up_without_float():
    result = calculate_training(
        _request(
            current_xp=0,
            target_level=2,
            xp_per_action=Decimal("3.3"),
        )
    )
    # xp_for_level(2) == 83 (see test_experience.py::_KNOWN_VALUES); 83 / 3.3
    # == 25.1515..., which must round up to 26, not truncate to 25.
    assert result.remaining_xp == 83
    assert result.actions_required == 26


def test_decimal_action_duration_exact_multiplication():
    result = calculate_training(
        _request(
            current_xp=0,
            target_level=2,
            xp_per_action=Decimal(83),
            action_seconds=Decimal("2.5"),
        )
    )
    assert result.actions_required == 1
    assert result.total_seconds == Decimal("2.5")


def test_xp_per_hour():
    result = calculate_training(
        _request(xp_per_action=Decimal(100), action_seconds=Decimal(2))
    )
    # 100 xp/action * 3600 seconds / 2 seconds/action, computed by hand.
    assert result.xp_per_hour == Decimal(180_000)


def test_level_only_normalization_marks_level_minimum():
    request = request_from_current_level(2, 3, Decimal(50), Decimal(3))
    assert request.current_xp == xp_for_level(2)
    assert request.progress_source is ProgressSource.LEVEL_MINIMUM


def test_exact_xp_request_unchanged_and_marked_exact():
    request = request_from_exact_xp(1_000, 10, Decimal(100), Decimal("2.5"))
    assert request.current_xp == 1_000
    assert request.progress_source is ProgressSource.EXACT_XP


# --- validation ---

_REJECTED_OVERRIDES = [
    pytest.param({"current_xp": -1}, id="negative_current_xp"),
    pytest.param({"target_level": 0}, id="target_level_below_range"),
    pytest.param({"target_level": 121}, id="target_level_above_range"),
    pytest.param({"xp_per_action": Decimal(0)}, id="zero_xp_per_action"),
    pytest.param({"xp_per_action": Decimal(-5)}, id="negative_xp_per_action"),
    pytest.param({"action_seconds": Decimal(0)}, id="zero_action_seconds"),
    pytest.param({"action_seconds": Decimal(-1)}, id="negative_action_seconds"),
    pytest.param({"xp_per_action": Decimal("NaN")}, id="nan_xp_per_action"),
    pytest.param({"action_seconds": Decimal("Infinity")}, id="positive_infinity_action_seconds"),
    pytest.param({"xp_per_action": Decimal("-Infinity")}, id="negative_infinity_xp_per_action"),
    pytest.param({"current_xp": True}, id="bool_current_xp"),
    pytest.param({"target_level": True}, id="bool_target_level"),
    pytest.param({"xp_per_action": 100}, id="non_decimal_xp_per_action"),
    pytest.param({"progress_source": "EXACT_XP"}, id="non_enum_progress_source"),
]


@pytest.mark.parametrize("overrides", _REJECTED_OVERRIDES)
def test_invalid_request_rejected(overrides):
    with pytest.raises(CalculationValidationError):
        calculate_training(_request(**overrides))
