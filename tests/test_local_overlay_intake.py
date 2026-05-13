from __future__ import annotations

import json
from pathlib import Path

from pdde.local_overlay_intake import (
    load_local_overlay_governance_intake,
    local_overlay_items_from_governance_intake,
    validate_local_overlay_governance_intake,
)


ROOT = Path(__file__).resolve().parents[1]
INTAKE = ROOT / "LOCAL_OVERLAY_GOVERNANCE_INTAKE.md"


def test_intake_entry_is_complete_enough_for_metadata_only_validation() -> None:
    result = load_local_overlay_governance_intake(INTAKE)

    assert result.source == str(INTAKE)
    assert len(result.items) == 1
    validation = result.items[0]

    assert validation.status == "draft"
    assert validation.metadata_only_complete is True
    assert validation.activation_blocked is True
    assert validation.active is False
    assert validation.missing_fields == []

    assert validation.item is not None
    assert validation.item.overlay_id == "EXAMPLE-HF-ED-FOLLOWUP-001"
    assert validation.item.request_mode == "metadata-only"
    assert validation.item.verification_status == "draft"
    assert validation.item.non_activation_confirmed is True
    assert "local rules remain inactive" in validation.reason

    serialized = json.loads(result.model_dump_json())
    assert serialized["items"][0]["metadata_only_complete"] is True
    assert "final_recommendation" not in serialized
    assert "clinical_rule_activation" not in serialized


def test_draft_tbd_and_not_reviewed_fields_do_not_activate_rules() -> None:
    result = load_local_overlay_governance_intake(INTAKE)
    validation = result.items[0]

    assert validation.deferred_fields == [
        "reviewer_or_review_body",
        "review_cadence",
        "last_reviewed_date",
        "next_review_due_date",
        "effective_date",
    ]
    assert validation.active is False

    overlay_items = local_overlay_items_from_governance_intake(result)
    assert len(overlay_items) == 1
    overlay_item = overlay_items[0]

    assert overlay_item.overlay_id == "EXAMPLE-HF-ED-FOLLOWUP-001"
    assert overlay_item.status == "draft"
    assert overlay_item.active is False
    assert overlay_item.external_input_required is True
    assert overlay_item.owner is None
    assert overlay_item.source_reference is None
    assert overlay_item.review_cadence is None
    assert overlay_item.last_reviewed is None
    assert "deferred governance fields remain visible" in overlay_item.reason


def test_activation_seeking_intake_remains_blocked() -> None:
    markdown = INTAKE.read_text(encoding="utf-8").replace(
        "| Metadata-only or activation-seeking? | metadata-only |",
        "| Metadata-only or activation-seeking? | activation-seeking |",
    )

    result = validate_local_overlay_governance_intake(
        markdown,
        source=str(INTAKE),
    )

    validation = result.items[0]
    assert validation.status == "deferred"
    assert validation.metadata_only_complete is False
    assert validation.activation_blocked is True
    assert validation.active is False
    assert validation.item is not None
    assert validation.item.request_mode == "activation-seeking"
    assert "activation remains blocked" in validation.reason

    overlay_item = local_overlay_items_from_governance_intake(result)[0]
    assert overlay_item.status == "deferred"
    assert overlay_item.active is False


def test_missing_intake_section_fails_clearly_without_activation() -> None:
    result = validate_local_overlay_governance_intake(
        "# Local Overlay Governance Intake\n\nNo table here.\n",
        source="test_intake.md",
    )

    validation = result.items[0]
    assert validation.status == "missing"
    assert validation.metadata_only_complete is False
    assert validation.activation_blocked is True
    assert validation.active is False
    assert "section" in validation.reason
