"""Shared status-ledger projection for reports and provenance summaries."""

from __future__ import annotations

from collections.abc import Iterable

from .component_models import (
    DecisionProfileInputSummary,
    StatusLedger,
    StatusLedgerComponent,
    StatusLedgerRow,
)
from .pipeline_models import EvaluationPipelineResult


_INPUT_COMPONENTS: dict[str, StatusLedgerComponent] = {
    "decision_option": "decision_option",
    "domain_mapping": "domain_mapping",
    "decision_profiler": "decision_profiler",
}


def build_status_ledger(result: EvaluationPipelineResult) -> StatusLedger:
    """Project visible pipeline component statuses into one typed ledger.

    The ledger is a projection only. It does not evaluate gates, resolve priors,
    sample distributions, or assemble profiles.
    """

    rows: list[StatusLedgerRow] = []
    rows.extend(_input_summary_rows(result))
    rows.extend(_safety_gate_rows(result))
    rows.extend(_prior_resolution_rows(result))
    rows.extend(_monte_carlo_rows(result))
    rows.extend(_uncertainty_budget_rows(result))
    rows.extend(_value_of_information_rows(result))
    rows.extend(_local_overlay_rows(result))
    rows.extend(_decision_profile_rows(result))

    return StatusLedger(
        cde_id=result.cde.cde_id,
        domain_pack_id=result.domain_pack.domain_pack_id,
        rows=rows,
    )


def _input_summary_rows(result: EvaluationPipelineResult) -> list[StatusLedgerRow]:
    return [
        StatusLedgerRow(
            component=_INPUT_COMPONENTS[summary.input_type],
            identifier=summary.identifier,
            status=summary.status,
            reason=summary.reason,
            source=summary.source,
            provenance_references=_unique([summary.source]),
            related_entity_ids=_input_related_entities(summary),
        )
        for summary in result.decision_profiles.input_summaries
        if summary.input_type in _INPUT_COMPONENTS
    ]


def _safety_gate_rows(result: EvaluationPipelineResult) -> list[StatusLedgerRow]:
    rows: list[StatusLedgerRow] = []
    for evaluation in result.safety_gates.evaluations:
        source = (
            evaluation.source
            or f"domain_pack:{result.domain_pack.domain_pack_id}.hard_gates.{evaluation.gate_group}"
        )
        rows.append(
            StatusLedgerRow(
                component="safety_gate",
                identifier=_safety_identifier(evaluation.gate_group, evaluation.option_id, evaluation.claim_type),
                status=evaluation.status,
                reason=f"{evaluation.reason}: {evaluation.evidence}",
                source=source,
                provenance_references=_unique([source, evaluation.mapping_source]),
                related_entity_ids=_related_entities(
                    gate_groups=[evaluation.gate_group],
                    option_ids=[evaluation.option_id],
                    variables=[evaluation.variable],
                    claim_types=[evaluation.claim_type],
                ),
            )
        )
    return rows


def _prior_resolution_rows(result: EvaluationPipelineResult) -> list[StatusLedgerRow]:
    return [
        StatusLedgerRow(
            component="prior_resolution",
            identifier=resolution.prior_id,
            status=resolution.status,
            reason=resolution.reason,
            source=resolution.source,
            provenance_references=_unique([resolution.source]),
            related_entity_ids=_related_entities(prior_ids=[resolution.prior_id]),
        )
        for resolution in result.prior_resolutions.resolutions
    ]


def _monte_carlo_rows(result: EvaluationPipelineResult) -> list[StatusLedgerRow]:
    return [
        StatusLedgerRow(
            component="monte_carlo_prior",
            identifier=simulation.prior_id,
            status=simulation.status,
            reason=simulation.reason,
            source=simulation.source,
            provenance_references=_unique([simulation.source]),
            related_entity_ids=_related_entities(prior_ids=[simulation.prior_id]),
        )
        for simulation in result.simulation.prior_simulations
    ]


