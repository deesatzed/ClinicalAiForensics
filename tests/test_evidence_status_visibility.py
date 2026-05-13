from __future__ import annotations

import json
from pathlib import Path

import yaml

from pdde.cde_loader import load_cde
from pdde.evaluation_pipeline import evaluate_cde, run_evaluation_pipeline
from pdde.evidence_models import EvidenceRegistry, EvidenceSource, EvidenceSupportLink
from pdde.input_models import DomainPack
from pdde.provenance_logger import create_provenance_records, records_to_jsonl
from pdde.report_renderer import render_markdown_report
from pdde.status_ledger import build_status_ledger


ROOT = Path(__file__).resolve().parents[1]
V03_CDE = ROOT / "pdde_v0_3_first_principles_final/examples/hf_cde_stable.json"
V03_DOMAIN = (
    ROOT / "pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml"
)


def _domain_pack_with_evidence_reference() -> DomainPack:
    payload = yaml.safe_load(V03_DOMAIN.read_text(encoding="utf-8"))
    payload["evidence_references"] = [
        {
            "supported_entity_type": "prior",
            "supported_entity_id": "sglt2_ed_discharge",
            "evidence_source_ids": ["evsrc_conflicting_guideline"],
        }
    ]
    return DomainPack.model_validate(payload)


def _registry() -> EvidenceRegistry:
    return EvidenceRegistry(
        sources=[
            EvidenceSource(
                evidence_source_id="evsrc_conflicting_guideline",
                source_type="guideline",
                title_or_label="raw evidence title should stay out of reports and logs",
                review_status="reviewed",
                evidence_owner="evidence_review_team",
                last_reviewed="2026-05-13",
            )
        ],
        support_links=[
            EvidenceSupportLink(
                evidence_source_id="evsrc_conflicting_guideline",
                supported_entity_type="prior",
                supported_entity_id="sglt2_ed_discharge",
                support_status="conflicting",
                audit_decision_by="evidence_review_team",
                audit_decision_at="2026-05-13",
            )
        ],
    )


def _result_with_registry():
    return evaluate_cde(
        load_cde(V03_CDE),
        _domain_pack_with_evidence_reference(),
        n_iterations=5,
        random_seed=17,
        cde_source=str(V03_CDE),
        domain_pack_source=str(V03_DOMAIN),
        evidence_registry=_registry(),
    )


def test_evidence_link_validation_status_appears_in_typed_pipeline_output() -> None:
    result = _result_with_registry()

    assert result.evidence_links.domain_pack_id == "hf_ed_discharge_v0_3"
    assert len(result.evidence_links.items) == 1

    item = result.evidence_links.items[0]
    assert item.status == "linked"
    assert item.support_status == "conflicting"
    assert item.evidence_source_id == "evsrc_conflicting_guideline"
    assert item.supported_entity_type == "prior"
    assert item.supported_entity_id == "sglt2_ed_discharge"

    serialized = json.loads(result.model_dump_json())
    assert serialized["evidence_links"]["items"][0]["status"] == "linked"
    assert serialized["evidence_links"]["items"][0]["support_status"] == "conflicting"
    assert "final_recommendation" not in serialized
    assert "citation_score" not in serialized
    assert "source_truth_score" not in serialized


def test_evidence_status_is_projected_to_ledger_report_and_provenance_without_raw_text() -> None:
    result = _result_with_registry()
    ledger = build_status_ledger(result)

    row = next(row for row in ledger.rows if row.component == "evidence_link")
    assert row.status == "conflicting"
    assert row.is_unresolved()
    assert row.related_entity_ids == {
        "prior_ids": ["sglt2_ed_discharge"],
        "evidence_source_ids": ["evsrc_conflicting_guideline"],
    }

    report = render_markdown_report(result)
    assert "## Evidence Reference Status" in report
    assert "| prior | sglt2_ed_discharge | evsrc_conflicting_guideline | linked | conflicting |" in report
    assert "do not validate source truth" in report
    assert "raw evidence title should stay out of reports and logs" not in report

    records = create_provenance_records(
        result,
        command_name="report",
        timestamp="2026-05-13T00:00:00Z",
        run_id="run_evidence_visibility",
    )
    evidence_record = next(
        record for record in records if record["log_type"] == "evidence_link_validation"
    )
    assert evidence_record["payload"] == {
        "supported_entity_type": "prior",
        "supported_entity_id": "sglt2_ed_discharge",
        "evidence_source_id": "evsrc_conflicting_guideline",
        "link_status": "linked",
        "support_status": "conflicting",
        "source": (
            "domain_pack:hf_ed_discharge_v0_3.evidence_references."
            "prior.sglt2_ed_discharge"
        ),
        "evidence_source_present": True,
        "support_link_present": True,
        "provenance_references": [
            "domain_pack:hf_ed_discharge_v0_3.evidence_references.prior.sglt2_ed_discharge",
            "evidence_source:evsrc_conflicting_guideline",
        ],
    }

    jsonl = records_to_jsonl(records)
    assert "raw evidence title should stay out of reports and logs" not in jsonl
    assert "source_passage" not in jsonl
    assert "claim_excerpt" not in jsonl
    assert "source_truth_score" not in jsonl
    assert "citation_score" not in jsonl


def test_missing_evidence_references_stay_visible_as_deferred() -> None:
    result = run_evaluation_pipeline(
        cde_path=V03_CDE,
        domain_pack_path=V03_DOMAIN,
        n_iterations=5,
        random_seed=17,
    )

    assert result.domain_pack.evidence_references == []
    assert result.evidence_links.items[0].status == "deferred"

    report = render_markdown_report(result)
    assert "| domain_pack | hf_ed_discharge_v0_3 | none | deferred | n/a |" in report
    assert "no source support is implied" in report

    records = create_provenance_records(
        result,
        command_name="report",
        timestamp="2026-05-13T00:00:00Z",
        run_id="run_evidence_deferred",
    )
    evidence_record = next(
        record for record in records if record["log_type"] == "evidence_link_validation"
    )
    assert evidence_record["payload"]["link_status"] == "deferred"
    assert evidence_record["payload"]["evidence_source_present"] is False
    assert evidence_record["payload"]["support_link_present"] is False
