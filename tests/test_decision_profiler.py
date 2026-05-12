from __future__ import annotations

import json
from pathlib import Path

from pdde.cde_loader import load_cde
from pdde.decision_profiler import assemble_decision_profiles
from pdde.domain_pack_loader import load_domain_pack
from pdde.models import ClinicalDecisionEpisode, DecisionProfileEvaluation, DomainPack
from pdde.monte_carlo_engine import simulate_resolved_priors
from pdde.prior_resolver import resolve_priors
from pdde.safety_gate_engine import evaluate_safety_gates
from pdde.uncertainty_budget import evaluate_uncertainty_budget
from pdde.value_of_information import evaluate_value_of_information


ROOT = Path(__file__).resolve().parents[1]
V03_CDE = ROOT / "pdde_v0_3_first_principles_final/examples/hf_cde_stable.json"
V03_DOMAIN = (
    ROOT / "pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml"
)


def _cde(**patient_state_updates: object) -> ClinicalDecisionEpisode:
    cde = load_cde(V03_CDE)
    patient_state = dict(cde.patient_state)
    patient_state.update(patient_state_updates)
    return cde.model_copy(update={"patient_state": patient_state})


def _cde_without(*variables: str) -> ClinicalDecisionEpisode:
    cde = load_cde(V03_CDE)
    patient_state = dict(cde.patient_state)
    for variable in variables:
        patient_state.pop(variable, None)
    return cde.model_copy(update={"patient_state": patient_state})


def _domain() -> DomainPack:
    return load_domain_pack(V03_DOMAIN)


def _profiles(
    cde: ClinicalDecisionEpisode | None = None,
    domain: DomainPack | None = None,
):
    cde = cde or _cde()
    domain = domain or _domain()
    safety = evaluate_safety_gates(cde, domain)
    priors = resolve_priors(domain, cde=cde)
    simulation = simulate_resolved_priors(priors, n_iterations=50, random_seed=17)
    voi = evaluate_value_of_information(cde, domain, safety_gates=safety)
    budget = evaluate_uncertainty_budget(
        cde,
        domain,
        safety_gates=safety,
        prior_resolutions=priors,
        simulation=simulation,
        value_of_information=voi,
    )
    return assemble_decision_profiles(
        cde,
        domain,
        safety_gates=safety,
        prior_resolutions=priors,
        simulation=simulation,
        uncertainty_budget=budget,
        value_of_information=voi,
    )


def _profile(result, option_id: str) -> DecisionProfileEvaluation:
    return result.profiles_by_option()[option_id]


def test_stable_explicit_profile_is_eligible_with_traceability() -> None:
    result = _profiles()
    sglt2 = _profile(result, "discharge_add_sglt2")

    assert result.cde_id == "hf_cde_stable"
    assert result.domain_pack_id == "hf_ed_discharge_v0_3"
    assert sglt2.status == "eligible"
    assert sglt2.active_blockers == []
    assert any("sglt2_blocks" in gate for gate in sglt2.supporting_gates)
    assert any("sglt2_ed_discharge: resolved" in prior for prior in sglt2.supporting_priors)
    assert any("sglt2_ed_discharge: sampled" in item for item in sglt2.supporting_simulations)
    assert any("domain_pack:hf_ed_discharge_v0_3.prior_policy.sglt2_ed_discharge" in source for source in sglt2.provenance_references)
    assert "not a recommendation or ranking" in sglt2.reason


def test_profile_is_blocked_by_explicit_safety_gate() -> None:
    result = _profiles(_cde(potassium=5.7), _domain())
    mra = _profile(result, "discharge_add_mra")

    assert mra.status == "blocked"
    assert mra.active_blockers == ["mra_blocks: hyperkalemia risk; potassium=5.7 meets >=5.5"]
    assert "Blocked by explicit safety gate" in mra.reason


def test_profile_with_missing_required_gate_data_is_missing() -> None:
    result = _profiles(_cde_without("potassium"), _domain())
    mra = _profile(result, "discharge_add_mra")

    assert mra.status == "missing"
    assert mra.missing_data == [
        "mra_blocks: hyperkalemia risk; potassium is missing; condition >=5.5 was not evaluated"
    ]
    assert "Missing required safety-gate input" in mra.reason


def test_malformed_profile_definition_is_unsupported_and_visible() -> None:
    cde = _cde()
    domain = _domain().model_copy(update={"decision_options": [{"id": "", "label": "broken"}]})

    result = assemble_decision_profiles(cde, domain, safety_gates=None)

    invalid = result.profiles[0]
    unsupported_inputs = [
        item for item in result.input_summaries if item.input_type == "decision_option" and item.status == "unsupported"
    ]

    assert invalid.option_id == "<invalid:0>"
    assert invalid.status == "unsupported"
    assert "decision_options[0] failed validation" in invalid.unsupported_inputs[0]
    assert unsupported_inputs
    assert result.profiles_by_option()["discharge_add_sglt2"].status == "unsupported"
    assert "not defined in domain_pack" in result.profiles_by_option()["discharge_add_sglt2"].unsupported_inputs[0]


def test_unresolved_uncertainty_and_voi_stay_visible_in_profiles() -> None:
    result = _profiles()
    loop = _profile(result, "discharge_loop_continue_gdmt")

    assert any("harm_uncertainty: deferred" in item for item in loop.uncertainty_items)
    assert any("post_diuresis_sbp: present" in item for item in loop.value_of_information_items)
    assert any("numeric harm attribution formula" in reason for reason in loop.deferred_reasons)
    assert any(item.input_type == "uncertainty_budget" for item in result.deferred_inputs())
    assert any(item.input_type == "decision_profiler" for item in result.deferred_inputs())


def test_profiler_does_not_invent_final_recommendations_or_rankings() -> None:
    serialized = json.loads(_profiles().model_dump_json())

    for profile in serialized["profiles"]:
        assert "final_recommendation" not in profile
        assert "rank" not in profile
        assert "category" not in profile
        assert "median_fitness" not in profile
        assert "uncertainty_interval" not in profile
        assert any("did not create a final recommendation" in reason for reason in profile["deferred_reasons"])


def test_decision_profile_evaluation_result_serializes() -> None:
    serialized = json.loads(_profiles().model_dump_json())
    profile = next(
        item for item in serialized["profiles"] if item["option_id"] == "discharge_add_sglt2"
    )

    assert profile["option_id"] == "discharge_add_sglt2"
    assert profile["status"] == "eligible"
    assert serialized["input_summaries"]
