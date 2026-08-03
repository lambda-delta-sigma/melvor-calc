"""Domain request/result models for training calculations."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto


class ProgressSource(Enum):
    EXACT_XP = auto()
    LEVEL_MINIMUM = auto()


class CalculationValidationError(ValueError):
    """Raised when a training calculation input violates the domain contract."""


@dataclass(frozen=True)
class TrainingRequest:
    current_xp: int
    target_level: int
    xp_per_action: Decimal
    action_seconds: Decimal
    progress_source: ProgressSource


@dataclass(frozen=True)
class TrainingResult:
    current_xp: int
    target_level: int
    target_xp: int
    remaining_xp: int
    actions_required: int
    action_seconds: Decimal
    total_seconds: Decimal
    xp_per_hour: Decimal
    progress_source: ProgressSource
