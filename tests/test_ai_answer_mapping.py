from __future__ import annotations

import json
from pathlib import Path

import pytest

from pdde.ai_answer_mapping import map_ai_answer_text
from pdde.cde_loader import load_cde
from pdde.domain_pack_loader import load_domain_pack
from pdde.evaluation_pipeline import evaluate_cde
from pdde.provenance_logger import create_provenance_records, records_to_jsonl
from pdde.report_renderer import render_markdown_report
from pdde.status_ledger import build_status_ledger


ROOT = Path(__file__).resolve().parents[1]
V03_CDE = ROOT / "pdde_v0_3_first_principles_final/examples/hf_cde_stable.json"
V03_DOMAIN = (
    ROOT / "pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml"
)
SOTALOL_ANSWER = ROOT / "pdde-build-package/examples/adversarial_sotalol.txt"
GLP1_ANSWER = ROOT / "pdde-build-package/examples/adversarial_glp1.txt"
TIMESTAMP = "2026-05-12T00:00:00Z"


def _cde():
    return load_cde(V03_CDE)


def _domain():
    return load_domain_pack(V03_DOMAIN)


def test_maps_sotalol_as_hf_beta_blocker_example_to_structured_claim() -> None:
    mapping = map_ai_answer_text(SOTALOL_ANSWER.read_text(encoding="utf-8"), _cde(), _domain())

    assert mapping.mapped_claim_types() == ["sotalol_as_hf_beta_blocker"]
    claim = mapping.claims[0]
    assert claim.status == "mapped"
    assert claim.claim_type == "sotalol_as_hf_beta_blocker"
    assert claim.source.endswith(".patterns.sotalol_as_hf_beta_blocker")
    assert "hf_ed_discharge_v0.yaml.prohibited_recommendations.sotalol_as_hf_bb" in claim.reason

    serialized = mapping.model_dump_json()
    assert "Sotalol is also a reasonable HF beta blocker" not in serialized
    assert "Class III antiarrhythmic effects" not in serialized


def test_maps_glp1_hf_admission_prevention_example_to_structured_claim() -> None:
    mapping = map_ai_answer_text(GLP1_ANSWER.read_text(encoding="utf-8"), _cde(), _domain())

    assert mapping.mapped_claim_types() == ["glp1_hf_admission_prevention"]
    claim = mapping.claims[0]
    assert claim.status == "mapped"
    assert claim.claim_type == "glp1_hf_admission_prevention"
    assert "hf_ed_discharge_v0.yaml.prohibited_recommendations.glp1_hf_admission_prevention" in claim.reason

    serialized = mapping.model_dump_json()
    assert "should be considered for HF admission prevention" not in serialized
    assert "modern HF discharge ensemble" not in serialized


def test_mapped_claims_activate_claim_type_wrong_indication_gates_only_as_structured_input() -> None:
    cde = _cde()
    domain = _domain()
    mapping = map_ai_answer_text(SOTALOL_ANSWER.read_text(encoding="utf-8"), cde, domain)

    result = evaluate_cde(cde, domain, n_iterations=5, random_seed=17, ai_answer_mapping=mapping)

    claim_gate = next(
        gate
        for gate in result.safety_gates.evaluations
        if gate.claim_type == "sotalol_as_hf_beta_blocker"
    )
    other_claim_gate = next(
        gate
        for gate in result.safety_gates.evaluations
        if gate.claim_type == "glp1_hf_admission_prevention"
    )

    assert claim_gate.status == "blocked"
    assert claim_gate.option_id is None
    assert claim_gate.mapping_source == mapping.claims[0].source
    assert "structured claim metadata only" in claim_gate.evidence
    assert other_claim_gate.status == "unsupported"
    assert "final_recommendation" not in json.loads(result.model_dump_json())
    assert "answer_grade" not in json.loads(result.model_dump_json())


def test_unmapped_ai_answer_stays_visible_and_does_not_activate_claim_gate() -> None:
    cde = _cde()
    domain = _domain()
    mapping = map_ai_answer_text("Sotalol may be continued for atrial fibrillation.", cde, domain)

    result = evaluate_cde(cde, domain, n_iterations=5, random_seed=17, ai_answer_mapping=mapping)
    ledger = build_status_ledger(result)

    assert mapping.claims[0].status == "unmapped"
    assert result.ai_answer_mapping.claims[0].status == "unmapped"
    assert all(
        gate.status == "unsupported"
        for gate in result.safety_gates.evaluations
        if gate.gate_group == "wrong_indication_blocks"
    )
    assert any(
        row.component == "ai_answer_mapping"
        and row.identifier == "ai_claim_unmapped_001"
        and row.status == "unmapped"
        for row in ledger.rows
    )


def test_mapping_id_mismatch_fails_clearly() -> None:
    cde = _cde()
    domain = _domain()
    mapping = map_ai_answer_text(SOTALOL_ANSWER.read_text(encoding="utf-8"), cde, domain)
    mismatched_mapping = mapping.model_copy(update={"cde_id": "other_case"})

    with pytest.raises(ValueError, match="AI-answer mapping cde_id does not match"):
        evaluate_cde(cde, domain, n_iterations=5, random_seed=17, ai_answer_mapping=mismatched_mapping)


def test_unsupported_claim_type_mapping_remains_visible() -> None:
    cde = _cde()
    domain = _domain()
    hard_gates = {key: value for key, value in domain.hard_gates.items() if key != "wrong_indication_blocks"}
    domain_without_claim_gates = domain.model_copy(update={"hard_gates": hard_gates})

    mapping = map_ai_answer_text(
        SOTALOL_ANSWER.read_text(encoding="utf-8"),
        cde,
        domain_without_claim_gates,
    )

    assert mapping.claims[0].status == "unsupported"
    assert mapping.claims[0].claim_type is None
    assert "has no claim_type gate" in mapping.claims[0].reason


def test_report_and_provenance_include_mapping_status_without_raw_answer_text() -> None:
    cde = _cde()
    domain = _domain()
    answer_text = SOTALOL_ANSWER.read_text(encoding="utf-8")
    mapping = map_ai_answer_text(answer_text, cde, domain, source="adversarial_sotalol_fixture")
    result = evaluate_cde(cde, domain, n_iterations=5, random_seed=17, ai_answer_mapping=mapping)

    report = render_markdown_report(result)
    records = create_provenance_records(
        result,
        command_name="api-test",
        timestamp=TIMESTAMP,
        run_id="run_ai_mapping",
    )
    jsonl = records_to_jsonl(records)

    assert "AI-answer mapping inputs are structured deterministic claim metadata only" in report
    assert "ai_claim_sotalol_as_hf_beta_blocker" in report
    assert "| wrong_indication_blocks | sotalol_as_hf_beta_blocker | n/a | n/a | blocked |" in report
    assert "reasonable HF beta blocker" not in report
    assert "Class III antiarrhythmic effects" not in report

    mapping_record = next(record for record in records if record["log_type"] == "ai_answer_mapping")
    assert mapping_record["payload"]["status"] == "mapped"
    assert mapping_record["payload"]["claim_type"] == "sotalol_as_hf_beta_blocker"
    assert "reasonable HF beta blocker" not in jsonl
    assert "Class III antiarrhythmic effects" not in jsonl
