"""Local overlay verification contract evaluation.

This module records local operational-overlay verification metadata only. It
does not apply local workflow rules, change safety gates, or create clinical
recommendations.
"""

from __future__ import annotations

from typing import Any, cast

from .component_models import (
    LocalOverlayRequiredField,
    LocalOverlayVerificationItem,
    LocalOverlayVerificationSet,
    LocalOverlayVerificationStatus,
)
from .input_models import ClinicalDecisionEpisode, DomainPack


REQUIRED_LOCAL_OVERLAY_FIELDS: tuple[LocalOverlayRequiredField, ...] = (
    "owner",
    "status",
    "source",
    "review_cadence",
    "last_reviewed",
)

_SUPPORTED_RAW_STATUSES = {"verified", "draft", "deferred"}


def evaluate_local_overlay(
    cde: ClinicalDecisionEpisode,
    domain_pack: DomainPack,
) -> LocalOverlayVerificationSet:
    """Evaluate explicit local overlay verification metadata from CDE local_context."""

    items = _items_from_local_context(cde)
    return LocalOverlayVerificationSet(
        cde_id=cde.cde_id,
        domain_pack_id=domain_pack.domain_pack_id,
        items=items,
    )


def _items_from_local_context(cde: ClinicalDecisionEpisode) -> list[LocalOverlayVerificationItem]:
    local_context = cde.local_context
    rules_payload = local_context.get("local_overlay_rules")
    if rules_payload is None:
        return [
            _item_from_rule(
                overlay_id="local_overlay",
                raw_rule={
                    "status": local_context.get("overlay_status"),
                    "owner": local_context.get("overlay_owner"),
                    "source": local_context.get("overlay_source"),
                    "review_cadence": local_context.get("overlay_review_cadence"),
                    "last_reviewed": local_context.get("overlay_last_reviewed"),
                },
                source=(
                    f"cde:{cde.cde_id}.local_context.overlay_status"
                    if "overlay_status" in local_context
                    else f"cde:{cde.cde_id}.local_context"
                ),
            )
        ]

    source = f"cde:{cde.cde_id}.local_context.local_overlay_rules"
    if not isinstance(rules_payload, list):
        return [
            LocalOverlayVerificationItem(
                overlay_id="local_overlay_rules",
                status="unsupported",
                reason="local_overlay_rules must be a list of explicit verification objects",
                source=source,
                missing_fields=list(REQUIRED_LOCAL_OVERLAY_FIELDS),
                external_input_required=True,
            )
        ]

    if not rules_payload:
        return [
            LocalOverlayVerificationItem(
                overlay_id="local_overlay_rules",
                status="deferred",
                reason="no local overlay rules were provided for verification",
                source=source,
                missing_fields=list(REQUIRED_LOCAL_OVERLAY_FIELDS),
                external_input_required=True,
            )
        ]

    items: list[LocalOverlayVerificationItem] = []
    for index, raw_rule in enumerate(rules_payload):
        rule_source = f"{source}[{index}]"
        if not isinstance(raw_rule, dict):
            items.append(
                LocalOverlayVerificationItem(
                    overlay_id=f"local_overlay_rule_{index + 1}",
                    status="unsupported",
                    reason="local overlay rule must be an object with explicit verification metadata",
                    source=rule_source,
                    missing_fields=list(REQUIRED_LOCAL_OVERLAY_FIELDS),
                    external_input_required=True,
                )
            )
            continue

        overlay_id = _string_or_none(raw_rule.get("id")) or f"local_overlay_rule_{index + 1}"
        items.append(_item_from_rule(overlay_id=overlay_id, raw_rule=raw_rule, source=rule_source))
    return items


def _item_from_rule(
    *,
    overlay_id: str,
    raw_rule: dict[str, Any],
    source: str,
) -> LocalOverlayVerificationItem:
    status_value = _string_or_none(raw_rule.get("status"))
    owner = _string_or_none(raw_rule.get("owner"))
    source_reference = _string_or_none(raw_rule.get("source"))
    review_cadence = _string_or_none(raw_rule.get("review_cadence"))
    last_reviewed = _string_or_none(raw_rule.get("last_reviewed"))
    missing_fields = _missing_fields(
        status=status_value,
        owner=owner,
        source_reference=source_reference,
        review_cadence=review_cadence,
        last_reviewed=last_reviewed,
    )

    if status_value is None:
        return LocalOverlayVerificationItem(
            overlay_id=overlay_id,
            status="missing",
            reason=(
                "local overlay status is missing; owner, source, review cadence, "
                "and last-reviewed metadata are required before local rules can be verified"
            ),
            source=source,
            owner=owner,
            source_reference=source_reference,
            review_cadence=review_cadence,
            last_reviewed=last_reviewed,
            missing_fields=missing_fields,
            external_input_required=True,
        )

    normalized_status = status_value.lower()
    if normalized_status not in _SUPPORTED_RAW_STATUSES:
        return LocalOverlayVerificationItem(
            overlay_id=overlay_id,
            status="unsupported",
            reason=f"unsupported local overlay status {status_value!r}; expected verified, draft, or deferred",
            source=source,
            owner=owner,
            source_reference=source_reference,
            review_cadence=review_cadence,
            last_reviewed=last_reviewed,
            missing_fields=missing_fields,
            external_input_required=True,
        )

    if normalized_status == "verified" and missing_fields:
        return LocalOverlayVerificationItem(
            overlay_id=overlay_id,
            status="deferred",
            reason=(
                "local overlay was marked verified but required verification metadata is incomplete; "
                "local rules remain inactive until owner, source, review cadence, and last-reviewed are supplied"
            ),
            source=source,
            owner=owner,
            source_reference=source_reference,
            review_cadence=review_cadence,
            last_reviewed=last_reviewed,
            missing_fields=missing_fields,
            external_input_required=True,
        )

    status = cast(LocalOverlayVerificationStatus, normalized_status)
    return LocalOverlayVerificationItem(
        overlay_id=overlay_id,
        status=status,
        reason=_reason_for_status(status, missing_fields),
        source=source,
        owner=owner,
        source_reference=source_reference,
        review_cadence=review_cadence,
        last_reviewed=last_reviewed,
        missing_fields=missing_fields,
        external_input_required=status != "verified" or bool(missing_fields),
        active=False,
    )


def _missing_fields(
    *,
    status: str | None,
    owner: str | None,
    source_reference: str | None,
    review_cadence: str | None,
    last_reviewed: str | None,
) -> list[LocalOverlayRequiredField]:
    missing: list[LocalOverlayRequiredField] = []
    if status is None:
        missing.append("status")
    if owner is None:
        missing.append("owner")
    if source_reference is None:
        missing.append("source")
    if review_cadence is None:
        missing.append("review_cadence")
    if last_reviewed is None:
        missing.append("last_reviewed")
    return missing


def _reason_for_status(
    status: LocalOverlayVerificationStatus,
    missing_fields: list[LocalOverlayRequiredField],
) -> str:
    if status == "verified":
        return (
            "local overlay verification metadata is complete; this records metadata only "
            "and does not activate clinical rules"
        )
    if status == "draft":
        if missing_fields:
            return "local overlay is draft and verification metadata is incomplete; local rules remain inactive"
        return "local overlay is draft; metadata presence is recorded but local rules remain inactive"
    if status == "deferred":
        return "local overlay verification is deferred pending external local workflow owner input"
    return "local overlay verification is incomplete"


def _string_or_none(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None
