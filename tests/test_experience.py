import pytest

from melvor_calc.experience import (
    MAX_SUPPORTED_LEVEL,
    MIN_SUPPORTED_LEVEL,
    ExperienceValidationError,
    xp_for_level,
)

KNOWN_VALUES = [
    (1, 0),
    (2, 83),
    (3, 174),
    (10, 1_154),
    (50, 101_333),
    (92, 6_517_253),
    (99, 13_034_431),
    (120, 104_273_167),
]


@pytest.mark.parametrize("level,expected_xp", KNOWN_VALUES)
def test_known_values(level, expected_xp):
    assert xp_for_level(level) == expected_xp


@pytest.mark.parametrize("level,expected_xp", KNOWN_VALUES)
def test_known_values_are_int(level, expected_xp):
    assert isinstance(xp_for_level(level), int)


def test_level_1_is_zero():
    assert xp_for_level(1) == 0


def test_thresholds_strictly_increase():
    previous = xp_for_level(MIN_SUPPORTED_LEVEL)
    for level in range(MIN_SUPPORTED_LEVEL + 1, MAX_SUPPORTED_LEVEL + 1):
        current = xp_for_level(level)
        assert current > previous
        previous = current


def test_level_zero_rejected():
    with pytest.raises(ExperienceValidationError):
        xp_for_level(0)


def test_level_above_max_rejected():
    with pytest.raises(ExperienceValidationError):
        xp_for_level(MAX_SUPPORTED_LEVEL + 1)


def test_integral_float_rejected():
    with pytest.raises(ExperienceValidationError):
        xp_for_level(99.0)


def test_bool_true_rejected():
    with pytest.raises(ExperienceValidationError):
        xp_for_level(True)


def test_bool_false_rejected():
    with pytest.raises(ExperienceValidationError):
        xp_for_level(False)
