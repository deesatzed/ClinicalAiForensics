"""JSONL provenance logging for PDDE evaluation runs."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable, Sequence
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

from . import __version__
from .pipeline_models import EvaluationPipelineResult
from .status_ledger import build_status_ledger


ProvenanceRecord = dict[str, Any]


def create_provenance_records(
    result: EvaluationPipelineResult,
    *,
    command_name: str,
    report_path: str | Path | None = None,
    timestamp: str | None = None,
    run_id: str | None = None,
) -> list[ProvenanceRecord]:
    """Create JSONL-ready provenance records without raw clinical content."""

    timestamp_value = timestamp or _utc_timestamp()
    report_path_value = str(report_path) if report_path is not None else None
    run_id_value = run_id or _derive_run_id(
        result=result,
        command_name=command_name,
        report_path=report_path_value,
        timestamp=timestamp_value,
    )
    records: list[ProvenanceRecord] = []

    def append(log_type: str, payload: dict[str, Any]) -> None:
        records.append(
            {
                "log_type": log_type,
                "run_id": run_id_value,
                "timestamp": timestamp_value,
                "sequence": len(records),
                "cde_id": result.cde.cde_id,
                "domain_pack_id": result.domain_pack.domain_pack_id,
                "payload": payload,
            }
        )

    append(
        "run_metadata",
        {
            "package_version": __version__,
            "command_name": command_name,
            "workflow_mode": result.workflow_mode,
            "cde_source": result.cde_source,
            "domain_pack_source": result.domain_pack_source,
            "report_path": report_path_value,
            "domain": result.cde.domain,
            "domain_pack_version": result.domain_pack.version,
            "domain_pack_status": result.domain_pack.status,
            "calibration_status": result.domain_pack.calibration_status,
            "n_iterations": result.n_iterations,
            "random_seed": result.random_seed,
            "component_counts": _component_counts(result),
            "provenance_references": _provenance_references(result),
        },
    )
    append("component_status_summary", _component_status_summary(result))

    for evaluation in result.safety_gates.evaluations:
        append(
            "safety_gate_result",
            {
                "gate_group": evaluation.gate_group,
                "target_id": evaluation.option_id or evaluation.claim_type,
                "status": evaluation.status,
                "reason": evaluation.reason,
                "variable": evaluation.variable,
                "condition": evaluation.condition,
                "claim_type": evaluation.claim_type,
                "source": evaluation.source
                or f"domain_pack:{result.domain_pack.domain_pack_id}.hard_gates.{evaluation.gate_group}",
                "mapping_source": evaluation.mapping_source,
            },
        )

    for resolution in result.prior_resolutions.resolutions:
        append(
            "prior_resolution",
            {
                "prior_id": resolution.prior_id,
                "status": resolution.status,
                "source": resolution.source,
                "distribution": resolution.distribution,
                "provenance_class": resolution.provenance_class,
                "normalized_provenance_class": resolution.normalized_provenance_class,
                "confidence_class": resolution.confidence_class,
                "calibration_status": resolution.calibration_status,
                "warning_present": bool(resolution.warning),
            },
        )

    for simulation in result.simulation.prior_simulations:
        append(
            "monte_carlo_prior",
            {
                "prior_id": simulation.prior_id,
                "status": simulation.status,
                "source": simulation.source,
                "distribution": simulation.distribution,
                "sample_count": simulation.sample_count,
                "provenance_class": simulation.provenance_class,
                "confidence_class": simulation.confidence_class,
                "calibration_status": simulation.calibration_status,
                "warning_present": bool(simulation.warning),
            },
        )

    for item in result.uncertainty_budget.items:
        append(
            "uncertainty_budget_item",
            {
                "category": item.category,
                "status": item.status,
                "source": item.source,
                "actionable": item.actionable,
                "could_change_decision": item.could_change_decision,
                "source_fields": item.source_fields,
                "related_variables": item.related_variables,
                "related_prior_ids": item.related_prior_ids,
                "related_gate_groups": item.related_gate_groups,
            },
        )

    for item in result.value_of_information.items:
        append(
            "value_of_information_item",
            {
                "variable": item.variable,
                "status": item.status,
                "source": item.source,
                "rank": item.rank,
                "source_field": item.source_field,
                "actionable": item.actionable,
                "could_change_decision": item.could_change_decision,
                "related_gate_groups": item.related_gate_groups,
            },
        )

    for profile in result.decision_profiles.profiles:
        append(
            "decision_profile",
            {
                "option_id": profile.option_id,
                "status": profile.status,
                "source": profile.source,
                "active_blocker_count": len(profile.active_blockers),
                "active_trigger_count": len(profile.active_triggers),
                "missing_data_count": len(profile.missing_data),
                "unsupported_input_count": len(profile.unsupported_inputs),
                "deferred_reason_count": len(profile.deferred_reasons),
                "supporting_priors": profile.supporting_priors,
                "supporting_simulations": profile.supporting_simulations,
                "uncertainty_items": profile.uncertainty_items,
                "value_of_information_items": profile.value_of_information_items,
                "provenance_references": profile.provenance_references,
            },
        )

    return records


def records_to_jsonl(records: Sequence[ProvenanceRecord]) -> str:
    """Serialize provenance records as deterministic JSONL text."""

    return "".join(_json_line(record) for record in records)


def write_jsonl(records: Sequence[ProvenanceRecord], path: str | Path) -> None:
    """Write provenance records to a JSONL file."""

    log_path = Path(path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(records_to_jsonl(records), encoding="utf-8")


def append_jsonl(records: Sequence[ProvenanceRecord], path: str | Path) -> None:
    """Append provenance records to a JSONL file."""

    log_path = Path(path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(records_to_jsonl(records))


def write_provenance_log(
    result: EvaluationPipelineResult,
    path: str | Path,
    *,
    command_name: str,
    report_path: str | Path | None = None,
    timestamp: str | None = None,
    run_id: str | None = None,
    append: bool = True,
) -> list[ProvenanceRecord]:
    """Create and write provenance records, returning the records for callers/tests."""

    records = create_provenance_records(
        result,
        command_name=command_name,
        report_path=report_path,
        timestamp=timestamp,
        run_id=run_id,
    )
    if append:
        append_jsonl(records, path)
    else:
        write_jsonl(records, path)
    return records


def _component_counts(result: EvaluationPipelineResult) -> dict[str, int]:
    return {
        "safety_gates": len(result.safety_gates.evaluations),
        "prior_resolutions": len(result.prior_resolutions.resolutions),
        "monte_carlo_priors": len(result.simulation.prior_simulations),
        "uncertainty_budget_items": len(result.uncertainty_budget.items),
        "value_of_information_items": len(result.value_of_information.items),
        "decision_profiles": len(result.decision_profiles.profiles),
    }


def _component_status_summary(result: EvaluationPipelineResult) -> dict[str, Any]:
    return {
        "safety_gates": _status_counts(evaluation.status for evaluation in result.safety_gates.evaluations),
        "prior_resolutions": _status_counts(resolution.status for resolution in result.prior_resolutions.resolutions),
        "monte_carlo_priors": _status_counts(simulation.status for simulation in result.simulation.prior_simulations),
        "uncertainty_budget_items": _status_counts(item.status for item in result.uncertainty_budget.items),
        "value_of_information_items": _status_counts(item.status for item in result.value_of_information.items),
        "decision_profiles": _status_counts(profile.status for profile in result.decision_profiles.profiles),
        "status_ledger": build_status_ledger(result).status_counts_by_component(),
    }


def _status_counts(statuses: Iterable[str]) -> dict[str, int]:
    return dict(sorted(Counter(statuses).items()))


def _provenance_references(result: EvaluationPipelineResult) -> list[str]:
    return _unique(
        [
            result.cde_source,
            result.domain_pack_source,
            *[evaluation.source for evaluation in result.safety_gates.evaluations],
            *[evaluation.mapping_source for evaluation in result.safety_gates.evaluations],
            *[resolution.source for resolution in result.prior_resolutions.resolutions],
            *[simulation.source for simulation in result.simulation.prior_simulations],
            *[item.source for item in result.uncertainty_budget.items],
            *[item.source for item in result.value_of_information.items],
            *[summary.source for summary in result.decision_profiles.input_summaries],
            *[
                reference
                for profile in result.decision_profiles.profiles
                for reference in profile.provenance_references
            ],
        ]
    )


def _derive_run_id(
    *,
    result: EvaluationPipelineResult,
    command_name: str,
    report_path: str | None,
    timestamp: str,
) -> str:
    seed = {
        "timestamp": timestamp,
        "command_name": command_name,
        "cde_source": result.cde_source,
        "domain_pack_source": result.domain_pack_source,
        "cde_id": result.cde.cde_id,
        "domain_pack_id": result.domain_pack.domain_pack_id,
        "n_iterations": result.n_iterations,
        "random_seed": result.random_seed,
        "report_path": report_path,
    }
    digest = sha256(json.dumps(seed, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return f"run_{digest[:16]}"


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _json_line(record: ProvenanceRecord) -> str:
    return json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"


def _unique(values: Iterable[str | None]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value is None or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
