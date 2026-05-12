from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from pdde.evaluation_pipeline import run_evaluation_pipeline
from pdde.models import StatusLedgerRow
from pdde.status_ledger import build_status_ledger


ROOT = Path(__file__).resolve().parents[1]
V03_CDE = ROOT / "pdde_v0_3_first_principles_final/examples/hf_cde_stable.json"
HIGH_K_CDE = ROOT / "examples/hf_cde_high_k.json"
V03_DOMAIN = (
    ROOT / "pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml"
)


def _result(cde_path: Path = V03_CDE):
    return run_evaluation_pipeline(
        cde_path=cde_path,
        domain_pack_path=V03_DOMAIN,
        n_iterations=5,
        random_seed=17,
    )


def test_status_ledger_projects_all_pipeline_components() -> None:
    ledger = build_status_ledger(_result())

    assert ledger.cde_id == "hf_cde_stable"
    assert ledger.domain_pack_id == "hf_ed_discharge_v0_3"
    assert {
        "decision_option",
        "domain_mapping",
        "safety_gate",
        "prior_resolution",
        "monte_carlo_prior",
        "uncertainty_budget_item",
        "value_of_information_item",
        "decision_profile",
        "decision_profiler",
    }.issubset({row.component for row in ledger.rows})

    statuses = {(row.component, row.status) for row in ledger.rows}
    assert ("prior_resolution", "resolved") in statuses
    assert ("monte_carlo_prior", "sampled") in statuses
    assert ("value_of_information_item", "present") in statuses
    assert ("decision_profile", "eligible") in statuses
    assert ("decision_profiler", "deferred") in statuses


def test_unresolved_status_ledger_rows_do_not_disappear() -> None:
    canonical_ledger = build_status_ledger(_result())
    canonical_statuses = {row.status for row in canonical_ledger.unresolved_rows()}

    assert {"active", "deferred", "missing", "unsupported"}.issubset(canonical_statuses)

    high_k_ledger = build_status_ledger(_result(HIGH_K_CDE))
    unresolved = high_k_ledger.unresolved_rows()
    assert any(
        row.component == "safety_gate"
        and row.status == "blocked"
        and row.related_entity_ids.get("option_ids") == ["discharge_add_mra"]
        and "potassium=5.7 meets >=5.5" in row.reason
        for row in unresolved
    )
    assert any(
        row.component == "decision_profile"
        and row.identifier == "discharge_add_mra"
        and row.status == "blocked"
        for row in unresolved
    )


def test_status_ledger_preserves_source_traceability_and_serializes() -> None:
    ledger = build_status_ledger(_result())

    sglt2_prior = next(
        row
        for row in ledger.rows
        if row.component == "prior_resolution" and row.identifier == "sglt2_ed_discharge"
    )
    assert sglt2_prior.source == "domain_pack:hf_ed_discharge_v0_3.prior_policy.sglt2_ed_discharge"
    assert sglt2_prior.provenance_references == [sglt2_prior.source]
    assert sglt2_prior.related_entity_ids == {"prior_ids": ["sglt2_ed_discharge"]}

    safety_row = next(
        row
        for row in ledger.rows
        if row.component == "safety_gate" and row.identifier == "sglt2_blocks:discharge_add_sglt2"
    )
    assert (
        "domain_pack:hf_ed_discharge_v0_3.mappings.safety_gate_targets.sglt2_blocks"
        in safety_row.provenance_references
    )

    serialized = json.loads(ledger.model_dump_json())
    assert serialized["rows"][0]["component"] == "decision_option"
    assert any(row["component"] == "decision_profiler" for row in serialized["rows"])


def test_status_ledger_row_rejects_unknown_components() -> None:
    with pytest.raises(ValidationError):
        StatusLedgerRow(
            component="free_text_clinical_reasoning",
            identifier="unsupported",
            status="unsupported",
            reason="status ledger rows must use explicit component names",
        )
