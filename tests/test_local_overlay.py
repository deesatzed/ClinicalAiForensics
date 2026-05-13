from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from pdde.cde_loader import load_cde
from pdde.domain_pack_loader import load_domain_pack
from pdde.local_overlay import evaluate_local_overlay
from pdde.models import ClinicalDecisionEpisode, LocalOverlayVerificationItem


ROOT = Path(__file__).resolve().parents[1]
V03_CDE = ROOT / "pdde_v0_3_first_principles_final/examples/hf_cde_stable.json"
V03_DOMAIN = (
    ROOT / "pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml"
)


def _domain():
    return load_domain_pack(V03_DOMAIN)


def _cde_with_local_context(local_context: dict[str, object]) -> ClinicalDecisionEpisode:
    return load_cde(V03_CDE).model_copy(update={"local_context": local_context})


def test_canonical_draft_overlay_remains_inactive_and_deferred_for_owner_input() -> None:
    result = evaluate_local_overlay(load_cde(V03_CDE), _domain())

    assert result.cde_id == "hf_cde_stable"
    assert result.domain_pack_id == "hf_ed_discharge_v0_3"
    assert len(result.items) == 1

    item = result.items[0]
    assert item.overlay_id == "local_overlay"
    assert item.status == "draft"
    assert item.active is False
    assert item.external_input_required is True
    assert item.missing_fields == ["owner", "source", "review_cadence", "last_reviewed"]
    assert item.source == "cde:hf_cde_stable.local_context.overlay_status"
    assert "local rules remain inactive" in item.reason


def test_verified_overlay_with_missing_metadata_is_deferred_not_activated() -> None:
    cde = _cde_with_local_context(
        {
            "overlay_status": "verified",
            "overlay_owner": "cardiology",
        }
    )

    result = evaluate_local_overlay(cde, _domain())

    item = result.items[0]
    assert item.status == "deferred"
    assert item.active is False
    assert item.owner == "cardiology"
    assert item.missing_fields == ["source", "review_cadence", "last_reviewed"]
    assert "required verification metadata is incomplete" in item.reason


def test_explicit_verified_overlay_rule_preserves_source_traceability_and_serializes() -> None:
    cde = _cde_with_local_context(
        {
            "local_overlay_rules": [
                {
                    "id": "hf_clinic_followup",
                    "status": "verified",
                    "owner": "cardiology_owner",
                    "source": "local_policy_hf_ed_2026",
                    "review_cadence": "annual",
                    "last_reviewed": "2026-05-01",
                    "draft_value": "intentionally ignored by evaluator",
                }
            ]
        }
    )

    result = evaluate_local_overlay(cde, _domain())
    item = result.items[0]

    assert item.overlay_id == "hf_clinic_followup"
    assert item.status == "verified"
    assert item.active is False
    assert item.missing_fields == []
    assert item.source == "cde:hf_cde_stable.local_context.local_overlay_rules[0]"
    assert item.source_reference == "local_policy_hf_ed_2026"
    assert "does not activate clinical rules" in item.reason

    serialized = json.loads(result.model_dump_json())
    assert serialized["items"][0]["overlay_id"] == "hf_clinic_followup"
    assert serialized["items"][0]["status"] == "verified"


def test_missing_overlay_status_stays_missing_without_fuzzy_inference() -> None:
    cde = _cde_with_local_context(
        {
            "overlay_owner": "cardiology_owner",
            "overlay_source": "local_policy_hf_ed_2026",
            "overlay_review_cadence": "annual",
            "overlay_last_reviewed": "2026-05-01",
        }
    )

    result = evaluate_local_overlay(cde, _domain())

    item = result.items[0]
    assert item.status == "missing"
    assert item.active is False
    assert item.missing_fields == ["status"]
    assert "status is missing" in item.reason


def test_malformed_or_unsupported_overlay_definitions_fail_clearly() -> None:
    malformed = evaluate_local_overlay(
        _cde_with_local_context({"local_overlay_rules": "not-a-list"}),
        _domain(),
    )
    assert malformed.items[0].status == "unsupported"
    assert malformed.items[0].missing_fields == [
        "owner",
        "status",
        "source",
        "review_cadence",
        "last_reviewed",
    ]

    unsupported = evaluate_local_overlay(
        _cde_with_local_context(
            {
                "local_overlay_rules": [
                    {
                        "id": "example_formulary",
                        "status": "approved_by_label_only",
                        "owner": "pharmacy",
                    }
                ]
            }
        ),
        _domain(),
    )
    assert unsupported.items[0].status == "unsupported"
    assert "unsupported local overlay status" in unsupported.items[0].reason


def test_verified_overlay_model_rejects_missing_required_metadata() -> None:
    with pytest.raises(ValidationError, match="verified local overlay items require"):
        LocalOverlayVerificationItem(
            overlay_id="invalid_verified_overlay",
            status="verified",
            reason="verified cannot omit review metadata",
            source="test",
            owner="cardiology",
        )