def _uncertainty_budget_rows(result: EvaluationPipelineResult) -> list[StatusLedgerRow]:
    return [
        StatusLedgerRow(
            component="uncertainty_budget_item",
            identifier=item.category,
            status=item.status,
            reason=item.reason,
            source=item.source,
            provenance_references=_unique([item.source]),
            related_entity_ids=_related_entities(
                variables=item.related_variables,
                prior_ids=item.related_prior_ids,
                gate_groups=item.related_gate_groups,
            ),
        )
        for item in result.uncertainty_budget.items
    ]


def _value_of_information_rows(result: EvaluationPipelineResult) -> list[StatusLedgerRow]:
    return [
        StatusLedgerRow(
            component="value_of_information_item",
            identifier=item.variable,
            status=item.status,
            reason=item.reason,
            source=item.source,
            provenance_references=_unique([item.source]),
            related_entity_ids=_related_entities(
                variables=[item.variable],
                gate_groups=item.related_gate_groups,
            ),
        )
        for item in result.value_of_information.items
    ]


def _local_overlay_rows(result: EvaluationPipelineResult) -> list[StatusLedgerRow]:
    return [
        StatusLedgerRow(
            component="local_overlay",
            identifier=item.overlay_id,
            status=item.status,
            reason=item.reason,
            source=item.source,
            provenance_references=_unique([item.source]),
            related_entity_ids=_related_entities(local_overlay_ids=[item.overlay_id]),
        )
        for item in result.local_overlay.items
    ]


def _decision_profile_rows(result: EvaluationPipelineResult) -> list[StatusLedgerRow]:
    prior_ids_by_option = result.domain_pack.mappings.prior_ids_by_option()
    return [
        StatusLedgerRow(
            component="decision_profile",
            identifier=profile.option_id,
            status=profile.status,
            reason=profile.reason,
            source=profile.source,
            provenance_references=profile.provenance_references,
            related_entity_ids=_related_entities(
                option_ids=[profile.option_id],
                prior_ids=prior_ids_by_option.get(profile.option_id, []),
            ),
        )
        for profile in result.decision_profiles.profiles
    ]


def _input_related_entities(summary: DecisionProfileInputSummary) -> dict[str, list[str]]:
    if summary.input_type == "decision_option":
        return _related_entities(option_ids=[summary.identifier])
    if summary.input_type == "domain_mapping":
        if summary.identifier.startswith("safety_gate_targets."):
            return _related_entities(gate_groups=[summary.identifier.rsplit(".", maxsplit=1)[-1]])
        if summary.identifier.startswith("prior_to_options."):
            return _related_entities(prior_ids=[summary.identifier.rsplit(".", maxsplit=1)[-1]])
    return {}


def _safety_identifier(
    gate_group: str,
    option_id: str | None,
    claim_type: str | None,
) -> str:
    return f"{gate_group}:{option_id or claim_type or 'unmapped'}"


def _related_entities(
    *,
    option_ids: Iterable[str | None] = (),
    prior_ids: Iterable[str | None] = (),
    gate_groups: Iterable[str | None] = (),
    variables: Iterable[str | None] = (),
    claim_types: Iterable[str | None] = (),
    uncertainty_items: Iterable[str | None] = (),
    value_of_information_items: Iterable[str | None] = (),
    local_overlay_ids: Iterable[str | None] = (),
) -> dict[str, list[str]]:
    related = {
        "option_ids": _unique(option_ids),
        "prior_ids": _unique(prior_ids),
        "gate_groups": _unique(gate_groups),
        "variables": _unique(variables),
        "claim_types": _unique(claim_types),
        "uncertainty_items": _unique(uncertainty_items),
        "value_of_information_items": _unique(value_of_information_items),
        "local_overlay_ids": _unique(local_overlay_ids),
    }
    return {key: values for key, values in related.items() if values}


def _unique(values: Iterable[str | None]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value is None or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
