"""Deterministic uncertainty-budget item evaluation.

The current Phase 0 domain pack defines required uncertainty-budget categories,
but not a numeric attribution formula. This module therefore returns typed
category-level status records and required-data prompts without inventing
weights or clinical thresholds.
"""

from __future__ import annotations

from .models import (
    ClinicalDecisionEpisode,
    DomainPack,
    MonteCarloSimulationResult,
    PriorResolutionSet,
    SafetyGateEvaluationSet,
    UncertaintyBudgetEvaluationItem,
    UncertaintyBudgetEvaluationSet,
    ValueOfInformationEvaluationSet,
)
from .value_of_information import evaluate_value_of_information


_SOURCE = "pdde_v0_3_first_principles_final/05_PRIOR_AND_UNCERTAINTY_GOVERNANCE.md#Uncertainty Budget"
_LOW_OR_DRAFT_CONFIDENCE = {"low", "moderate", "low_unverified", "moderate_unverified"}


def evaluate_uncertainty_budget(
    cde: ClinicalDecisionEpisode,
    domain_pack: DomainPack,
    *,
    safety_gates: SafetyGateEvaluationSet | None = None,
    prior_resolutions: PriorResolutionSet | None = None,
    simulation: MonteCarloSimulationResult | None = None,
    value_of_information: ValueOfInformationEvaluationSet | None = None,
) -> UncertaintyBudgetEvaluationSet:
    """Return explicit uncertainty-budget categories with transparent statuses."""

    voi = value_of_information or evaluate_value_of_information(
        cde,
        domain_pack,
        safety_gates=safety_gates,
    )

    items = [
        _evidence_uncertainty(domain_pack, prior_resolutions),
        _patient_context_uncertainty(safety_gates, voi),
        _local_execution_uncertainty(domain_pack, voi, safety_gates),
        _monitoring_rescue_uncertainty(domain_pack, voi),
        _harm_uncertainty(domain_pack),
        _preference_feasibility_uncertainty(voi),
        _prior_quality_uncertainty(prior_resolutions, simulation),
    ]
    return UncertaintyBudgetEvaluationSet(
        cde_id=cde.cde_id,
        domain_pack_id=domain_pack.domain_pack_id,
        items=items,
    )


def _evidence_uncertainty(
    domain_pack: DomainPack,
    prior_resolutions: PriorResolutionSet | None,
) -> UncertaintyBudgetEvaluationItem:
    source_fields = _soft_node_fields(domain_pack, "evidence_applicability", "evidence_maturity")
    related_prior_ids = _prior_ids(prior_resolutions)
    if not source_fields:
        return _deferred_item(
            "evidence_uncertainty",
            reason="domain pack does not define evidence applicability or evidence maturity soft nodes",
            required_data=["Add explicit evidence uncertainty nodes or definitions to the domain pack."],
        )
    return UncertaintyBudgetEvaluationItem(
        category="evidence_uncertainty",
        status="defined",
        source=_SOURCE,
        source_fields=source_fields,
        related_prior_ids=related_prior_ids,
        reason="evidence uncertainty category is explicitly defined; numeric attribution is deferred until profiling",
    )


def _patient_context_uncertainty(
    safety_gates: SafetyGateEvaluationSet | None,
    voi: ValueOfInformationEvaluationSet,
) -> UncertaintyBudgetEvaluationItem:
    missing_gate_variables = []
    related_gate_groups = []
    if safety_gates is not None:
        for evaluation in safety_gates.evaluations:
            if evaluation.variable is None or evaluation.status != "missing":
                continue
            missing_gate_variables.append(evaluation.variable)
            related_gate_groups.append(evaluation.gate_group)

    missing_voi_variables = [
        item.variable for item in voi.items if item.status == "missing" and item.variable not in missing_gate_variables
    ]
    variables = _unique(missing_gate_variables + missing_voi_variables)
    if variables:
        return UncertaintyBudgetEvaluationItem(
            category="patient_context_uncertainty",
            status="active",
            source=_SOURCE,
            source_fields=["patient_state", "domain_pack.hard_gates", "domain_pack.value_of_information_variables"],
            related_variables=variables,
            related_gate_groups=_unique(related_gate_groups),
            actionable=True,
            could_change_decision=True,
            required_data=[f"Provide CDE patient_state.{variable}." for variable in variables],
            reason="missing patient-state variables are explicit uncertainty drivers",
        )

    return UncertaintyBudgetEvaluationItem(
        category="patient_context_uncertainty",
        status="defined",
        source=_SOURCE,
        source_fields=["patient_state", "domain_pack.hard_gates", "domain_pack.value_of_information_variables"],
        reason="patient-context uncertainty category is explicit; no missing patient-state VOI variables were detected",
    )


