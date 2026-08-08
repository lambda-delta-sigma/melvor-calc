import pytest

from melvor_calc.experience import (
    MAX_SUPPORTED_LEVEL,
    MIN_SUPPORTED_LEVEL,
    ExperienceValidationError,
    xp_for_level,
)

_KNOWN_VALUES = [
    pytest.param(1, 0, id="level_1"),
    pytest.param(2, 83, id="level_2"),
    pytest.param(3, 174, id="level_3"),
    pytest.param(10, 1_154, id="level_10"),
    pytest.param(50, 101_333, id="level_50"),
    pytest.param(92, 6_517_253, id="level_92"),
    pytest.param(99, 13_034_431, id="level_99"),
    pytest.param(120, 104_273_167, id="level_120"),
]


@pytest.mark.parametrize("level,expected_xp", _KNOWN_VALUES)
def test_known_values(level, expected_xp):
    assert xp_for_level(level) == expected_xp


def test_level_1_is_zero():
    assert xp_for_level(1) == 0


def test_thresholds_strictly_increase():
    previous = xp_for_level(MIN_SUPPORTED_LEVEL)
    for level in range(MIN_SUPPORTED_LEVEL + 1, MAX_SUPPORTED_LEVEL + 1):
        current = xp_for_level(level)
        assert current > previous
        previous = current


# --- validation ---

_REJECTED_LEVELS = [
    pytest.param(0, id="below_range"),
    pytest.param(MAX_SUPPORTED_LEVEL + 1, id="above_range"),
    pytest.param(99.0, id="integral_float"),
    pytest.param(True, id="bool_true"),
    pytest.param(False, id="bool_false"),
]


@pytest.mark.parametrize("level", _REJECTED_LEVELS)
def test_invalid_level_rejected(level):
    with pytest.raises(ExperienceValidationError):
        xp_for_level(level)
