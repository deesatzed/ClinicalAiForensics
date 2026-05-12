"""Deterministic value-of-information item evaluation.

This layer only evaluates explicit variables listed by a loaded domain pack. It
does not calculate expected value, infer clinical thresholds, or synthesize
decision-profile rankings.
"""

from __future__ import annotations

from typing import Any

from .component_models import (
    SafetyGateEvaluationSet,
    ValueOfInformationEvaluation,
    ValueOfInformationEvaluationSet,
)
from .input_models import ClinicalDecisionEpisode, DomainPack


_CDE_FIELD_ALIASES = {
    "post_diuresis_sbp": "sbp",
}
_REQUIRED_DATA_LABELS = {
    "egfr": "Provide CDE patient_state.egfr.",
    "potassium": "Provide CDE patient_state.potassium.",
    "post_diuresis_sbp": "Provide CDE patient_state.sbp for post-diuresis SBP.",
    "volume_status": "Provide CDE patient_state.volume_status.",
    "dka_risk": "Provide CDE patient_state.dka_risk.",
    "follow_up_available": "Provide CDE patient_state.follow_up_available.",
    "medication_access": "Provide CDE patient_state.medication_access.",
    "patient_preference": "Provide CDE patient_state.patient_preference.",
}


def evaluate_value_of_information(
    cde: ClinicalDecisionEpisode,
    domain_pack: DomainPack,
    *,
    safety_gates: SafetyGateEvaluationSet | None = None,
) -> ValueOfInformationEvaluationSet:
    """Return transparent VOI status records for explicit domain-pack variables."""

    if not domain_pack.value_of_information_variables:
        return ValueOfInformationEvaluationSet(
            cde_id=cde.cde_id,
            domain_pack_id=domain_pack.domain_pack_id,
            items=[
                ValueOfInformationEvaluation(
                    variable="value_of_information_variables",
                    status="deferred",
                    source=f"domain_pack:{domain_pack.domain_pack_id}.value_of_information_variables",
                    reason="domain pack does not define explicit value-of-information variables",
                    required_data=["Add explicit value_of_information_variables to the domain pack."],
                )
            ],
        )

    items: list[ValueOfInformationEvaluation] = []
    rank = 1
    for raw_variable in domain_pack.value_of_information_variables:
        item = _evaluate_variable(cde, domain_pack, raw_variable, rank, safety_gates)
        items.append(item)
        if item.rank is not None:
            rank += 1

    return ValueOfInformationEvaluationSet(
        cde_id=cde.cde_id,
        domain_pack_id=domain_pack.domain_pack_id,
        items=items,
    )


def _evaluate_variable(
    cde: ClinicalDecisionEpisode,
    domain_pack: DomainPack,
    raw_variable: Any,
    rank: int,
    safety_gates: SafetyGateEvaluationSet | None,
) -> ValueOfInformationEvaluation:
    source = f"domain_pack:{domain_pack.domain_pack_id}.value_of_information_variables"
    if not isinstance(raw_variable, str) or not raw_variable.strip():
        return ValueOfInformationEvaluation(
            variable=f"<invalid:{raw_variable!r}>",
            status="unsupported",
            source=source,
            reason="value-of-information variable definitions must be non-empty strings",
        )

    variable = raw_variable.strip()
    cde_field = _CDE_FIELD_ALIASES.get(variable, variable)
    source_field = f"patient_state.{cde_field}"
    related_gate_groups = _related_gate_groups(safety_gates, cde_field)
    value = cde.patient_state.get(cde_field)

    if value is None:
        return ValueOfInformationEvaluation(
            variable=variable,
            status="missing",
            rank=rank,
            source=source,
            source_field=source_field,
            actionable=True,
            could_change_decision=True,
            reason=(
                f"{source_field} is absent; no numeric VOI score was computed because no "
                "explicit VOI formula is defined"
            ),
            required_data=[_REQUIRED_DATA_LABELS.get(variable, f"Provide CDE {source_field}.")],
            related_gate_groups=related_gate_groups,
        )

    return ValueOfInformationEvaluation(
        variable=variable,
        status="present",
        rank=rank,
        source=source,
        source_field=source_field,
        actionable=False,
        could_change_decision=False,
        reason=(
            f"{source_field} is present; item remains visible for VOI reporting, "
            "but no numeric VOI score was computed because no explicit VOI formula is defined"
        ),
        related_gate_groups=related_gate_groups,
    )


def _related_gate_groups(
    safety_gates: SafetyGateEvaluationSet | None,
    cde_field: str,
) -> list[str]:
    if safety_gates is None:
        return []
    gate_groups = {
        evaluation.gate_group
        for evaluation in safety_gates.evaluations
        if evaluation.variable == cde_field
    }
    return sorted(gate_groups)
