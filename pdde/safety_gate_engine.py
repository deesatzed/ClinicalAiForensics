"""Deterministic safety gate evaluation.

The engine only evaluates explicit hard gates from a loaded domain pack against a
loaded CDE. It does not resolve priors, run Monte Carlo, or infer clinical facts
that are not present in the CDE.
"""

from __future__ import annotations

import re
from typing import Any, Literal

from .models import (
    ClinicalDecisionEpisode,
    DomainPack,
    SafetyGate,
    SafetyGateEvaluation,
    SafetyGateEvaluationSet,
)


_MISSING = object()
_NUMERIC_CONDITION = re.compile(r"^(<=|>=|<|>|==|=)\s*(-?\d+(?:\.\d+)?)$")
_RANGE_CONDITION = re.compile(r"^(-?\d+(?:\.\d+)?)\s*-\s*(-?\d+(?:\.\d+)?)$")
_COMPOUND_STRING_CONDITIONS: dict[str, set[str]] = {
    "active_ketosis_or_prior_euglycemic_dka_high_risk": {
        "active_ketosis",
        "prior_euglycemic_dka",
        "prior_euglycemic_dka_high_risk",
        "high_risk",
        "active_ketosis_or_prior_euglycemic_dka_high_risk",
    },
    "persistent_or_worsening": {
        "persistent",
        "worsening",
        "persistent_or_worsening",
    },
    "still_congested_severe": {
        "severely_congested",
        "still_congested_severe",
    },
}


class UnsupportedSafetyGate(ValueError):
    """Raised internally when a gate cannot be deterministically evaluated."""


def evaluate_safety_gates(
    cde: ClinicalDecisionEpisode,
    domain_pack: DomainPack,
) -> SafetyGateEvaluationSet:
    """Evaluate deterministic hard gates and return typed result records."""

    option_ids = {option.id for option in domain_pack.decision_options}
    gate_targets = domain_pack.mappings.safety_gate_target_by_group()
    evaluations: list[SafetyGateEvaluation] = []

    for gate_group, gates in domain_pack.hard_gates.items():
        if gate_group == "wrong_indication_blocks":
            evaluations.extend(_unsupported_claim_gate(domain_pack, gate_group, gate) for gate in gates)
            continue

        target = gate_targets.get(gate_group)
        if target is None:
            evaluations.extend(
                _unsupported_gate_group(
                    domain_pack,
                    gate_group,
                    gate,
                    evidence=(
                        f"missing explicit safety_gate_targets mapping for hard gate group "
                        f"{gate_group!r}; no Python fallback was applied"
                    ),
                )
                for gate in gates
            )
            continue

        option_id = target.option_id
        matched_status = target.matched_status
        mapping_source = _mapping_source(domain_pack, gate_group)
        if option_id not in option_ids:
            evaluations.extend(
                _unsupported_gate_group(
                    domain_pack,
                    gate_group,
                    gate,
                    evidence=f"gate group {gate_group!r} maps to missing option {option_id!r}",
                    mapping_source=mapping_source,
                )
                for gate in gates
            )
            continue

        for gate in gates:
            evaluations.append(
                _evaluate_variable_gate(
                    cde,
                    domain_pack,
                    gate_group,
                    option_id,
                    matched_status,
                    gate,
                    mapping_source=mapping_source,
                )
            )

    return SafetyGateEvaluationSet(
        cde_id=cde.cde_id,
        domain_pack_id=domain_pack.domain_pack_id,
        evaluations=evaluations,
    )


def _evaluate_variable_gate(
    cde: ClinicalDecisionEpisode,
    domain_pack: DomainPack,
    gate_group: str,
    option_id: str,
    matched_status: Literal["blocked", "triggered"],
    gate: SafetyGate,
    *,
    mapping_source: str,
) -> SafetyGateEvaluation:
    if gate.variable is None or gate.condition is None:
        return SafetyGateEvaluation(
            gate_group=gate_group,
            option_id=option_id,
            status="unsupported",
            reason=gate.reason,
            evidence="variable gate requires both variable and condition",
            source=_gate_source(domain_pack, gate_group),
            mapping_source=mapping_source,
            variable=gate.variable,
            condition=gate.condition,
            claim_type=gate.claim_type,
        )

    observed_value = cde.patient_state.get(gate.variable, _MISSING)
    if observed_value is _MISSING or observed_value is None:
        return SafetyGateEvaluation(
            gate_group=gate_group,
            option_id=option_id,
            status="missing",
            reason=gate.reason,
            evidence=f"{gate.variable} is missing; condition {gate.condition} was not evaluated",
            source=_gate_source(domain_pack, gate_group),
            mapping_source=mapping_source,
            variable=gate.variable,
            condition=gate.condition,
            observed_value=None,
        )

    try:
        matched = _condition_matches(observed_value, gate.condition)
    except UnsupportedSafetyGate as exc:
        return SafetyGateEvaluation(
            gate_group=gate_group,
            option_id=option_id,
            status="unsupported",
            reason=gate.reason,
            evidence=str(exc),
            source=_gate_source(domain_pack, gate_group),
            mapping_source=mapping_source,
            variable=gate.variable,
            condition=gate.condition,
            observed_value=observed_value,
        )

    status = matched_status if matched else "passed"
    comparator = "meets" if matched else "does not meet"
    return SafetyGateEvaluation(
        gate_group=gate_group,
        option_id=option_id,
        status=status,
        reason=gate.reason,
        evidence=f"{gate.variable}={observed_value!r} {comparator} {gate.condition}",
        source=_gate_source(domain_pack, gate_group),
        mapping_source=mapping_source,
        variable=gate.variable,
        condition=gate.condition,
        observed_value=observed_value,
    )


