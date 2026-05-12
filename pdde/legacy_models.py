"""Legacy and planned report/log models kept for compatibility."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, Self

from pydantic import Field, model_validator

from .model_base import JsonObject, NonEmptyString, StrictModel


class LocalOverlayRule(StrictModel):
    value: str | list[str] | JsonObject
    status: Literal["draft", "verified", "deprecated", "retired"]
    owner: NonEmptyString
    verified_by: str | None = None
    verified_date: str | None = None

    @model_validator(mode="after")
    def require_verified_metadata(self) -> Self:
        if self.status == "verified" and (not self.verified_by or not self.verified_date):
            raise ValueError("verified local overlay rules require verified_by and verified_date")
        return self


class UncertaintyBudget(StrictModel):
    evidence_uncertainty: float = Field(ge=0, le=1)
    patient_context_uncertainty: float = Field(ge=0, le=1)
    local_execution_uncertainty: float = Field(ge=0, le=1)
    monitoring_rescue_uncertainty: float = Field(ge=0, le=1)
    harm_uncertainty: float = Field(ge=0, le=1)
    preference_feasibility_uncertainty: float = Field(ge=0, le=1)
    prior_quality_uncertainty: float = Field(ge=0, le=1)


class ValueOfInformationItem(StrictModel):
    variable: NonEmptyString
    rank: int | None = Field(default=None, ge=1)


class PriorProvenance(StrictModel):
    prior_id: NonEmptyString
    provenance_class: NonEmptyString
    confidence_class: NonEmptyString
    calibration_status: NonEmptyString


DecisionCategory = Literal[
    "action_ready",
    "conditionally_defensible",
    "needs_more_data",
    "escalate_observe_admit",
    "locally_infeasible",
    "discouraged",
    "unsafe_wrong_indication",
]


class DecisionProfile(StrictModel):
    option_id: NonEmptyString
    category: DecisionCategory
    uncertainty_interval: tuple[float, float]
    hard_stops: list[str] = Field(default_factory=list)
    missing_variables: list[str] = Field(default_factory=list)
    uncertainty_budget: UncertaintyBudget
    median_fitness: float | None = Field(default=None, ge=0, le=1)
    soft_concerns: list[str] = Field(default_factory=list)
    value_of_information: list[ValueOfInformationItem] = Field(default_factory=list)
    local_execution_checklist: list[str] = Field(default_factory=list)
    prior_provenance: list[PriorProvenance] = Field(default_factory=list)
    calibration_status: str = "uncalibrated"

    @model_validator(mode="after")
    def require_ordered_interval(self) -> Self:
        lower, upper = self.uncertainty_interval
        if lower > upper:
            raise ValueError("uncertainty_interval lower bound must be <= upper bound")
        return self


class RunMetadata(StrictModel):
    log_type: Literal["run_metadata"] = "run_metadata"
    run_id: NonEmptyString
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    cde_id: NonEmptyString
    domain_pack_id: NonEmptyString
    domain_pack_version: NonEmptyString
    workflow_mode: str = "direct_cde_simulation"
    n_iterations: int | None = Field(default=None, ge=1)
    random_seed: int | None = None
    engine_version: NonEmptyString


class PriorUsageLog(StrictModel):
    log_type: Literal["prior_used"] = "prior_used"
    run_id: NonEmptyString
    prior_id: NonEmptyString
    distribution: NonEmptyString
    provenance_class: NonEmptyString
    confidence_class: NonEmptyString
    calibration_status: NonEmptyString
    warning_displayed: bool


class PredictionLog(StrictModel):
    log_type: Literal["prediction"] = "prediction"
    run_id: NonEmptyString
    cde_id: NonEmptyString
    option_id: NonEmptyString
    category: DecisionCategory
    uncertainty_interval: tuple[float, float]
    median_fitness: float | None = Field(default=None, ge=0, le=1)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
