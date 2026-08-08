from __future__ import annotations

from decimal import Decimal, ROUND_CEILING

from melvor_calc.experience import (
    MAX_SUPPORTED_LEVEL,
    MIN_SUPPORTED_LEVEL,
    xp_for_level,
)
from melvor_calc.models import (
    CalculationValidationError,
    ProgressSource,
    TrainingRequest,
    TrainingResult,
)

SECONDS_PER_HOUR = Decimal(3600)


def request_from_exact_xp(
    current_xp: int,
    target_level: int,
    xp_per_action: Decimal,
    action_seconds: Decimal,
) -> TrainingRequest:
    """Build a request from exact current cumulative XP."""
    return TrainingRequest(
        current_xp=current_xp,
        target_level=target_level,
        xp_per_action=xp_per_action,
        action_seconds=action_seconds,
        progress_source=ProgressSource.EXACT_XP,
    )


def request_from_current_level(
    current_level: int,
    target_level: int,
    xp_per_action: Decimal,
    action_seconds: Decimal,
) -> TrainingRequest:
    """Build a request assuming 0% progress into ``current_level``.

    Normalizes the level to its minimum cumulative XP and marks the
    resulting request LEVEL_MINIMUM so the presentation layer can disclose
    the assumption.
    """
    return TrainingRequest(
        current_xp=xp_for_level(current_level),
        target_level=target_level,
        xp_per_action=xp_per_action,
        action_seconds=action_seconds,
        progress_source=ProgressSource.LEVEL_MINIMUM,
    )


def _validate_current_xp(current_xp: int) -> None:
    if isinstance(current_xp, bool) or not isinstance(current_xp, int):
        raise CalculationValidationError(
            f"current_xp must be an int, got {type(current_xp).__name__}"
        )
    if current_xp < 0:
        raise CalculationValidationError("current_xp must be 0 or greater")


def _validate_target_level(target_level: int) -> None:
    if isinstance(target_level, bool) or not isinstance(target_level, int):
        raise CalculationValidationError(
            f"target_level must be an int, got {type(target_level).__name__}"
        )
    if not (MIN_SUPPORTED_LEVEL <= target_level <= MAX_SUPPORTED_LEVEL):
        raise CalculationValidationError(
            f"target_level must be between {MIN_SUPPORTED_LEVEL} and "
            f"{MAX_SUPPORTED_LEVEL}, got {target_level}"
        )


def _validate_positive_decimal(value: Decimal, name: str) -> None:
    if not isinstance(value, Decimal):
        raise CalculationValidationError(
            f"{name} must be a Decimal, got {type(value).__name__}"
        )
    if not value.is_finite():
        raise CalculationValidationError(f"{name} must be a finite number")
    if value <= 0:
        raise CalculationValidationError(f"{name} must be greater than 0")


def _validate_progress_source(progress_source: ProgressSource) -> None:
    if not isinstance(progress_source, ProgressSource):
        raise CalculationValidationError(
            "progress_source must be a ProgressSource, got "
            f"{type(progress_source).__name__}"
        )


def _validate_request(request: TrainingRequest) -> None:
    _validate_current_xp(request.current_xp)
    _validate_target_level(request.target_level)
    _validate_positive_decimal(request.xp_per_action, "xp_per_action")
    _validate_positive_decimal(request.action_seconds, "action_seconds")
    _validate_progress_source(request.progress_source)


def calculate_training(request: TrainingRequest) -> TrainingResult:
    """Compute remaining XP, required actions, and total time for ``request``."""
    _validate_request(request)

    target_xp = xp_for_level(request.target_level)
    remaining_xp = max(0, target_xp - request.current_xp)

    if remaining_xp == 0:
        actions_required = 0
    else:
        actions_required = int(
            (Decimal(remaining_xp) / request.xp_per_action).to_integral_value(
                rounding=ROUND_CEILING
            )
        )

    total_seconds = Decimal(actions_required) * request.action_seconds
    xp_per_hour = request.xp_per_action * SECONDS_PER_HOUR / request.action_seconds

    return TrainingResult(
        current_xp=request.current_xp,
        target_level=request.target_level,
        target_xp=target_xp,
        remaining_xp=remaining_xp,
        actions_required=actions_required,
        action_seconds=request.action_seconds,
        total_seconds=total_seconds,
        xp_per_hour=xp_per_hour,
        progress_source=request.progress_source,
    )
