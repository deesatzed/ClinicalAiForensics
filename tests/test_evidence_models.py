from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from pdde.evidence_models import EvidenceRegistry, EvidenceSource, EvidenceSupportLink
from pdde.models import EvidenceRegistry as FacadeEvidenceRegistry


def _reviewed_source() -> EvidenceSource:
    return EvidenceSource(
        evidence_source_id="src_hf_guideline",
        source_type="guideline",
        title_or_label="HF guideline source placeholder",
        review_status="reviewed",
        bibliographic_ids=[{"id_type": "guideline_id", "value": "HF-GUIDE-PLACEHOLDER"}],
        evidence_owner="evidence_review_team",
        last_reviewed="2026-05-12",
        review_cadence="annual",
    )


def test_evidence_registry_serializes_source_and_support_traceability() -> None:
    registry = EvidenceRegistry(
        sources=[_reviewed_source()],
        support_links=[
            EvidenceSupportLink(
                evidence_source_id="src_hf_guideline",
                supported_entity_type="prior",
                supported_entity_id="sglt2_ed_discharge",
                support_status="supported",
                support_scope={"domain": "hf_ed_discharge", "setting": "policy_prior"},
                limitations=["source support is recorded, not automatically validated"],
                audit_decision_by="evidence_review_team",
                audit_decision_at="2026-05-12",
                audit_notes_reference="EVIDENCE_AUDIT_HANDOFF.md",
            )
        ],
    )

    serialized = json.loads(registry.model_dump_json())

    assert serialized["sources"][0]["evidence_source_id"] == "src_hf_guideline"
    assert serialized["support_links"][0]["supported_entity_id"] == "sglt2_ed_discharge"
    assert serialized["support_links"][0]["support_scope"]["domain"] == "hf_ed_discharge"
    assert FacadeEvidenceRegistry is EvidenceRegistry


def test_reviewed_evidence_source_requires_review_metadata() -> None:
    with pytest.raises(ValidationError, match="evidence_owner and last_reviewed"):
        EvidenceSource(
            evidence_source_id="src_missing_review_metadata",
            source_type="guideline",
            title_or_label="Reviewed source without owner",
            review_status="reviewed",
        )


def test_final_support_status_requires_audit_metadata() -> None:
    with pytest.raises(ValidationError, match="audit_decision_by and audit_decision_at"):
        EvidenceSupportLink(
            evidence_source_id="src_hf_guideline",
            supported_entity_type="prior",
            supported_entity_id="sglt2_ed_discharge",
            support_status="supported",
        )


def test_registry_rejects_unknown_source_references_and_duplicates() -> None:
    with pytest.raises(ValidationError, match="unknown evidence_source_id"):
        EvidenceRegistry(
            sources=[_reviewed_source()],
            support_links=[
                EvidenceSupportLink(
                    evidence_source_id="not_in_registry",
                    supported_entity_type="prior",
                    supported_entity_id="sglt2_ed_discharge",
                )
            ],
        )

    with pytest.raises(ValidationError, match="source ids must be unique"):
        EvidenceRegistry(sources=[_reviewed_source(), _reviewed_source()])

    duplicate_link = EvidenceSupportLink(
        evidence_source_id="src_hf_guideline",
        supported_entity_type="prior",
        supported_entity_id="sglt2_ed_discharge",
    )
    with pytest.raises(ValidationError, match="support links must be unique"):
        EvidenceRegistry(
            sources=[_reviewed_source()],
            support_links=[duplicate_link, duplicate_link],
        )


def test_evidence_models_reject_raw_source_text_fields() -> None:
    with pytest.raises(ValidationError):
        EvidenceSource.model_validate(
            {
                "evidence_source_id": "src_with_raw_text",
                "source_type": "trial",
                "title_or_label": "Trial source placeholder",
                "review_status": "pending_review",
                "source_passage": "Do not store copied source passages in the registry.",
            }
        )

    with pytest.raises(ValidationError):
        EvidenceSupportLink.model_validate(
            {
                "evidence_source_id": "src_hf_guideline",
                "supported_entity_type": "prior",
                "supported_entity_id": "sglt2_ed_discharge",
                "claim_excerpt": "Do not store copied clinical or source text in support links.",
            }
        )
