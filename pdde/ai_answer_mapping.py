"""Deterministic AI-answer claim mapping boundary.

This module provides a typed interface for answer-derived claims. It does not
call an LLM, score answers, change priors, or create clinical recommendations.
Only explicit source-backed claim patterns are mapped into structured claim
types that existing deterministic gates can consume.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

from .component_models import AIAnswerMappedClaim, AIAnswerMappingResult
from .input_models import ClinicalDecisionEpisode, DomainPack


_SOTALOL_PATTERN_SOURCE = "hf_ed_discharge_v0.yaml.prohibited_recommendations.sotalol_as_hf_bb"
_GLP1_PATTERN_SOURCE = "hf_ed_discharge_v0.yaml.prohibited_recommendations.glp1_hf_admission_prevention"


def empty_ai_answer_mapping(
    cde: ClinicalDecisionEpisode,
    domain_pack: DomainPack,
    *,
    source: str = "not_provided",
) -> AIAnswerMappingResult:
    """Return an empty mapping result for direct CDE runs without AI-answer input."""

    return AIAnswerMappingResult(
        cde_id=cde.cde_id,
        domain_pack_id=domain_pack.domain_pack_id,
        source=f"ai_answer_mapping:{source}",
        claims=[],
    )


def map_ai_answer_text(
    answer_text: str,
    cde: ClinicalDecisionEpisode,
    domain_pack: DomainPack,
    *,
    source: str = "provided_text",
) -> AIAnswerMappingResult:
    """Map supported AI-answer text patterns into typed deterministic claims.

    The returned model intentionally omits the raw answer text. Callers must pass
    the structured result into the evaluation pipeline explicitly; free text is
    never evaluated by safety gates directly.
    """

    supported_claim_types = _domain_claim_types(domain_pack)
    claims: list[AIAnswerMappedClaim] = []
    normalized = _normalize(answer_text)

    if _matches_sotalol_wrong_indication(normalized):
        claims.append(
            _claim_from_pattern(
                claim_id="ai_claim_sotalol_as_hf_beta_blocker",
                claim_type="sotalol_as_hf_beta_blocker",
                supported_claim_types=supported_claim_types,
                source=f"ai_answer_mapping:{source}.patterns.sotalol_as_hf_beta_blocker",
                pattern_source=_SOTALOL_PATTERN_SOURCE,
                matched_terms=["sotalol", "HF/HFrEF/HFmrEF", "beta blocker/GDMT/pillar"],
            )
        )

    if _matches_glp1_hf_prevention(normalized):
        claims.append(
            _claim_from_pattern(
                claim_id="ai_claim_glp1_hf_admission_prevention",
                claim_type="glp1_hf_admission_prevention",
                supported_claim_types=supported_claim_types,
                source=f"ai_answer_mapping:{source}.patterns.glp1_hf_admission_prevention",
                pattern_source=_GLP1_PATTERN_SOURCE,
                matched_terms=[
                    "GLP-1/liraglutide/semaglutide/tirzepatide",
                    "HFrEF/HFmrEF",
                    "admission/prevention",
                ],
            )
        )

    if not claims:
        reason = (
            "AI answer text was empty; no deterministic claim input was produced"
            if not normalized
            else "no explicit supported AI-answer claim pattern matched; no deterministic claim input was produced"
        )
        claims.append(
            AIAnswerMappedClaim(
                claim_id="ai_claim_unmapped_001",
                status="unmapped",
                reason=reason,
                source=f"ai_answer_mapping:{source}",
            )
        )

    return AIAnswerMappingResult(
        cde_id=cde.cde_id,
        domain_pack_id=domain_pack.domain_pack_id,
        source=f"ai_answer_mapping:{source}",
        claims=claims,
    )


def _claim_from_pattern(
    *,
    claim_id: str,
    claim_type: str,
    supported_claim_types: set[str],
    source: str,
    pattern_source: str,
    matched_terms: list[str],
) -> AIAnswerMappedClaim:
    if claim_type not in supported_claim_types:
        return AIAnswerMappedClaim(
            claim_id=claim_id,
            status="unsupported",
            reason=(
                f"explicit source pattern {pattern_source} matched, but domain pack has no "
                f"claim_type gate for {claim_type!r}"
            ),
            source=source,
            matched_terms=matched_terms,
        )
    return AIAnswerMappedClaim(
        claim_id=claim_id,
        status="mapped",
        claim_type=claim_type,
        reason=(
            f"explicit source pattern {pattern_source} matched; structured claim_type "
            "is available for deterministic gate evaluation"
        ),
        source=source,
        matched_terms=matched_terms,
    )


def _domain_claim_types(domain_pack: DomainPack) -> set[str]:
    return {
        gate.claim_type
        for gates in domain_pack.hard_gates.values()
        for gate in gates
        if gate.claim_type is not None
    }


def _matches_sotalol_wrong_indication(text: str) -> bool:
    return (
        _contains_any(text, ["sotalol"])
        and _contains_any(text, ["hf", "hfr ef", "hfref", "hfmr ef", "hfmref"])
        and _contains_any(text, ["beta blocker", "gdmt", "pillar"])
    )


def _matches_glp1_hf_prevention(text: str) -> bool:
    return (
        _contains_any(text, ["liraglutide", "semaglutide", "tirzepatide", "glp 1"])
        and _contains_any(text, ["hfr ef", "hfref", "hfmr ef", "hfmref"])
        and _contains_any(text, ["admission", "readmission", "prevent", "protective"])
    )


def _contains_any(text: str, needles: Iterable[str]) -> bool:
    return any(_contains_term(text, needle) for needle in needles)


def _contains_term(text: str, needle: str) -> bool:
    return re.search(rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])", text) is not None


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
