"""Pydantic data contracts for the Phase 0 PDDE build.

These models validate the shapes defined by the v0.3 build directions and
example fixtures. Engine behavior lives in dedicated modules.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, PositiveFloat, StringConstraints, model_validator


NonEmptyString = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
JsonObject = dict[str, Any]


class StrictModel(BaseModel):
    """Base model with explicit fields only."""

    model_config = ConfigDict(extra="forbid")


class SourceRecommendation(StrictModel):
    source: NonEmptyString
    text: NonEmptyString


class ClinicalDecisionEpisode(StrictModel):
    cde_id: NonEmptyString
    domain: NonEmptyString
    decision_moment: NonEmptyString
    case_text: str | None = None
    patient_state: JsonObject = Field(default_factory=dict)
    candidate_options: list[NonEmptyString] = Field(min_length=1)
    source_recommendations: list[SourceRecommendation] = Field(default_factory=list)
    local_context: JsonObject = Field(default_factory=dict)
    outcome_tracking: JsonObject = Field(default_factory=dict)


class DecisionOption(StrictModel):
    id: NonEmptyString
    label: NonEmptyString


class SafetyGate(StrictModel):
    reason: NonEmptyString
    variable: NonEmptyString | None = None
    condition: NonEmptyString | None = None
    claim_type: NonEmptyString | None = None

    @model_validator(mode="after")
    def require_variable_or_claim_type(self) -> Self:
        if self.variable is None and self.claim_type is None:
            raise ValueError("safety gate requires either variable or claim_type")
        if self.variable is not None and self.condition is None:
            raise ValueError("variable safety gate requires condition")
        return self


SafetyGateMatchedStatus = Literal["blocked", "triggered"]


class SafetyGateTargetMapping(StrictModel):
    gate_group: NonEmptyString
    option_id: NonEmptyString
    matched_status: SafetyGateMatchedStatus


class PriorToOptionMapping(StrictModel):
    prior_id: NonEmptyString
    option_ids: list[NonEmptyString] = Field(min_length=1)

    @model_validator(mode="after")
    def require_unique_option_ids(self) -> Self:
        if len(set(self.option_ids)) != len(self.option_ids):
            raise ValueError("prior-to-option mappings cannot repeat option ids")
        return self


class DomainPackMappings(StrictModel):
    safety_gate_targets: list[SafetyGateTargetMapping] = Field(default_factory=list)
    prior_to_options: list[PriorToOptionMapping] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_unique_mapping_keys(self) -> Self:
        gate_groups = [mapping.gate_group for mapping in self.safety_gate_targets]
        if len(set(gate_groups)) != len(gate_groups):
            raise ValueError("safety gate target mappings must use unique gate_group values")

        prior_ids = [mapping.prior_id for mapping in self.prior_to_options]
        if len(set(prior_ids)) != len(prior_ids):
            raise ValueError("prior-to-option mappings must use unique prior_id values")
        return self

    def safety_gate_target_by_group(self) -> dict[str, SafetyGateTargetMapping]:
        return {mapping.gate_group: mapping for mapping in self.safety_gate_targets}

    def prior_ids_by_option(self) -> dict[str, list[str]]:
        by_option: dict[str, list[str]] = {}
        for mapping in self.prior_to_options:
            for option_id in mapping.option_ids:
                by_option.setdefault(option_id, []).append(mapping.prior_id)
        return by_option


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


class Prior(StrictModel):
    distribution: Literal["beta"]
    alpha: PositiveFloat
    beta: PositiveFloat
    provenance_class: NonEmptyString
    elicitation_method: NonEmptyString
    confidence_class: NonEmptyString
    calibration_status: NonEmptyString
    warning: str | None = None
    owner: str | None = None
    review_status: str | None = None
    source_basis: str | None = None
    last_reviewed: str | None = None

    @model_validator(mode="after")
    def require_warning_for_low_confidence(self) -> Self:
        confidence = self.confidence_class.lower()
        if confidence in {"low", "moderate", "low_unverified", "moderate_unverified"}:
            if not self.warning:
                raise ValueError("low or unverified confidence priors require a warning")
        return self


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


class DomainPack(StrictModel):
    domain_pack_id: NonEmptyString
    version: NonEmptyString
    status: NonEmptyString
    clinical_owner: NonEmptyString
    calibration_status: NonEmptyString
    decision_options: list[DecisionOption] = Field(min_length=1)
    hard_gates: dict[str, list[SafetyGate]] = Field(default_factory=dict)
    mappings: DomainPackMappings = Field(default_factory=DomainPackMappings)
    soft_nodes: list[NonEmptyString] = Field(default_factory=list)
    prior_policy: dict[str, Prior] = Field(default_factory=dict)
    value_of_information_variables: list[NonEmptyString] = Field(default_factory=list)
    reporting_rules: dict[str, bool] = Field(default_factory=dict)

    @model_validator(mode="after")
    def require_unique_decision_option_ids(self) -> Self:
        option_ids = [option.id for option in self.decision_options]
        if len(set(option_ids)) != len(option_ids):
            raise ValueError("decision option ids must be unique")
        return self

    @model_validator(mode="after")
    def validate_explicit_mappings(self) -> Self:
        option_ids = {option.id for option in self.decision_options}
        gate_groups = set(self.hard_gates)
        prior_ids = set(self.prior_policy)

        for mapping in self.mappings.safety_gate_targets:
            if mapping.gate_group not in gate_groups:
                raise ValueError(
                    f"safety gate mapping references unknown gate_group {mapping.gate_group!r}"
                )
            if mapping.option_id not in option_ids:
                raise ValueError(
                    f"safety gate mapping for {mapping.gate_group!r} references "
                    f"unknown option_id {mapping.option_id!r}"
                )

        for mapping in self.mappings.prior_to_options:
            if mapping.prior_id not in prior_ids:
                raise ValueError(
                    f"prior-to-option mapping references unknown prior_id {mapping.prior_id!r}"
                )
            unknown_option_ids = [
                option_id for option_id in mapping.option_ids if option_id not in option_ids
            ]
            if unknown_option_ids:
                raise ValueError(
                    f"prior-to-option mapping for {mapping.prior_id!r} references "
                    f"unknown option_id(s): {', '.join(unknown_option_ids)}"
                )
        return self


class EvaluationPipelineResult(StrictModel):
    workflow_mode: Literal["direct_cde_simulation"] = "direct_cde_simulation"
    cde_source: NonEmptyString | None = None
    domain_pack_source: NonEmptyString | None = None
    n_iterations: int = Field(ge=1)
    random_seed: int | None = None
    cde: ClinicalDecisionEpisode
    domain_pack: DomainPack
    safety_gates: SafetyGateEvaluationSet
    prior_resolutions: PriorResolutionSet
    simulation: MonteCarloSimulationResult
    value_of_information: ValueOfInformationEvaluationSet
    uncertainty_budget: UncertaintyBudgetEvaluationSet
    decision_profiles: DecisionProfileEvaluationSet

    @model_validator(mode="after")
    def require_matching_component_ids(self) -> Self:
        cde_id = self.cde.cde_id
        domain_pack_id = self.domain_pack.domain_pack_id
        component_pairs = [
            (self.safety_gates.cde_id, self.safety_gates.domain_pack_id, "safety_gates"),
            (self.prior_resolutions.cde_id, self.prior_resolutions.domain_pack_id, "prior_resolutions"),
            (self.simulation.cde_id, self.simulation.domain_pack_id, "simulation"),
            (self.value_of_information.cde_id, self.value_of_information.domain_pack_id, "value_of_information"),
            (self.uncertainty_budget.cde_id, self.uncertainty_budget.domain_pack_id, "uncertainty_budget"),
            (self.decision_profiles.cde_id, self.decision_profiles.domain_pack_id, "decision_profiles"),
        ]
        for component_cde_id, component_domain_pack_id, name in component_pairs:
            if component_cde_id is not None and component_cde_id != cde_id:
                raise ValueError(f"{name} cde_id does not match cde.cde_id")
            if component_domain_pack_id != domain_pack_id:
                raise ValueError(f"{name} domain_pack_id does not match domain_pack.domain_pack_id")
        if self.simulation.n_iterations != self.n_iterations:
            raise ValueError("simulation n_iterations does not match pipeline n_iterations")
        if self.simulation.random_seed != self.random_seed:
            raise ValueError("simulation random_seed does not match pipeline random_seed")
        return self


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