def _local_execution_uncertainty(
    domain_pack: DomainPack,
    voi: ValueOfInformationEvaluationSet,
    safety_gates: SafetyGateEvaluationSet | None,
) -> UncertaintyBudgetEvaluationItem:
    variables = [
        item.variable
        for item in voi.items
        if item.variable in {"follow_up_available", "medication_access"} and item.status == "missing"
    ]
    if safety_gates is not None:
        variables.extend(
            evaluation.variable
            for evaluation in safety_gates.evaluations
            if evaluation.variable == "follow_up_available" and evaluation.status in {"missing", "triggered"}
        )
    variables = _unique(variable for variable in variables if variable is not None)
    source_fields = _soft_node_fields(domain_pack, "local_executability")
    if variables:
        return UncertaintyBudgetEvaluationItem(
            category="local_execution_uncertainty",
            status="active",
            source=_SOURCE,
            source_fields=source_fields + ["patient_state.follow_up_available", "patient_state.medication_access"],
            related_variables=variables,
            actionable=True,
            could_change_decision=True,
            required_data=[f"Resolve local execution field {variable}." for variable in variables],
            reason="local execution variables are missing or failed an explicit safety gate",
        )
    if not source_fields:
        return _deferred_item(
            "local_execution_uncertainty",
            reason="domain pack does not define local executability inputs",
            required_data=["Add explicit local executability definitions to the domain pack."],
        )
    return UncertaintyBudgetEvaluationItem(
        category="local_execution_uncertainty",
        status="defined",
        source=_SOURCE,
        source_fields=source_fields + ["patient_state.follow_up_available", "patient_state.medication_access"],
        reason="local execution category is explicit; no missing local execution VOI variables were detected",
    )


def _monitoring_rescue_uncertainty(
    domain_pack: DomainPack,
    voi: ValueOfInformationEvaluationSet,
) -> UncertaintyBudgetEvaluationItem:
    follow_up = next((item for item in voi.items if item.variable == "follow_up_available"), None)
    source_fields = _soft_node_fields(domain_pack, "monitoring_rescue_capacity")
    if follow_up is not None and follow_up.status == "missing":
        return UncertaintyBudgetEvaluationItem(
            category="monitoring_rescue_uncertainty",
            status="active",
            source=_SOURCE,
            source_fields=source_fields + ["patient_state.follow_up_available"],
            related_variables=["follow_up_available"],
            actionable=True,
            could_change_decision=True,
            required_data=["Provide CDE patient_state.follow_up_available."],
            reason="follow-up availability is missing for monitoring/rescue assessment",
        )
    return UncertaintyBudgetEvaluationItem(
        category="monitoring_rescue_uncertainty",
        status="deferred",
        source=_SOURCE,
        source_fields=source_fields,
        required_data=["Add explicit monitoring/rescue pathway fields, such as lab follow-up capacity."],
        reason="monitoring/rescue category is explicit, but the current v0.3 CDE has no numeric monitoring-capacity definition",
    )


def _harm_uncertainty(domain_pack: DomainPack) -> UncertaintyBudgetEvaluationItem:
    source_fields = _soft_node_fields(domain_pack, "harm_susceptibility")
    if not source_fields:
        return _deferred_item(
            "harm_uncertainty",
            reason="domain pack does not define harm susceptibility inputs",
            required_data=["Add explicit harm uncertainty definitions to the domain pack."],
        )
    return UncertaintyBudgetEvaluationItem(
        category="harm_uncertainty",
        status="deferred",
        source=_SOURCE,
        source_fields=source_fields,
        required_data=["Add explicit harm ranges or inputs before numeric harm uncertainty attribution."],
        reason="harm category is explicit, but the v0.3 domain pack has no numeric harm attribution formula",
    )