def _condition_matches(value: Any, condition: str) -> bool:
    normalized_condition = condition.strip()

    numeric_match = _NUMERIC_CONDITION.match(normalized_condition)
    if numeric_match is not None:
        operator, threshold = numeric_match.groups()
        return _compare_number(value, operator, float(threshold), normalized_condition)

    range_match = _RANGE_CONDITION.match(normalized_condition)
    if range_match is not None:
        lower, upper = (float(part) for part in range_match.groups())
        number = _coerce_number(value, normalized_condition)
        return lower <= number <= upper

    lowered_condition = normalized_condition.lower()
    if lowered_condition in {"true", "false"}:
        return _coerce_bool(value, normalized_condition) is (lowered_condition == "true")

    if isinstance(value, bool):
        raise UnsupportedSafetyGate(
            f"condition {normalized_condition!r} is not a boolean condition for boolean value {value!r}"
        )
    if isinstance(value, int | float):
        raise UnsupportedSafetyGate(
            f"condition {normalized_condition!r} is not a numeric condition for numeric value {value!r}"
        )
    if not isinstance(value, str):
        raise UnsupportedSafetyGate(
            f"condition {normalized_condition!r} cannot be evaluated for value {value!r}"
        )

    normalized_value = value.strip().lower()
    if lowered_condition in _COMPOUND_STRING_CONDITIONS:
        return normalized_value in _COMPOUND_STRING_CONDITIONS[lowered_condition]
    return normalized_value == lowered_condition


def _compare_number(value: Any, operator: str, threshold: float, condition: str) -> bool:
    number = _coerce_number(value, condition)
    if operator == "<":
        return number < threshold
    if operator == "<=":
        return number <= threshold
    if operator == ">":
        return number > threshold
    if operator == ">=":
        return number >= threshold
    return number == threshold


def _coerce_number(value: Any, condition: str) -> float:
    if isinstance(value, bool):
        raise UnsupportedSafetyGate(f"condition {condition!r} requires a numeric value, got {value!r}")
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise UnsupportedSafetyGate(
            f"condition {condition!r} requires a numeric value, got {value!r}"
        ) from exc


def _coerce_bool(value: Any, condition: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().lower() in {"true", "false"}:
        return value.strip().lower() == "true"
    raise UnsupportedSafetyGate(f"condition {condition!r} requires a boolean value, got {value!r}")


def _unsupported_claim_gate(
    domain_pack: DomainPack,
    gate_group: str,
    gate: SafetyGate,
) -> SafetyGateEvaluation:
    claim_type = gate.claim_type or "<missing>"
    return SafetyGateEvaluation(
        gate_group=gate_group,
        status="unsupported",
        reason=gate.reason,
        evidence=f"claim_type gate {claim_type!r} requires mapped claim types; AI answer mapping is deferred",
        source=_gate_source(domain_pack, gate_group),
        claim_type=gate.claim_type,
    )


def _unsupported_gate_group(
    domain_pack: DomainPack,
    gate_group: str,
    gate: SafetyGate,
    evidence: str | None = None,
    mapping_source: str | None = None,
) -> SafetyGateEvaluation:
    return SafetyGateEvaluation(
        gate_group=gate_group,
        status="unsupported",
        reason=gate.reason,
        evidence=evidence or f"unsupported hard gate group {gate_group!r}; no deterministic mapping defined",
        source=_gate_source(domain_pack, gate_group),
        mapping_source=mapping_source,
        variable=gate.variable,
        condition=gate.condition,
        claim_type=gate.claim_type,
    )


def _gate_source(domain_pack: DomainPack, gate_group: str) -> str:
    return f"domain_pack:{domain_pack.domain_pack_id}.hard_gates.{gate_group}"


def _mapping_source(domain_pack: DomainPack, gate_group: str) -> str:
    return f"domain_pack:{domain_pack.domain_pack_id}.mappings.safety_gate_targets.{gate_group}"
