"""Deterministic prior resolution for direct CDE simulation.

This module only resolves priors that are explicitly present in a loaded domain
pack. It does not infer priors, elicit LLM estimates, run simulation, or make
clinical judgments.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from pydantic import ValidationError

from .component_models import PriorResolution, PriorResolutionSet
from .input_models import ClinicalDecisionEpisode, DomainPack, Prior
from .loader_errors import validation_summary


_NORMALIZED_PROVENANCE_CLASSES = {
    "guideline_mapped_policy_prior": "guideline_mapped_policy_prior",
    "draft_expert_policy_prior": "draft_expert_policy_prior",
    "guideline_mapped": "guideline_mapped_policy_prior",
    "panel_elicited_pending": "draft_expert_policy_prior",
}
_ALLOWED_NORMALIZED_PROVENANCE_CLASSES = {
    "guideline_mapped_policy_prior",
    "draft_expert_policy_prior",
}
_BLOCKED_PROVENANCE_CLASSES = {"llm_unverified"}
_BLOCKED_CONFIDENCE_CLASSES = {"low_unverified"}


def resolve_priors(
    domain_pack: DomainPack,
    *,
    cde: ClinicalDecisionEpisode | None = None,
    prior_ids: Iterable[str] | None = None,
) -> PriorResolutionSet:
    """Resolve requested priors from a domain pack without inventing defaults."""

    prior_policy = domain_pack.prior_policy
    requested_prior_ids = list(prior_ids) if prior_ids is not None else list(prior_policy.keys())
    resolutions = [
        _resolve_one(domain_pack=domain_pack, prior_id=prior_id, raw_prior=prior_policy.get(prior_id))
        for prior_id in requested_prior_ids
    ]
    return PriorResolutionSet(
        cde_id=cde.cde_id if cde is not None else None,
        domain_pack_id=domain_pack.domain_pack_id,
        requested_prior_ids=requested_prior_ids,
        resolutions=resolutions,
    )


def _resolve_one(domain_pack: DomainPack, prior_id: str, raw_prior: Any) -> PriorResolution:
    source = f"domain_pack:{domain_pack.domain_pack_id}.prior_policy.{prior_id}"
    if raw_prior is None:
        return PriorResolution(
            prior_id=prior_id,
            status="missing",
            reason=f"prior {prior_id!r} is not defined in domain_pack.prior_policy",
        )

    prior = raw_prior if isinstance(raw_prior, Prior) else _validate_prior(prior_id, raw_prior, source)
    if isinstance(prior, PriorResolution):
        return prior

    normalized_provenance = _NORMALIZED_PROVENANCE_CLASSES.get(prior.provenance_class)
    base_resolution = _prior_resolution_fields(
        prior_id=prior_id,
        source=source,
        prior=prior,
        normalized_provenance_class=normalized_provenance,
    )

    if prior.provenance_class in _BLOCKED_PROVENANCE_CLASSES:
        return PriorResolution(
            **base_resolution,
            status="blocked",
            reason=(
                f"prior {prior_id!r} uses provenance_class {prior.provenance_class!r}, "
                "which is not allowed in Phase 0 direct simulation"
            ),
        )

    if prior.confidence_class in _BLOCKED_CONFIDENCE_CLASSES:
        return PriorResolution(
            **base_resolution,
            status="blocked",
            reason=(
                f"prior {prior_id!r} uses confidence_class {prior.confidence_class!r}, "
                "which is not allowed for active direct simulation priors"
            ),
        )

    if normalized_provenance not in _ALLOWED_NORMALIZED_PROVENANCE_CLASSES:
        return PriorResolution(
            **base_resolution,
            status="unsupported",
            reason=(
                f"prior {prior_id!r} uses unsupported provenance_class "
                f"{prior.provenance_class!r} for Phase 0 direct simulation"
            ),
        )

    return PriorResolution(
        **base_resolution,
        status="resolved",
        reason=(
            f"prior {prior_id!r} resolved from domain_pack.prior_policy; "
            f"calibration_status={prior.calibration_status!r}"
        ),
    )


def _validate_prior(prior_id: str, raw_prior: Any, source: str) -> Prior | PriorResolution:
    try:
        return Prior.model_validate(raw_prior)
    except ValidationError as exc:
        return PriorResolution(
            prior_id=prior_id,
            status="unsupported",
            source=source,
            reason=f"prior {prior_id!r} failed validation: {validation_summary(exc)}",
        )


def _prior_resolution_fields(
    *,
    prior_id: str,
    source: str,
    prior: Prior,
    normalized_provenance_class: str | None,
) -> dict[str, object]:
    return {
        "prior_id": prior_id,
        "source": source,
        "normalized_provenance_class": normalized_provenance_class,
        "prior": prior,
        "distribution": prior.distribution,
        "parameters": {"alpha": float(prior.alpha), "beta": float(prior.beta)},
        "provenance_class": prior.provenance_class,
        "confidence_class": prior.confidence_class,
        "calibration_status": prior.calibration_status,
        "warning": prior.warning,
        "owner": prior.owner,
        "review_status": prior.review_status,
        "source_basis": prior.source_basis,
        "last_reviewed": prior.last_reviewed,
    }
