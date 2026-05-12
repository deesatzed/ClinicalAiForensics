"""Typed component-result and status-ledger data contracts."""

from __future__ import annotations

from typing import Any, Literal, Self

from pydantic import Field, model_validator

from .input_models import Prior
from .model_base import NonEmptyString, StrictModel


SafetyGateStatus = Literal["passed", "blocked", "triggered", "missing", "unsupported"]


class SafetyGateEvaluation(StrictModel):
    gate_group: NonEmptyString
    status: SafetyGateStatus
    reason: NonEmptyString
    evidence: NonEmptyString
    source: NonEmptyString | None = None
    mapping_source: NonEmptyString | None = None
    option_id: NonEmptyString | None = None
    variable: NonEmptyString | None = None
    condition: NonEmptyString | None = None
    observed_value: Any | None = None
    claim_type: NonEmptyString | None = None

    @model_validator(mode="after")
    def require_target_for_active_status(self) -> Self:
        if self.status in {"blocked", "triggered"} and self.option_id is None and self.claim_type is None:
            raise ValueError("active safety gate evaluations require option_id or claim_type")
        return self


class SafetyGateEvaluationSet(StrictModel):
    cde_id: NonEmptyString
    domain_pack_id: NonEmptyString
    evaluations: list[SafetyGateEvaluation] = Field(default_factory=list)

    def active_hard_stops(self) -> list[SafetyGateEvaluation]:
        return [evaluation for evaluation in self.evaluations if evaluation.status in {"blocked", "triggered"}]

    def hard_stops_by_option(self) -> dict[str, list[str]]:
        hard_stops: dict[str, list[str]] = {}
        for evaluation in self.active_hard_stops():
            if evaluation.option_id is None:
                continue
            hard_stops.setdefault(evaluation.option_id, []).append(
                f"{evaluation.reason}: {evaluation.evidence}"
            )
        return hard_stops


PriorResolutionStatus = Literal["resolved", "missing", "unsupported", "blocked"]


class PriorResolution(StrictModel):
    prior_id: NonEmptyString
    status: PriorResolutionStatus
    reason: NonEmptyString
    source: NonEmptyString | None = None
    normalized_provenance_class: NonEmptyString | None = None
    prior: Prior | None = None
    distribution: NonEmptyString | None = None
    parameters: dict[str, float] | None = None
    provenance_class: NonEmptyString | None = None
    confidence_class: NonEmptyString | None = None
    calibration_status: NonEmptyString | None = None
    warning: str | None = None
    owner: str | None = None
    review_status: str | None = None
    source_basis: str | None = None
    last_reviewed: str | None = None

    @model_validator(mode="after")
    def require_resolved_prior_metadata(self) -> Self:
        if self.status == "resolved":
            required = [
                self.source,
                self.normalized_provenance_class,
                self.prior,
                self.distribution,
                self.parameters,
                self.provenance_class,
                self.confidence_class,
                self.calibration_status,
            ]
            if any(value is None for value in required):
                raise ValueError("resolved prior requires source, prior, distribution, parameters, and provenance")
        if self.status in {"blocked", "unsupported"} and self.source is None:
            raise ValueError("blocked or unsupported prior requires source")
        return self


class PriorResolutionSet(StrictModel):
    cde_id: NonEmptyString | None = None
    domain_pack_id: NonEmptyString
    requested_prior_ids: list[NonEmptyString] = Field(default_factory=list)
    resolutions: list[PriorResolution] = Field(default_factory=list)

    def active_resolutions(self) -> list[PriorResolution]:
        return [resolution for resolution in self.resolutions if resolution.status == "resolved"]

    def active_priors(self) -> dict[str, Prior]:
        return {
            resolution.prior_id: resolution.prior
            for resolution in self.active_resolutions()
            if resolution.prior is not None
        }


MonteCarloPriorStatus = Literal["sampled", "missing", "unsupported", "blocked"]


