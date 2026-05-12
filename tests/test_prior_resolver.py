from __future__ import annotations

import json
from pathlib import Path

from pdde.cde_loader import load_cde
from pdde.domain_pack_loader import load_domain_pack
from pdde.models import ClinicalDecisionEpisode, DomainPack, Prior, PriorResolution
from pdde.prior_resolver import resolve_priors


ROOT = Path(__file__).resolve().parents[1]
V03_CDE = ROOT / "pdde_v0_3_first_principles_final/examples/hf_cde_stable.json"
V03_DOMAIN = (
    ROOT / "pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml"
)


def _cde() -> ClinicalDecisionEpisode:
    return load_cde(V03_CDE)


def _domain() -> DomainPack:
    return load_domain_pack(V03_DOMAIN)


def _only(resolutions: list[PriorResolution], prior_id: str) -> PriorResolution:
    for resolution in resolutions:
        if resolution.prior_id == prior_id:
            return resolution
    raise AssertionError(f"prior resolution not found for {prior_id!r}")


def test_resolves_canonical_domain_pack_priors_with_traceability() -> None:
    result = resolve_priors(_domain(), cde=_cde())

    sglt2 = _only(result.resolutions, "sglt2_ed_discharge")

    assert result.cde_id == "hf_cde_stable"
    assert result.domain_pack_id == "hf_ed_discharge_v0_3"
    assert [resolution.status for resolution in result.resolutions] == [
        "resolved",
        "resolved",
        "resolved",
    ]
    assert sglt2.source == "domain_pack:hf_ed_discharge_v0_3.prior_policy.sglt2_ed_discharge"
    assert sglt2.distribution == "beta"
    assert sglt2.parameters == {"alpha": 14.0, "beta": 5.0}
    assert sglt2.provenance_class == "guideline_mapped_policy_prior"
    assert sglt2.normalized_provenance_class == "guideline_mapped_policy_prior"
    assert sglt2.calibration_status == "uncalibrated"
    assert sglt2.warning == "Not direct ED-discharge anti-admission proof; conditional/extrapolated."
    assert result.active_priors()["sglt2_ed_discharge"].beta == 5
    assert json.loads(result.model_dump_json())["resolutions"][0]["parameters"] == {
        "alpha": 14.0,
        "beta": 5.0,
    }


def test_missing_requested_prior_is_missing_not_invented() -> None:
    result = resolve_priors(_domain(), prior_ids=["not_defined"])
    missing = result.resolutions[0]

    assert missing.status == "missing"
    assert missing.prior is None
    assert missing.parameters is None
    assert missing.source is None
    assert "not defined" in missing.reason
    assert result.active_priors() == {}


def test_empty_prior_policy_does_not_invent_requested_prior() -> None:
    domain = _domain().model_copy(update={"prior_policy": {}})

    result = resolve_priors(domain, prior_ids=["sglt2_ed_discharge"])
    missing = result.resolutions[0]

    assert missing.status == "missing"
    assert missing.prior is None
    assert missing.parameters is None
    assert result.active_resolutions() == []


def test_malformed_prior_definition_is_unsupported() -> None:
    malformed_prior = {
        "distribution": "normal",
        "alpha": 1,
        "beta": 1,
        "provenance_class": "guideline_mapped_policy_prior",
        "elicitation_method": "bad fixture",
        "confidence_class": "high",
        "calibration_status": "uncalibrated",
    }
    domain = _domain().model_copy(update={"prior_policy": {"bad_prior": malformed_prior}})

    result = resolve_priors(domain)
    bad_prior = result.resolutions[0]

    assert bad_prior.status == "unsupported"
    assert bad_prior.source == "domain_pack:hf_ed_discharge_v0_3.prior_policy.bad_prior"
    assert "failed validation" in bad_prior.reason
    assert "distribution" in bad_prior.reason
    assert result.active_priors() == {}


def test_unsupported_provenance_class_is_not_resolved() -> None:
    prior = Prior(
        distribution="beta",
        alpha=16,
        beta=4,
        provenance_class="trial_parsed",
        elicitation_method="trial extraction not admitted for Phase 0 direct simulation",
        confidence_class="high",
        calibration_status="uncalibrated",
    )
    domain = _domain().model_copy(update={"prior_policy": {"trial_prior": prior}})

    result = resolve_priors(domain)
    trial_prior = result.resolutions[0]

    assert trial_prior.status == "unsupported"
    assert trial_prior.prior == prior
    assert "unsupported provenance_class" in trial_prior.reason
    assert result.active_priors() == {}


def test_llm_unverified_prior_is_blocked() -> None:
    prior = Prior(
        distribution="beta",
        alpha=1,
        beta=1,
        provenance_class="llm_unverified",
        elicitation_method="LLM fallback",
        confidence_class="low_unverified",
        calibration_status="uncalibrated",
        warning="LLM-only prior; not formally elicited.",
    )
    domain = _domain().model_copy(update={"prior_policy": {"llm_prior": prior}})

    result = resolve_priors(domain)
    llm_prior = result.resolutions[0]

    assert llm_prior.status == "blocked"
    assert llm_prior.source == "domain_pack:hf_ed_discharge_v0_3.prior_policy.llm_prior"
    assert "not allowed in Phase 0 direct simulation" in llm_prior.reason
    assert result.active_priors() == {}


def test_compatible_v01_provenance_labels_are_normalized() -> None:
    guideline_prior = Prior(
        distribution="beta",
        alpha=16,
        beta=3,
        provenance_class="guideline_mapped",
        elicitation_method="v0.1 guideline mapping",
        confidence_class="high",
        calibration_status="uncalibrated",
    )
    panel_prior = Prior(
        distribution="beta",
        alpha=11,
        beta=6,
        provenance_class="panel_elicited_pending",
        elicitation_method="v0.1 panel elicitation pending",
        confidence_class="moderate_unverified",
        calibration_status="uncalibrated",
        warning="PLACEHOLDER - requires formal panel elicitation.",
    )
    domain = _domain().model_copy(
        update={"prior_policy": {"guideline_prior": guideline_prior, "panel_prior": panel_prior}}
    )

    result = resolve_priors(domain)
    guideline = _only(result.resolutions, "guideline_prior")
    panel = _only(result.resolutions, "panel_prior")

    assert guideline.status == "resolved"
    assert guideline.normalized_provenance_class == "guideline_mapped_policy_prior"
    assert panel.status == "resolved"
    assert panel.normalized_provenance_class == "draft_expert_policy_prior"
    assert panel.warning == "PLACEHOLDER - requires formal panel elicitation."
