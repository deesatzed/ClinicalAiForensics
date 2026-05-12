"""Deterministic Decision Profile assembly.

The profiler is intentionally an assembly layer. It carries forward explicit
safety gates, priors, simulations, uncertainty-budget items, and VOI items, but
does not invent decision-fitness formulas, ranking weights, or clinical
recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import ValidationError

from .loader_errors import validation_summary
from .models import (
    ClinicalDecisionEpisode,
    DecisionOption,
    DecisionProfileEvaluation,
    DecisionProfileEvaluationSet,
    DecisionProfileEvaluationStatus,
    DecisionProfileInputSummary,
    DomainPack,
    MonteCarloPriorSimulation,
    MonteCarloSimulationResult,
    PriorResolution,
    PriorResolutionSet,
    SafetyGateEvaluation,
    SafetyGateEvaluationSet,
    UncertaintyBudgetEvaluationSet,
    ValueOfInformationEvaluationSet,
)


_PROFILE_SCHEMA_SOURCE = "pdde_v0_3_first_principles_final/schemas/decision_profile.schema.json"
_DECISION_FITNESS_DEFERRED_REASON = (
    "No explicit decision-fitness formula, ranking threshold, or option utility was provided; "
    "the profiler assembled evidence only and did not create a final recommendation."
)


@dataclass(frozen=True)
class _OptionSpec:
    option_id: str
    source: str
    option_label: str | None = None
    valid: bool = True
    reason: str | None = None


def assemble_decision_profiles(
    cde: ClinicalDecisionEpisode,
    domain_pack: DomainPack,
    *,
    safety_gates: SafetyGateEvaluationSet | None = None,
    prior_resolutions: PriorResolutionSet | None = None,
    simulation: MonteCarloSimulationResult | None = None,
    uncertainty_budget: UncertaintyBudgetEvaluationSet | None = None,
    value_of_information: ValueOfInformationEvaluationSet | None = None,
) -> DecisionProfileEvaluationSet:
    """Assemble typed Decision Profile status records without hidden scoring."""

    option_specs = _option_specs(cde, domain_pack)
    input_summaries = _input_summaries(
        option_specs=option_specs,
        domain_pack=domain_pack,
        safety_gates=safety_gates,
        prior_resolutions=prior_resolutions,
        simulation=simulation,
        uncertainty_budget=uncertainty_budget,
        value_of_information=value_of_information,
    )
    profiles = [
        _assemble_profile(
            spec,
            domain_pack=domain_pack,
            safety_gates=safety_gates,
            prior_resolutions=prior_resolutions,
            simulation=simulation,
            uncertainty_budget=uncertainty_budget,
            value_of_information=value_of_information,
        )
        for spec in option_specs
    ]

    return DecisionProfileEvaluationSet(
        cde_id=cde.cde_id,
        domain_pack_id=domain_pack.domain_pack_id,
        profiles=profiles,
        input_summaries=input_summaries,
    )


def _assemble_profile(
    spec: _OptionSpec,
    *,
    domain_pack: DomainPack,
    safety_gates: SafetyGateEvaluationSet | None,
    prior_resolutions: PriorResolutionSet | None,
    simulation: MonteCarloSimulationResult | None,
    uncertainty_budget: UncertaintyBudgetEvaluationSet | None,
    value_of_information: ValueOfInformationEvaluationSet | None,
) -> DecisionProfileEvaluation:
    direct_gates = _direct_gates(spec.option_id, safety_gates)
    active_blockers = _gate_summaries(direct_gates, "blocked")
    active_triggers = _gate_summaries(direct_gates, "triggered")
    missing_data = _gate_summaries(direct_gates, "missing")
    supporting_gates = _gate_summaries(direct_gates, "passed")
    unsupported_inputs = _gate_summaries(direct_gates, "unsupported")
    deferred_reasons = [_DECISION_FITNESS_DEFERRED_REASON]
    provenance_references = [spec.source, _PROFILE_SCHEMA_SOURCE]
    provenance_references.extend(_gate_sources(direct_gates))

    if not spec.valid and spec.reason is not None:
        unsupported_inputs.append(spec.reason)

    related_prior_ids = _related_prior_ids(spec.option_id, domain_pack)
    supporting_priors, prior_unsupported, prior_sources = _prior_summaries(
        related_prior_ids,
        prior_resolutions,
        domain_pack,
    )
    unsupported_inputs.extend(prior_unsupported)
    provenance_references.extend(prior_sources)

    supporting_simulations, simulation_unsupported, simulation_sources = _simulation_summaries(
        related_prior_ids,
        simulation,
    )
    unsupported_inputs.extend(simulation_unsupported)
    provenance_references.extend(simulation_sources)

    uncertainty_items = _uncertainty_summaries(uncertainty_budget)
    value_of_information_items = _value_of_information_summaries(value_of_information)
    deferred_reasons.extend(_deferred_reasons(safety_gates, prior_resolutions, simulation))
    deferred_reasons.extend(_uncertainty_deferred_reasons(uncertainty_budget))
    deferred_reasons.extend(_value_of_information_deferred_reasons(value_of_information))

    status = _profile_status(
        spec=spec,
        safety_gates=safety_gates,
        active_blockers=active_blockers,
        active_triggers=active_triggers,
        missing_data=missing_data,
        unsupported_inputs=unsupported_inputs,
    )

    return DecisionProfileEvaluation(
        option_id=spec.option_id,
        option_label=spec.option_label,
        status=status,
        reason=_profile_reason(
            status,
            active_blockers=active_blockers,
            active_triggers=active_triggers,
            missing_data=missing_data,
            unsupported_inputs=unsupported_inputs,
        ),
        source=spec.source,
        active_blockers=active_blockers,
        active_triggers=active_triggers,
        missing_data=missing_data,
        supporting_gates=supporting_gates,
        unsupported_inputs=unsupported_inputs,
        supporting_priors=supporting_priors,
        supporting_simulations=supporting_simulations,
        uncertainty_items=uncertainty_items,
        value_of_information_items=value_of_information_items,
        deferred_reasons=_unique(deferred_reasons),
        provenance_references=_unique(provenance_references),
    )


def _profile_status(
    *,
    spec: _OptionSpec,
    safety_gates: SafetyGateEvaluationSet | None,
    active_blockers: list[str],
    active_triggers: list[str],
    missing_data: list[str],
    unsupported_inputs: list[str],
) -> DecisionProfileEvaluationStatus:
    if not spec.valid:
        return "unsupported"
    if safety_gates is None:
        return "deferred"
    if active_blockers:
        return "blocked"
    if active_triggers:
        return "triggered"
    if missing_data:
        return "missing"
    if unsupported_inputs:
        return "unsupported"
    return "eligible"


def _profile_reason(
    status: DecisionProfileEvaluationStatus,
    *,
    active_blockers: list[str],
    active_triggers: list[str],
    missing_data: list[str],
    unsupported_inputs: list[str],
) -> str:
    if status == "blocked":
        return f"Blocked by explicit safety gate(s): {'; '.join(active_blockers)}"
    if status == "triggered":
        return f"Triggered by explicit safety gate(s): {'; '.join(active_triggers)}"
    if status == "missing":
        return f"Missing required safety-gate input(s): {'; '.join(missing_data)}"
    if status == "unsupported":
        return f"Unsupported profile input(s): {'; '.join(unsupported_inputs)}"
    if status == "deferred":
        return "Decision profiling is deferred because safety gate evaluations were not provided."
    return (
        "No active explicit safety-gate blocker, trigger, or missing direct gate input was found; "
        "this is an eligibility assembly, not a recommendation or ranking."
    )


def _option_specs(cde: ClinicalDecisionEpisode, domain_pack: DomainPack) -> list[_OptionSpec]:
    specs: list[_OptionSpec] = []
    valid_domain_option_ids: set[str] = set()

    for index, raw_option in enumerate(domain_pack.decision_options):
        source = f"domain_pack:{domain_pack.domain_pack_id}.decision_options[{index}]"
        if isinstance(raw_option, DecisionOption):
            specs.append(
                _OptionSpec(
                    option_id=raw_option.id,
                    option_label=raw_option.label,
                    source=f"domain_pack:{domain_pack.domain_pack_id}.decision_options.{raw_option.id}",
                )
            )
            valid_domain_option_ids.add(raw_option.id)
            continue
        try:
            option = DecisionOption.model_validate(raw_option)
        except ValidationError as exc:
            specs.append(
                _OptionSpec(
                    option_id=f"<invalid:{index}>",
                    source=source,
                    valid=False,
                    reason=f"{source} failed validation: {validation_summary(exc)}",
                )
            )
            continue
        specs.append(
            _OptionSpec(
                option_id=option.id,
                option_label=option.label,
                source=f"domain_pack:{domain_pack.domain_pack_id}.decision_options.{option.id}",
            )
        )
        valid_domain_option_ids.add(option.id)

    for candidate_option_id in cde.candidate_options:
        if candidate_option_id in valid_domain_option_ids:
            continue
        source = f"cde:{cde.cde_id}.candidate_options.{candidate_option_id}"
        specs.append(
            _OptionSpec(
                option_id=candidate_option_id,
                source=source,
                valid=False,
                reason=(
                    f"{source} is not defined in "
                    f"domain_pack:{domain_pack.domain_pack_id}.decision_options"
                ),
            )
        )

    return specs


def _input_summaries(
    *,
    option_specs: list[_OptionSpec],
    domain_pack: DomainPack,
    safety_gates: SafetyGateEvaluationSet | None,
    prior_resolutions: PriorResolutionSet | None,
    simulation: MonteCarloSimulationResult | None,
    uncertainty_budget: UncertaintyBudgetEvaluationSet | None,
    value_of_information: ValueOfInformationEvaluationSet | None,
) -> list[DecisionProfileInputSummary]:
    summaries: list[DecisionProfileInputSummary] = []
    summaries.extend(_option_input_summaries(option_specs))
    summaries.extend(_mapping_input_summaries(domain_pack))
    summaries.extend(_safety_input_summaries(domain_pack, safety_gates))
    summaries.extend(_prior_input_summaries(prior_resolutions))
    summaries.extend(_simulation_input_summaries(simulation))
    summaries.extend(_uncertainty_input_summaries(uncertainty_budget))
    summaries.extend(_voi_input_summaries(value_of_information))
    summaries.append(
        DecisionProfileInputSummary(
            input_type="decision_profiler",
            identifier="decision_fitness_formula",
            status="deferred",
            source=_PROFILE_SCHEMA_SOURCE,
            reason=_DECISION_FITNESS_DEFERRED_REASON,
        )
    )
    return summaries


def _option_input_summaries(option_specs: list[_OptionSpec]) -> list[DecisionProfileInputSummary]:
    return [
        DecisionProfileInputSummary(
            input_type="decision_option",
            identifier=spec.option_id,
            status="defined" if spec.valid else "unsupported",
            source=spec.source,
            reason=spec.reason
            or f"decision option {spec.option_id!r} is explicitly defined in the domain pack",
        )
        for spec in option_specs
    ]


def _mapping_input_summaries(domain_pack: DomainPack) -> list[DecisionProfileInputSummary]:
    summaries: list[DecisionProfileInputSummary] = []

    safety_mappings = domain_pack.mappings.safety_gate_target_by_group()
    if not safety_mappings:
        summaries.append(
            DecisionProfileInputSummary(
                input_type="domain_mapping",
                identifier="safety_gate_targets",
                status="missing",
                source=f"domain_pack:{domain_pack.domain_pack_id}.mappings.safety_gate_targets",
                reason="domain pack does not define explicit safety gate target mappings",
            )
        )
    else:
        for mapping in domain_pack.mappings.safety_gate_targets:
            summaries.append(
                DecisionProfileInputSummary(
                    input_type="domain_mapping",
                    identifier=f"safety_gate_targets.{mapping.gate_group}",
                    status="defined",
                    source=_safety_mapping_source(domain_pack, mapping.gate_group),
                    reason=(
                        f"gate group {mapping.gate_group!r} maps to option "
                        f"{mapping.option_id!r} with matched_status={mapping.matched_status!r}"
                    ),
                )
            )

    for gate_group in domain_pack.hard_gates:
        if gate_group == "wrong_indication_blocks" or gate_group in safety_mappings:
            continue
        summaries.append(
            DecisionProfileInputSummary(
                input_type="domain_mapping",
                identifier=f"safety_gate_targets.{gate_group}",
                status="missing",
                source=f"domain_pack:{domain_pack.domain_pack_id}.mappings.safety_gate_targets",
                reason=(
                    f"hard gate group {gate_group!r} has no explicit safety gate target mapping; "
                    "the safety gate engine will not apply a Python fallback"
                ),
            )
        )

    if not domain_pack.mappings.prior_to_options:
        summaries.append(
            DecisionProfileInputSummary(
                input_type="domain_mapping",
                identifier="prior_to_options",
                status="missing",
                source=f"domain_pack:{domain_pack.domain_pack_id}.mappings.prior_to_options",
                reason="domain pack does not define explicit prior-to-option mappings",
            )
        )
    else:
        for mapping in domain_pack.mappings.prior_to_options:
            summaries.append(
                DecisionProfileInputSummary(
                    input_type="domain_mapping",
                    identifier=f"prior_to_options.{mapping.prior_id}",
                    status="defined",
                    source=_prior_mapping_source(domain_pack, mapping.prior_id),
                    reason=(
                        f"prior {mapping.prior_id!r} maps to option id(s): "
                        f"{', '.join(mapping.option_ids)}"
                    ),
                )
            )

    return summaries


def _safety_input_summaries(
    domain_pack: DomainPack,
    safety_gates: SafetyGateEvaluationSet | None,
) -> list[DecisionProfileInputSummary]:
    if safety_gates is None:
        return [
            DecisionProfileInputSummary(
                input_type="safety_gate",
                identifier="SafetyGateEvaluationSet",
                status="deferred",
                source=f"domain_pack:{domain_pack.domain_pack_id}.hard_gates",
                reason="safety gate evaluations were not provided to the decision profiler",
            )
        ]

    return [
        DecisionProfileInputSummary(
            input_type="safety_gate",
            identifier=_gate_identifier(evaluation),
            status=evaluation.status,
            source=evaluation.source or f"domain_pack:{domain_pack.domain_pack_id}.hard_gates.{evaluation.gate_group}",
            reason=f"{evaluation.reason}: {evaluation.evidence}",
        )
        for evaluation in safety_gates.evaluations
    ]


def _prior_input_summaries(
    prior_resolutions: PriorResolutionSet | None,
) -> list[DecisionProfileInputSummary]:
    if prior_resolutions is None:
        return [
            DecisionProfileInputSummary(
                input_type="prior_resolution",
                identifier="PriorResolutionSet",
                status="deferred",
                reason="prior-resolution results were not provided to the decision profiler",
            )
        ]

    return [
        DecisionProfileInputSummary(
            input_type="prior_resolution",
            identifier=resolution.prior_id,
            status=resolution.status,
            source=resolution.source,
            reason=resolution.reason,
        )
        for resolution in prior_resolutions.resolutions
    ]


def _simulation_input_summaries(
    simulation: MonteCarloSimulationResult | None,
) -> list[DecisionProfileInputSummary]:
    if simulation is None:
        return [
            DecisionProfileInputSummary(
                input_type="monte_carlo_simulation",
                identifier="MonteCarloSimulationResult",
                status="deferred",
                reason="Monte Carlo simulation results were not provided to the decision profiler",
            )
        ]

    return [
        DecisionProfileInputSummary(
            input_type="monte_carlo_simulation",
            identifier=prior_simulation.prior_id,
            status=prior_simulation.status,
            source=prior_simulation.source,
            reason=prior_simulation.reason,
        )
        for prior_simulation in simulation.prior_simulations
    ]


def _uncertainty_input_summaries(
    uncertainty_budget: UncertaintyBudgetEvaluationSet | None,
) -> list[DecisionProfileInputSummary]:
    if uncertainty_budget is None:
        return [
            DecisionProfileInputSummary(
                input_type="uncertainty_budget",
                identifier="UncertaintyBudgetEvaluationSet",
                status="deferred",
                reason="uncertainty-budget results were not provided to the decision profiler",
            )
        ]

    return [
        DecisionProfileInputSummary(
            input_type="uncertainty_budget",
            identifier=item.category,
            status=item.status,
            source=item.source,
            reason=item.reason,
        )
        for item in uncertainty_budget.items
    ]


def _voi_input_summaries(
    value_of_information: ValueOfInformationEvaluationSet | None,
) -> list[DecisionProfileInputSummary]:
    if value_of_information is None:
        return [
            DecisionProfileInputSummary(
                input_type="value_of_information",
                identifier="ValueOfInformationEvaluationSet",
                status="deferred",
                reason="value-of-information results were not provided to the decision profiler",
            )
        ]

    return [
        DecisionProfileInputSummary(
            input_type="value_of_information",
            identifier=item.variable,
            status=item.status,
            source=item.source,
            reason=item.reason,
        )
        for item in value_of_information.items
    ]


def _direct_gates(
    option_id: str,
    safety_gates: SafetyGateEvaluationSet | None,
) -> list[SafetyGateEvaluation]:
    if safety_gates is None:
        return []
    return [evaluation for evaluation in safety_gates.evaluations if evaluation.option_id == option_id]


def _gate_sources(gates: list[SafetyGateEvaluation]) -> list[str]:
    sources: list[str] = []
    for gate in gates:
        if gate.source is not None:
            sources.append(gate.source)
        if gate.mapping_source is not None:
            sources.append(gate.mapping_source)
    return sources


def _gate_summaries(gates: list[SafetyGateEvaluation], status: str) -> list[str]:
    return [
        f"{gate.gate_group}: {gate.reason}; {gate.evidence}"
        for gate in gates
        if gate.status == status
    ]


def _gate_identifier(evaluation: SafetyGateEvaluation) -> str:
    target = evaluation.option_id or evaluation.claim_type or evaluation.variable or "unmapped"
    return f"{evaluation.gate_group}:{target}"


def _related_prior_ids(
    option_id: str,
    domain_pack: DomainPack,
) -> list[str]:
    return domain_pack.mappings.prior_ids_by_option().get(option_id, [])


def _prior_summaries(
    related_prior_ids: list[str],
    prior_resolutions: PriorResolutionSet | None,
    domain_pack: DomainPack,
) -> tuple[list[str], list[str], list[str]]:
    if prior_resolutions is None:
        return [], [], []

    by_prior_id = {resolution.prior_id: resolution for resolution in prior_resolutions.resolutions}
    supporting: list[str] = []
    unsupported: list[str] = []
    sources: list[str] = []
    for prior_id in related_prior_ids:
        sources.append(_prior_mapping_source(domain_pack, prior_id))
        resolution = by_prior_id.get(prior_id)
        if resolution is None:
            unsupported.append(
                f"{prior_id}: missing; explicit prior-to-option mapping exists but no "
                "prior-resolution result was provided"
            )
            continue
        summary = _prior_summary(resolution)
        if resolution.source is not None:
            sources.append(resolution.source)
        if resolution.status == "resolved":
            supporting.append(summary)
        else:
            unsupported.append(summary)
    return supporting, unsupported, sources


def _prior_summary(resolution: PriorResolution) -> str:
    source = f"; source={resolution.source}" if resolution.source is not None else ""
    return f"{resolution.prior_id}: {resolution.status}; {resolution.reason}{source}"


def _simulation_summaries(
    related_prior_ids: list[str],
    simulation: MonteCarloSimulationResult | None,
) -> tuple[list[str], list[str], list[str]]:
    if simulation is None:
        return [], [], []

    by_prior_id = {
        prior_simulation.prior_id: prior_simulation
        for prior_simulation in simulation.prior_simulations
    }
    supporting: list[str] = []
    unsupported: list[str] = []
    sources: list[str] = []
    for prior_id in related_prior_ids:
        prior_simulation = by_prior_id.get(prior_id)
        if prior_simulation is None:
            unsupported.append(
                f"{prior_id}: missing; no Monte Carlo simulation result was provided for this related prior"
            )
            continue
        if prior_simulation.source is not None:
            sources.append(prior_simulation.source)
        summary = _simulation_summary(prior_simulation)
        if prior_simulation.status == "sampled":
            supporting.append(summary)
        else:
            unsupported.append(summary)
    return supporting, unsupported, sources


def _simulation_summary(prior_simulation: MonteCarloPriorSimulation) -> str:
    if prior_simulation.status != "sampled":
        return f"{prior_simulation.prior_id}: {prior_simulation.status}; {prior_simulation.reason}"

    return (
        f"{prior_simulation.prior_id}: sampled; sample_count={prior_simulation.sample_count}; "
        f"median={prior_simulation.sample_median:.3f}; p5={prior_simulation.p5:.3f}; "
        f"p95={prior_simulation.p95:.3f}; source={prior_simulation.source}"
    )


def _uncertainty_summaries(
    uncertainty_budget: UncertaintyBudgetEvaluationSet | None,
) -> list[str]:
    if uncertainty_budget is None:
        return []
    return [
        f"{item.category}: {item.status}; {item.reason}"
        for item in uncertainty_budget.items
    ]


def _value_of_information_summaries(
    value_of_information: ValueOfInformationEvaluationSet | None,
) -> list[str]:
    if value_of_information is None:
        return []
    return [
        f"{item.variable}: {item.status}; rank={item.rank}; {item.reason}"
        for item in value_of_information.items
    ]


def _deferred_reasons(
    safety_gates: SafetyGateEvaluationSet | None,
    prior_resolutions: PriorResolutionSet | None,
    simulation: MonteCarloSimulationResult | None,
) -> list[str]:
    reasons = []
    if safety_gates is None:
        reasons.append("Safety gate evaluations are required before option status can be finalized.")
    if prior_resolutions is None:
        reasons.append("Prior-resolution results are required before prior provenance can be attached.")
    if simulation is None:
        reasons.append("Monte Carlo simulation results are required before prior samples can be attached.")
    return reasons


def _uncertainty_deferred_reasons(
    uncertainty_budget: UncertaintyBudgetEvaluationSet | None,
) -> list[str]:
    if uncertainty_budget is None:
        return ["Uncertainty-budget results are required before uncertainty items can be attached."]
    return [
        f"{item.category}: {item.reason}"
        for item in uncertainty_budget.items
        if item.status == "deferred"
    ]


def _value_of_information_deferred_reasons(
    value_of_information: ValueOfInformationEvaluationSet | None,
) -> list[str]:
    if value_of_information is None:
        return ["Value-of-information results are required before VOI items can be attached."]
    return [
        f"{item.variable}: {item.reason}"
        for item in value_of_information.items
        if item.status == "deferred"
    ]


def _safety_mapping_source(domain_pack: DomainPack, gate_group: str) -> str:
    return f"domain_pack:{domain_pack.domain_pack_id}.mappings.safety_gate_targets.{gate_group}"


def _prior_mapping_source(domain_pack: DomainPack, prior_id: str) -> str:
    return f"domain_pack:{domain_pack.domain_pack_id}.mappings.prior_to_options.{prior_id}"


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