class MonteCarloPriorSimulation(StrictModel):
    prior_id: NonEmptyString
    status: MonteCarloPriorStatus
    reason: NonEmptyString
    source: NonEmptyString | None = None
    distribution: NonEmptyString | None = None
    parameters: dict[str, float] | None = None
    provenance_class: NonEmptyString | None = None
    normalized_provenance_class: NonEmptyString | None = None
    confidence_class: NonEmptyString | None = None
    calibration_status: NonEmptyString | None = None
    warning: str | None = None
    sample_count: int = Field(default=0, ge=0)
    samples: list[float] = Field(default_factory=list)
    sample_mean: float | None = Field(default=None, ge=0, le=1)
    sample_median: float | None = Field(default=None, ge=0, le=1)
    p5: float | None = Field(default=None, ge=0, le=1)
    p95: float | None = Field(default=None, ge=0, le=1)
    interval_width: float | None = Field(default=None, ge=0, le=1)
    minimum: float | None = Field(default=None, ge=0, le=1)
    maximum: float | None = Field(default=None, ge=0, le=1)

    @model_validator(mode="after")
    def require_sampled_summary_or_empty_skip(self) -> Self:
        if self.status == "sampled":
            required = [
                self.source,
                self.distribution,
                self.parameters,
                self.provenance_class,
                self.normalized_provenance_class,
                self.confidence_class,
                self.calibration_status,
                self.sample_mean,
                self.sample_median,
                self.p5,
                self.p95,
                self.interval_width,
                self.minimum,
                self.maximum,
            ]
            if any(value is None for value in required):
                raise ValueError("sampled prior simulation requires prior metadata and summary statistics")
            if self.sample_count <= 0 or len(self.samples) != self.sample_count:
                raise ValueError("sampled prior simulation requires sample_count matching samples")
        else:
            if self.sample_count != 0 or self.samples:
                raise ValueError("non-sampled prior simulations cannot contain samples")
            summaries = [
                self.sample_mean,
                self.sample_median,
                self.p5,
                self.p95,
                self.interval_width,
                self.minimum,
                self.maximum,
            ]
            if any(value is not None for value in summaries):
                raise ValueError("non-sampled prior simulations cannot contain summary statistics")
        return self


class MonteCarloSimulationResult(StrictModel):
    cde_id: NonEmptyString | None = None
    domain_pack_id: NonEmptyString
    n_iterations: int = Field(ge=1)
    random_seed: int | None = None
    prior_simulations: list[MonteCarloPriorSimulation] = Field(default_factory=list)

    def sampled_simulations(self) -> list[MonteCarloPriorSimulation]:
        return [simulation for simulation in self.prior_simulations if simulation.status == "sampled"]

    def skipped_simulations(self) -> list[MonteCarloPriorSimulation]:
        return [simulation for simulation in self.prior_simulations if simulation.status != "sampled"]


UncertaintyCategory = Literal[
    "evidence_uncertainty",
    "patient_context_uncertainty",
    "local_execution_uncertainty",
    "monitoring_rescue_uncertainty",
    "harm_uncertainty",
    "preference_feasibility_uncertainty",
    "prior_quality_uncertainty",
]
UncertaintyItemStatus = Literal["defined", "active", "missing", "deferred", "unsupported"]


class UncertaintyBudgetEvaluationItem(StrictModel):
    category: UncertaintyCategory
    status: UncertaintyItemStatus
    source: NonEmptyString
    reason: NonEmptyString
    actionable: bool = False
    could_change_decision: bool = False
    source_fields: list[NonEmptyString] = Field(default_factory=list)
    required_data: list[NonEmptyString] = Field(default_factory=list)
    related_variables: list[NonEmptyString] = Field(default_factory=list)
    related_prior_ids: list[NonEmptyString] = Field(default_factory=list)
    related_gate_groups: list[NonEmptyString] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_data_for_actionable_items(self) -> Self:
        if self.actionable and not self.required_data:
            raise ValueError("actionable uncertainty budget items require required_data")
        return self


class UncertaintyBudgetEvaluationSet(StrictModel):
    cde_id: NonEmptyString
    domain_pack_id: NonEmptyString
    items: list[UncertaintyBudgetEvaluationItem] = Field(default_factory=list)

    def active_items(self) -> list[UncertaintyBudgetEvaluationItem]:
        return [item for item in self.items if item.status in {"active", "missing"}]

    def deferred_items(self) -> list[UncertaintyBudgetEvaluationItem]:
        return [item for item in self.items if item.status == "deferred"]


ValueOfInformationStatus = Literal["present", "missing", "unsupported", "deferred"]


class ValueOfInformationEvaluation(StrictModel):
    variable: NonEmptyString
    status: ValueOfInformationStatus
    source: NonEmptyString
    reason: NonEmptyString
    rank: int | None = Field(default=None, ge=1)
    source_field: NonEmptyString | None = None
    actionable: bool = False
    could_change_decision: bool = False
    required_data: list[NonEmptyString] = Field(default_factory=list)
    related_gate_groups: list[NonEmptyString] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_data_for_actionable_voi(self) -> Self:
        if self.actionable and not self.required_data:
            raise ValueError("actionable value-of-information items require required_data")
        return self


class ValueOfInformationEvaluationSet(StrictModel):
    cde_id: NonEmptyString
    domain_pack_id: NonEmptyString
    items: list[ValueOfInformationEvaluation] = Field(default_factory=list)

    def actionable_items(self) -> list[ValueOfInformationEvaluation]:
        return [item for item in self.items if item.actionable]

    def deferred_items(self) -> list[ValueOfInformationEvaluation]:
        return [item for item in self.items if item.status == "deferred"]


