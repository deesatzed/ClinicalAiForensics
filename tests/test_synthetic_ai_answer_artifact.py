from __future__ import annotations

import json
from pathlib import Path

from pdde.ai_answer_mapping import map_ai_answer_text
from pdde.cde_loader import load_cde
from pdde.domain_pack_loader import load_domain_pack
from pdde.evaluation_pipeline import evaluate_cde
from pdde.provenance_logger import create_provenance_records, records_to_jsonl
from pdde.report_renderer import render_markdown_report


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "examples/synthetic_ai_answer.json"
CDE = ROOT / "examples/hf_cde_stable.json"
DOMAIN = ROOT / "pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml"


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_synthetic_ai_answer_artifact_is_governed_non_phi_and_non_activating() -> None:
    artifact = _artifact()

    assert artifact["artifact_kind"] == "governed_synthetic_ai_answer"
    assert artifact["synthetic_non_phi"] is True
    assert artifact["phi_pii_status"] == "synthetic/non-PHI"
    assert artifact["not_approved_for_clinical_use"] is True
    assert artifact["not_an_answer_grade"] is True
    assert artifact["not_a_final_recommendation"] is True

    governance = artifact["governance"]
    assert governance["reviewer_or_approving_body"] == "Example governance reviewer"
    assert governance["activation_status"] == "documentation-only"
    confirmations = governance["explicit_confirmations"]
    assert confirmations["does_not_perform_answer_grading"] is True
    assert confirmations["does_not_perform_llm_judgment"] is True
    assert confirmations["does_not_create_final_clinical_recommendations"] is True
    assert confirmations["does_not_activate_clinical_rules"] is True
    assert confirmations["does_not_claim_evidence_truth"] is True
    assert confirmations["does_not_store_phi"] is True

    serialized = json.dumps(artifact)
    forbidden_terms = ["Temple", "TUH", "MRN", "date of birth", "phone number"]
    assert all(term.lower() not in serialized.lower() for term in forbidden_terms)


def test_synthetic_ai_answer_artifact_defines_required_mapping_boundaries() -> None:
    artifact = _artifact()
    boundaries = artifact["mapping_boundaries"]
    boundary_types = {boundary["boundary_type"] for boundary in boundaries}

    assert {
        "mapped_risky_claim",
        "unmapped",
        "omission",
        "overstatement",
        "unsupported",
    }.issubset(boundary_types)

    mapped_claim_types = {
        boundary["claim_type"]
        for boundary in boundaries
        if boundary["boundary_type"] == "mapped_risky_claim"
    }
    assert mapped_claim_types == {
        "sotalol_as_hf_beta_blocker",
        "glp1_hf_admission_prevention",
    }
    assert all(
        "does not grade the answer" in boundary.get("non_activation_rule", "")
        or "Do not infer" in boundary.get("non_activation_rule", "")
        or "must not activate" in boundary.get("non_activation_rule", "")
        for boundary in boundaries
    )

    deferred_boundaries = {
        boundary["boundary_type"]: boundary
        for boundary in boundaries
        if boundary["boundary_type"] in {"omission", "overstatement"}
    }
    assert all(
        boundary["verification_status"] == "not_approved_for_mapping"
        for boundary in deferred_boundaries.values()
    )


def test_synthetic_ai_answer_artifact_maps_current_supported_claim_patterns_only() -> None:
    artifact = _artifact()
    cde = load_cde(CDE)
    domain = load_domain_pack(DOMAIN)

    mapping = map_ai_answer_text(
        artifact["answer"]["text"],
        cde,
        domain,
        source=artifact["artifact_id"],
    )

    assert mapping.mapped_claim_types() == artifact["expected_current_api_behavior"][
        "expected_mapped_claim_types"
    ]
    assert all(claim.status == "mapped" for claim in mapping.claims)
    assert "omission" in artifact["expected_current_api_behavior"][
        "expected_unimplemented_boundaries"
    ]
    assert "overstatement" in artifact["expected_current_api_behavior"][
        "expected_unimplemented_boundaries"
    ]


def test_synthetic_ai_answer_artifact_keeps_raw_text_out_of_outputs() -> None:
    artifact = _artifact()
    cde = load_cde(CDE)
    domain = load_domain_pack(DOMAIN)
    mapping = map_ai_answer_text(
        artifact["answer"]["text"],
        cde,
        domain,
        source=artifact["artifact_id"],
    )

    result = evaluate_cde(cde, domain, n_iterations=5, random_seed=17, ai_answer_mapping=mapping)
    report = render_markdown_report(result)
    records = create_provenance_records(
        result,
        command_name="api-test",
        timestamp="2026-05-13T00:00:00Z",
        run_id="run_synthetic_ai_answer_artifact",
    )
    jsonl = records_to_jsonl(records)

    raw_phrases = [
        "Sotalol is a reasonable HF beta blocker",
        "GLP-1 receptor agonists such as semaglutide",
        "definitely safe for discharge",
    ]
    serialized_result = result.model_dump_json()
    assert all(phrase not in serialized_result for phrase in raw_phrases)
    assert all(phrase not in report for phrase in raw_phrases)
    assert all(phrase not in jsonl for phrase in raw_phrases)
    assert "final_recommendation" not in serialized_result
    assert "answer_grade" not in serialized_result
