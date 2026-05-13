from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from pdde.domain_pack_loader import load_domain_pack
from pdde.evidence_linking import validate_domain_pack_evidence_links
from pdde.evidence_models import EvidenceRegistry, EvidenceSource, EvidenceSupportLink
from pdde.input_models import DomainPack, DomainPackEvidenceReference


ROOT = Path(__file__).resolve().parents[1]
V03_DOMAIN = (
    ROOT / "pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml"
)


def _domain_payload() -> dict:
    return yaml.safe_load(V03_DOMAIN.read_text(encoding="utf-8"))


def _source() -> EvidenceSource:
    return EvidenceSource(
        evidence_source_id="evsrc_hf_guideline",
        source_type="guideline",
        title_or_label="HF guideline evidence source placeholder",
    )


def _domain_pack_with_prior_reference(source_id: str = "evsrc_hf_guideline") -> DomainPack:
    payload = _domain_payload()
    payload["evidence_references"] = [
        {
            "supported_entity_type": "prior",
            "supported_entity_id": "sglt2_ed_discharge",
            "evidence_source_ids": [source_id],
        }
    ]
    return DomainPack.model_validate(payload)


def test_canonical_domain_pack_without_evidence_references_stays_backward_compatible() -> None:
    domain_pack = load_domain_pack(V03_DOMAIN)

    assert domain_pack.evidence_references == []

    result = validate_domain_pack_evidence_links(domain_pack, EvidenceRegistry())

    assert len(result.items) == 1
    assert result.items[0].status == "deferred"
    assert result.items[0].supported_entity_type == "domain_pack"
    assert "no source support is implied" in result.items[0].reason


def test_domain_pack_loads_and_serializes_explicit_evidence_references() -> None:
    domain_pack = _domain_pack_with_prior_reference()

    assert domain_pack.evidence_references == [
        DomainPackEvidenceReference(
            supported_entity_type="prior",
            supported_entity_id="sglt2_ed_discharge",
            evidence_source_ids=["evsrc_hf_guideline"],
        )
    ]

    serialized = json.loads(domain_pack.model_dump_json())
    assert serialized["evidence_references"][0]["supported_entity_id"] == "sglt2_ed_discharge"
    assert serialized["evidence_references"][0]["evidence_source_ids"] == [
        "evsrc_hf_guideline"
    ]


def test_domain_pack_rejects_unknown_or_fuzzy_evidence_reference_targets() -> None:
    payload = _domain_payload()
    payload["evidence_references"] = [
        {
            "supported_entity_type": "prior",
            "supported_entity_id": "sglt2 ed discharge",
            "evidence_source_ids": ["evsrc_hf_guideline"],
        }
    ]

    with pytest.raises(ValidationError, match="unknown supported_entity_id"):
        DomainPack.model_validate(payload)


def test_domain_pack_rejects_duplicate_evidence_references() -> None:
    with pytest.raises(ValidationError, match="cannot repeat source ids"):
        DomainPackEvidenceReference(
            supported_entity_type="prior",
            supported_entity_id="sglt2_ed_discharge",
            evidence_source_ids=["evsrc_hf_guideline", "evsrc_hf_guideline"],
        )

    payload = _domain_payload()
    payload["evidence_references"] = [
        {
            "supported_entity_type": "prior",
            "supported_entity_id": "sglt2_ed_discharge",
            "evidence_source_ids": ["evsrc_hf_guideline"],
        },
        {
            "supported_entity_type": "prior",
            "supported_entity_id": "sglt2_ed_discharge",
            "evidence_source_ids": ["evsrc_hf_guideline"],
        },
    ]

    with pytest.raises(ValidationError, match="unique per entity and source id"):
        DomainPack.model_validate(payload)


def test_explicit_evidence_reference_validates_against_registry_support_link() -> None:
    domain_pack = _domain_pack_with_prior_reference()
    registry = EvidenceRegistry(
        sources=[_source()],
        support_links=[
            EvidenceSupportLink(
                evidence_source_id="evsrc_hf_guideline",
                supported_entity_type="prior",
                supported_entity_id="sglt2_ed_discharge",
            )
        ],
    )

    result = validate_domain_pack_evidence_links(domain_pack, registry)

    assert [(item.evidence_source_id, item.status) for item in result.items] == [
        ("evsrc_hf_guideline", "linked")
    ]
    assert result.items[0].support_status == "pending_review"
    assert "no truth validation was performed" in result.items[0].reason


def test_known_source_without_registry_support_link_remains_pending() -> None:
    domain_pack = _domain_pack_with_prior_reference()
    registry = EvidenceRegistry(sources=[_source()])

    result = validate_domain_pack_evidence_links(domain_pack, registry)

    assert result.items[0].status == "pending_review"
    assert "no explicit registry support link exists" in result.items[0].reason


def test_unknown_evidence_source_fails_clearly_only_when_registry_is_supplied() -> None:
    domain_pack = _domain_pack_with_prior_reference("evsrc_missing")

    without_registry = validate_domain_pack_evidence_links(domain_pack)
    assert without_registry.items[0].status == "pending_review"
    assert "no evidence registry was supplied" in without_registry.items[0].reason

    with_registry = validate_domain_pack_evidence_links(domain_pack, EvidenceRegistry())
    assert with_registry.items[0].status == "unknown_source"
    assert "unknown evidence_source_id" in with_registry.items[0].reason