DecisionProfileEvaluationStatus = Literal[
    "eligible",
    "blocked",
    "triggered",
    "missing",
    "unsupported",
    "deferred",
]
DecisionProfileInputType = Literal[
    "decision_option",
    "domain_mapping",
    "safety_gate",
    "prior_resolution",
    "monte_carlo_simulation",
    "uncertainty_budget",
    "value_of_information",
    "decision_profiler",
]


class DecisionProfileInputSummary(StrictModel):
    input_type: DecisionProfileInputType
    identifier: NonEmptyString
    status: NonEmptyString
    reason: NonEmptyString
    source: NonEmptyString | None = None


class DecisionProfileEvaluation(StrictModel):
    option_id: NonEmptyString
    status: DecisionProfileEvaluationStatus
    reason: NonEmptyString
    source: NonEmptyString
    option_label: NonEmptyString | None = None
    active_blockers: list[NonEmptyString] = Field(default_factory=list)
    active_triggers: list[NonEmptyString] = Field(default_factory=list)
    missing_data: list[NonEmptyString] = Field(default_factory=list)
    supporting_gates: list[NonEmptyString] = Field(default_factory=list)
    unsupported_inputs: list[NonEmptyString] = Field(default_factory=list)
    supporting_priors: list[NonEmptyString] = Field(default_factory=list)
    supporting_simulations: list[NonEmptyString] = Field(default_factory=list)
    uncertainty_items: list[NonEmptyString] = Field(default_factory=list)
    value_of_information_items: list[NonEmptyString] = Field(default_factory=list)
    deferred_reasons: list[NonEmptyString] = Field(default_factory=list)
    provenance_references: list[NonEmptyString] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_status_explanation(self) -> Self:
        if self.status == "blocked" and not self.active_blockers:
            raise ValueError("blocked decision profile evaluations require active_blockers")
        if self.status == "triggered" and not self.active_triggers:
            raise ValueError("triggered decision profile evaluations require active_triggers")
        if self.status == "missing" and not self.missing_data:
            raise ValueError("missing decision profile evaluations require missing_data")
        if self.status == "unsupported" and not self.unsupported_inputs:
            raise ValueError("unsupported decision profile evaluations require unsupported_inputs")
        if self.status == "deferred" and not self.deferred_reasons:
            raise ValueError("deferred decision profile evaluations require deferred_reasons")
        return self


class DecisionProfileEvaluationSet(StrictModel):
    cde_id: NonEmptyString
    domain_pack_id: NonEmptyString
    profiles: list[DecisionProfileEvaluation] = Field(default_factory=list)
    input_summaries: list[DecisionProfileInputSummary] = Field(default_factory=list)

    def profiles_by_option(self) -> dict[str, DecisionProfileEvaluation]:
        return {profile.option_id: profile for profile in self.profiles}

    def unresolved_inputs(self) -> list[DecisionProfileInputSummary]:
        return [
            item
            for item in self.input_summaries
            if item.status in {"missing", "unsupported", "blocked", "deferred", "active"}
        ]

    def deferred_inputs(self) -> list[DecisionProfileInputSummary]:
        return [item for item in self.input_summaries if item.status == "deferred"]


StatusLedgerComponent = Literal[
    "decision_option",
    "domain_mapping",
    "safety_gate",
    "prior_resolution",
    "monte_carlo_prior",
    "uncertainty_budget_item",
    "value_of_information_item",
    "decision_profile",
    "decision_profiler",
]


class StatusLedgerRow(StrictModel):
    component: StatusLedgerComponent
    identifier: NonEmptyString
    status: NonEmptyString
    reason: NonEmptyString
    source: NonEmptyString | None = None
    provenance_references: list[NonEmptyString] = Field(default_factory=list)
    related_entity_ids: dict[str, list[NonEmptyString]] = Field(default_factory=dict)

    def is_unresolved(self) -> bool:
        return self.status in {
            "active",
            "blocked",
            "deferred",
            "missing",
            "triggered",
            "unsupported",
        }


class StatusLedger(StrictModel):
    cde_id: NonEmptyString
    domain_pack_id: NonEmptyString
    rows: list[StatusLedgerRow] = Field(default_factory=list)

    def unresolved_rows(self) -> list[StatusLedgerRow]:
        return [row for row in self.rows if row.is_unresolved()]

    def status_counts_by_component(self) -> dict[str, dict[str, int]]:
        counts: dict[str, dict[str, int]] = {}
        for row in self.rows:
            component_counts = counts.setdefault(row.component, {})
            component_counts[row.status] = component_counts.get(row.status, 0) + 1
        return {
            component: dict(sorted(component_counts.items()))
            for component, component_counts in sorted(counts.items())
        }
