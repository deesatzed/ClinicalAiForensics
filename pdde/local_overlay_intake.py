"""Metadata-only local overlay governance intake validation.

This module parses the documentation intake table and produces typed validation
records. It does not activate local rules, alter clinical logic, or write logs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from .component_models import (
    LocalOverlayGovernanceIntakeItem,
    LocalOverlayGovernanceIntakeMode,
    LocalOverlayGovernanceIntakeStatus,
    LocalOverlayGovernanceIntakeValidation,
    LocalOverlayGovernanceIntakeValidationSet,
    LocalOverlayGovernanceValidationStatus,
    LocalOverlayVerificationItem,
)


DEFAULT_INTAKE_SECTION = "My First Local Overlay Entry"

_FIELD_MAP = {
    "local overlay/workflow item id": "overlay_id",
    "local overlay title/name": "title",
    "domain/site applicability": "domain_site_applicability",
    "accountable owner": "accountable_owner",
    "owner role": "owner_role",
    "authoritative source reference": "source_reference",
    "source type": "source_type",
    "verification status": "verification_status",
    "reviewer or review body": "reviewer_or_review_body",
    "review cadence": "review_cadence",
    "last-reviewed date": "last_reviewed_date",
    "next-review due date": "next_review_due_date",
    "version": "version",
    "effective date": "effective_date",
    "expiration date if applicable": "expiration_date",
    "change history reference": "change_history_reference",
    "metadata-only or activation-seeking?": "request_mode",
    "explicit confirmation that metadata remains non-activating": "non_activation_confirmed",
    "explicit activation criteria if future activation is ever requested": "activation_criteria",
    "safety/privacy notes": "safety_privacy_notes",
    "phi/pii handling statement": "phi_pii_handling_statement",
}

_REQUIRED_FIELDS = tuple(_FIELD_MAP.values())
_PLACEHOLDER_VALUES = {"tbd", "not yet reviewed", "not active"}
_SUPPORTED_STATUSES = {
    "draft",
    "pending_review",
    "verified_metadata_only",
    "rejected",
    "expired",
    "superseded",
}


def load_local_overlay_governance_intake(
    path: str | Path,
    *,
    section_heading: str = DEFAULT_INTAKE_SECTION,
) -> LocalOverlayGovernanceIntakeValidationSet:
    """Load and validate a local overlay governance intake Markdown file."""

    intake_path = Path(path)
    return validate_local_overlay_governance_intake(
        intake_path.read_text(encoding="utf-8"),
        source=str(intake_path),
        section_heading=section_heading,
    )


def validate_local_overlay_governance_intake(
    markdown: str,
    *,
    source: str,
    section_heading: str = DEFAULT_INTAKE_SECTION,
) -> LocalOverlayGovernanceIntakeValidationSet:
    """Validate a Markdown intake section as metadata-only local overlay governance."""

    table_values = _extract_two_column_table(markdown, section_heading=section_heading)
    if not table_values:
        return LocalOverlayGovernanceIntakeValidationSet(
            source=source,
            items=[
                LocalOverlayGovernanceIntakeValidation(
                    status="missing",
                    reason=f"local overlay governance intake section {section_heading!r} was not found",
                    source=source,
                    missing_fields=list(_REQUIRED_FIELDS),
                )
            ],
        )

    normalized_values = {
        field_name: _clean_value(table_values.get(label, ""))
        for label, field_name in _FIELD_MAP.items()
    }
    missing_fields = [
        field_name
        for field_name in _REQUIRED_FIELDS
        if not normalized_values.get(field_name)
    ]
    if missing_fields:
        return LocalOverlayGovernanceIntakeValidationSet(
            source=source,
            items=[
                LocalOverlayGovernanceIntakeValidation(
                    status="missing",
                    reason="local overlay governance intake is missing required metadata fields",
                    source=source,
                    missing_fields=missing_fields,
                )
            ],
        )

    governance_status = _normalize_status(normalized_values["verification_status"])
    request_mode = _normalize_request_mode(normalized_values["request_mode"])
    non_activation_confirmed = _is_non_activation_confirmed(
        normalized_values["non_activation_confirmed"]
    )

    unsupported_fields: list[str] = []
    if governance_status is None:
        unsupported_fields.append("verification_status")
    if request_mode is None:
        unsupported_fields.append("request_mode")
    if unsupported_fields:
        return LocalOverlayGovernanceIntakeValidationSet(
            source=source,
            items=[
                LocalOverlayGovernanceIntakeValidation(
                    status="unsupported",
                    reason="local overlay governance intake contains unsupported status or request mode",
                    source=source,
                    missing_fields=unsupported_fields,
                )
            ],
        )

    item = LocalOverlayGovernanceIntakeItem(
        overlay_id=normalized_values["overlay_id"],
        title=normalized_values["title"],
        domain_site_applicability=normalized_values["domain_site_applicability"],
        accountable_owner=normalized_values["accountable_owner"],
        owner_role=normalized_values["owner_role"],
        source_reference=normalized_values["source_reference"],
        source_type=normalized_values["source_type"],
        verification_status=governance_status,
        reviewer_or_review_body=normalized_values["reviewer_or_review_body"],
        review_cadence=normalized_values["review_cadence"],
        last_reviewed_date=normalized_values["last_reviewed_date"],
        next_review_due_date=normalized_values["next_review_due_date"],
        version=normalized_values["version"],
        effective_date=normalized_values["effective_date"],
        expiration_date=normalized_values["expiration_date"],
        change_history_reference=normalized_values["change_history_reference"],
        request_mode=request_mode,
        non_activation_confirmed=non_activation_confirmed,
        activation_criteria=normalized_values["activation_criteria"],
        safety_privacy_notes=normalized_values["safety_privacy_notes"],
        phi_pii_handling_statement=normalized_values["phi_pii_handling_statement"],
        source=f"{source}#{_slug(section_heading)}",
    )

    status = _validation_status_for(item)
    deferred_fields = _deferred_fields(normalized_values)
    metadata_only_complete = (
        not missing_fields
        and request_mode == "metadata-only"
        and non_activation_confirmed
        and governance_status is not None
    )
    return LocalOverlayGovernanceIntakeValidationSet(
        source=source,
        items=[
            LocalOverlayGovernanceIntakeValidation(
                status=status,
                reason=_reason_for(item, status=status, deferred_fields=deferred_fields),
                source=item.source,
                item=item,
                deferred_fields=deferred_fields,
                metadata_only_complete=metadata_only_complete,
                activation_blocked=True,
                active=False,
            )
        ],
    )


def local_overlay_items_from_governance_intake(
    validation_set: LocalOverlayGovernanceIntakeValidationSet,
) -> list[LocalOverlayVerificationItem]:
    """Project governance intake results into redacted non-activating overlay items."""

    items: list[LocalOverlayVerificationItem] = []
    for validation in validation_set.items:
        overlay_id = (
            validation.item.overlay_id
            if validation.item is not None
            else "local_overlay_governance_intake"
        )
        status: Literal["draft", "deferred"] = (
            "draft" if validation.status == "draft" else "deferred"
        )
        items.append(
            LocalOverlayVerificationItem(
                overlay_id=overlay_id,
                status=status,
                reason=validation.reason,
                source=validation.source,
                external_input_required=True,
                active=False,
            )
        )
    return items


def _extract_two_column_table(markdown: str, *, section_heading: str) -> dict[str, str]:
    section_lines = _section_lines(markdown, section_heading=section_heading)
    table_rows = [line for line in section_lines if line.strip().startswith("|")]
    values: dict[str, str] = {}
    for row in table_rows:
        cells = _split_table_row(row)
        if len(cells) != 2:
            continue
        key, value = cells
        normalized_key = _normalize_label(key)
        if normalized_key in {"field", "---"}:
            continue
        if set(normalized_key) == {"-"}:
            continue
        values[normalized_key] = value
    return values


def _section_lines(markdown: str, *, section_heading: str) -> list[str]:
    wanted = f"## {section_heading}".strip()
    lines = markdown.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        if line.strip() == wanted:
            start = index + 1
            break
    if start is None:
        return []

    section: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        section.append(line)
    return section


def _split_table_row(row: str) -> list[str]:
    stripped = row.strip().strip("|")
    return [cell.strip() for cell in stripped.split("|")]


def _normalize_label(value: str) -> str:
    return value.strip().lower()


def _clean_value(value: str) -> str:
    stripped = value.strip()
    if stripped.startswith("`") and stripped.endswith("`") and len(stripped) >= 2:
        stripped = stripped[1:-1].strip()
    return stripped


def _normalize_status(value: str) -> LocalOverlayGovernanceIntakeStatus | None:
    normalized = value.strip().lower()
    if normalized not in _SUPPORTED_STATUSES:
        return None
    return normalized  # type: ignore[return-value]


def _normalize_request_mode(value: str) -> LocalOverlayGovernanceIntakeMode | None:
    normalized = value.strip().lower()
    if normalized in {"metadata-only", "metadata only"}:
        return "metadata-only"
    if normalized in {"activation-seeking", "activation seeking"}:
        return "activation-seeking"
    return None


def _is_non_activation_confirmed(value: str) -> bool:
    lowered = value.strip().lower()
    return "yes" in lowered or "non-activating" in lowered or "must not activate" in lowered


def _validation_status_for(
    item: LocalOverlayGovernanceIntakeItem,
) -> LocalOverlayGovernanceValidationStatus:
    if item.request_mode == "activation-seeking":
        return "deferred"
    if not item.non_activation_confirmed:
        return "deferred"
    if item.verification_status == "draft":
        return "draft"
    return "deferred"


def _deferred_fields(values: dict[str, str]) -> list[str]:
    return [
        field_name
        for field_name, value in values.items()
        if value.strip().lower() in _PLACEHOLDER_VALUES
    ]


def _reason_for(
    item: LocalOverlayGovernanceIntakeItem,
    *,
    status: LocalOverlayGovernanceValidationStatus,
    deferred_fields: list[str],
) -> str:
    if item.request_mode == "activation-seeking":
        return (
            "local overlay governance intake requests activation; activation remains blocked "
            "until separate governance approval, tests, safety review, rollback plan, audit trail, "
            "and project-control decision are supplied"
        )
    if not item.non_activation_confirmed:
        return "local overlay governance intake lacks non-activation confirmation; local rules remain inactive"
    if status == "draft":
        if deferred_fields:
            return (
                "local overlay governance intake is draft metadata-only; deferred governance fields "
                f"remain visible ({', '.join(deferred_fields)}); local rules remain inactive"
            )
        return "local overlay governance intake is draft metadata-only; local rules remain inactive"
    return "local overlay governance intake is metadata-only; local rules remain inactive"


def _slug(value: str) -> str:
    return "-".join(value.strip().lower().split())