def _preference_feasibility_uncertainty(
    voi: ValueOfInformationEvaluationSet,
) -> UncertaintyBudgetEvaluationItem:
    variables = [
        item.variable
        for item in voi.items
        if item.variable in {"patient_preference", "medication_access"} and item.status == "missing"
    ]
    if variables:
        return UncertaintyBudgetEvaluationItem(
            category="preference_feasibility_uncertainty",
            status="active",
            source=_SOURCE,
            source_fields=["patient_state.patient_preference", "patient_state.medication_access"],
            related_variables=variables,
            actionable=True,
            could_change_decision=True,
            required_data=[f"Provide CDE patient_state.{variable}." for variable in variables],
            reason="patient feasibility/preference variables are missing",
        )
    return UncertaintyBudgetEvaluationItem(
        category="preference_feasibility_uncertainty",
        status="defined",
        source=_SOURCE,
        source_fields=["patient_state.patient_preference", "patient_state.medication_access"],
        reason="preference/feasibility category is explicit; required CDE fields are present when provided by VOI definitions",
    )


def _prior_quality_uncertainty(
    prior_resolutions: PriorResolutionSet | None,
    simulation: MonteCarloSimulationResult | None,
) -> UncertaintyBudgetEvaluationItem:
    if prior_resolutions is None:
        return _deferred_item(
            "prior_quality_uncertainty",
            reason="prior-resolution results are required before prior-quality uncertainty can be evaluated",
            required_data=["Run the prior resolver and provide PriorResolutionSet."],
        )

    related_prior_ids = []
    for resolution in prior_resolutions.resolutions:
        confidence = (resolution.confidence_class or "").lower()
        if (
            resolution.status != "resolved"
            or confidence in _LOW_OR_DRAFT_CONFIDENCE
            or resolution.calibration_status != "calibrated"
            or resolution.warning
        ):
            related_prior_ids.append(resolution.prior_id)

    if simulation is not None:
        related_prior_ids.extend(
            simulation.prior_id for simulation in simulation.skipped_simulations()
        )

    related_prior_ids = _unique(related_prior_ids)
    if related_prior_ids:
        return UncertaintyBudgetEvaluationItem(
            category="prior_quality_uncertainty",
            status="active",
            source=_SOURCE,
            source_fields=["domain_pack.prior_policy", "PriorResolutionSet", "MonteCarloSimulationResult"],
            related_prior_ids=related_prior_ids,
            actionable=True,
            could_change_decision=True,
            required_data=["Review, calibrate, or replace draft/blocked/unsupported priors."],
            reason="draft, uncalibrated, warning-bearing, blocked, missing, or unsupported priors are present",
        )

    return UncertaintyBudgetEvaluationItem(
        category="prior_quality_uncertainty",
        status="defined",
        source=_SOURCE,
        source_fields=["domain_pack.prior_policy", "PriorResolutionSet"],
        reason="prior-quality category is explicit; all provided priors resolved without draft-quality flags",
    )


def _soft_node_fields(domain_pack: DomainPack, *node_names: str) -> list[str]:
    node_set = set(domain_pack.soft_nodes)
    return [f"domain_pack.soft_nodes.{node_name}" for node_name in node_names if node_name in node_set]


def _prior_ids(prior_resolutions: PriorResolutionSet | None) -> list[str]:
    if prior_resolutions is None:
        return []
    return [resolution.prior_id for resolution in prior_resolutions.resolutions]


def _deferred_item(
    category: str,
    *,
    reason: str,
    required_data: list[str],
) -> UncertaintyBudgetEvaluationItem:
    return UncertaintyBudgetEvaluationItem(
        category=category,
        status="deferred",
        source=_SOURCE,
        required_data=required_data,
        reason=reason,
    )


def _unique(values) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
