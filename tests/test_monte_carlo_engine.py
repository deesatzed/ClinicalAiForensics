from __future__ import annotations

import json
from pathlib import Path

from pdde.cde_loader import load_cde
from pdde.domain_pack_loader import load_domain_pack
from pdde.models import ClinicalDecisionEpisode, DomainPack, Prior, PriorResolutionSet
from pdde.monte_carlo_engine import DEFAULT_ITERATIONS, simulate_resolved_priors
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


def _resolved_priors(domain: DomainPack | None = None) -> PriorResolutionSet:
    return resolve_priors(domain or _domain(), cde=_cde())


def test_simulates_explicit_numeric_priors_with_summary_and_traceability() -> None:
    result = simulate_resolved_priors(
        _resolved_priors(),
        n_iterations=1_000,
        random_seed=42,
    )
    sglt2 = result.prior_simulations[0]

    assert result.cde_id == "hf_cde_stable"
    assert result.domain_pack_id == "hf_ed_discharge_v0_3"
    assert result.n_iterations == 1_000
    assert result.random_seed == 42
    assert len(result.sampled_simulations()) == 3
    assert sglt2.status == "sampled"
    assert sglt2.prior_id == "sglt2_ed_discharge"
    assert sglt2.source == "domain_pack:hf_ed_discharge_v0_3.prior_policy.sglt2_ed_discharge"
    assert sglt2.distribution == "beta"
    assert sglt2.parameters == {"alpha": 14.0, "beta": 5.0}
    assert sglt2.provenance_class == "guideline_mapped_policy_prior"
    assert sglt2.calibration_status == "uncalibrated"
    assert sglt2.sample_count == 1_000
    assert len(sglt2.samples) == 1_000
    assert min(sglt2.samples) == sglt2.minimum
    assert max(sglt2.samples) == sglt2.maximum
    assert sglt2.p5 <= sglt2.sample_median <= sglt2.p95
    assert sglt2.interval_width == sglt2.p95 - sglt2.p5
    assert 0 <= sglt2.minimum <= sglt2.maximum <= 1


def test_fixed_seed_reproducibly_generates_identical_samples() -> None:
    prior_resolutions = _resolved_priors()

    first = simulate_resolved_priors(prior_resolutions, n_iterations=200, random_seed=7)
    second = simulate_resolved_priors(prior_resolutions, n_iterations=200, random_seed=7)

    assert first.prior_simulations[0].samples == second.prior_simulations[0].samples
    assert first.prior_simulations[1].sample_mean == second.prior_simulations[1].sample_mean


def test_default_iteration_count_samples_each_resolved_prior() -> None:
    result = simulate_resolved_priors(_resolved_priors(), random_seed=99)

    assert result.n_iterations == DEFAULT_ITERATIONS
    assert [simulation.sample_count for simulation in result.sampled_simulations()] == [
        DEFAULT_ITERATIONS,
        DEFAULT_ITERATIONS,
        DEFAULT_ITERATIONS,
    ]


def test_missing_priors_are_reported_without_sampling_or_invented_values() -> None:
    prior_resolutions = resolve_priors(_domain(), cde=_cde(), prior_ids=["not_defined"])

    result = simulate_resolved_priors(prior_resolutions, n_iterations=100, random_seed=1)
    missing = result.prior_simulations[0]

    assert missing.status == "missing"
    assert missing.sample_count == 0
    assert missing.samples == []
    assert missing.sample_mean is None
    assert missing.parameters is None
    assert "not defined" in missing.reason
    assert result.sampled_simulations() == []


def test_empty_prior_policy_does_not_create_simulated_values() -> None:
    domain = _domain().model_copy(update={"prior_policy": {}})
    prior_resolutions = resolve_priors(domain, cde=_cde(), prior_ids=["sglt2_ed_discharge"])

    result = simulate_resolved_priors(prior_resolutions, n_iterations=100, random_seed=1)
    missing = result.prior_simulations[0]

    assert missing.status == "missing"
    assert missing.samples == []
    assert missing.sample_median is None
    assert result.skipped_simulations()[0].prior_id == "sglt2_ed_discharge"


def test_unsupported_prior_resolution_is_reported_without_sampling() -> None:
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
    prior_resolutions = resolve_priors(domain, cde=_cde())

    result = simulate_resolved_priors(prior_resolutions, n_iterations=100, random_seed=1)
    unsupported = result.prior_simulations[0]

    assert unsupported.status == "unsupported"
    assert unsupported.prior_id == "trial_prior"
    assert unsupported.samples == []
    assert "unsupported provenance_class" in unsupported.reason


def test_malformed_prior_resolution_is_reported_without_sampling() -> None:
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
    prior_resolutions = resolve_priors(domain, cde=_cde())

    result = simulate_resolved_priors(prior_resolutions, n_iterations=100, random_seed=1)
    bad_prior = result.prior_simulations[0]

    assert bad_prior.status == "unsupported"
    assert bad_prior.samples == []
    assert "failed validation" in bad_prior.reason
    assert "distribution" in bad_prior.reason


def test_blocked_llm_prior_is_reported_without_sampling() -> None:
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
    prior_resolutions = resolve_priors(domain, cde=_cde())

    result = simulate_resolved_priors(prior_resolutions, n_iterations=100, random_seed=1)
    llm_prior = result.prior_simulations[0]

    assert llm_prior.status == "blocked"
    assert llm_prior.samples == []
    assert llm_prior.sample_count == 0
    assert "not allowed in Phase 0 direct simulation" in llm_prior.reason


def test_simulation_result_serializes() -> None:
    result = simulate_resolved_priors(
        _resolved_priors(),
        n_iterations=10,
        random_seed=11,
    )

    serialized = json.loads(result.model_dump_json())

    assert serialized["n_iterations"] == 10
    assert serialized["prior_simulations"][0]["status"] == "sampled"
    assert len(serialized["prior_simulations"][0]["samples"]) == 10
