from __future__ import annotations

import json
from pathlib import Path

from pdde.cde_loader import load_cde
from pdde.domain_pack_loader import load_domain_pack
from pdde.evaluation_pipeline import evaluate_cde, run_evaluation_pipeline
from pdde.models import ClinicalDecisionEpisode


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


def test_successful_end_to_end_pipeline_run_uses_canonical_fixtures() -> None:
    result = run_evaluation_pipeline(
        cde_path=V03_CDE,
        domain_pack_path=V03_DOMAIN,
        n_iterations=40,
        random_seed=23,
    )

    assert result.workflow_mode == "direct_cde_simulation"
    assert result.cde.cde_id == "hf_cde_stable"
    assert result.domain_pack.domain_pack_id == "hf_ed_discharge_v0_3"
    assert result.n_iterations == 40
    assert result.random_seed == 23
    assert result.cde_source == str(V03_CDE)
    assert result.domain_pack_source == str(V03_DOMAIN)


def test_pipeline_preserves_component_outputs_visibly() -> None:
    result = run_evaluation_pipeline(
        cde_path=V03_CDE,
        domain_pack_path=V03_DOMAIN,
        n_iterations=25,
        random_seed=7,
    )

    assert len(result.safety_gates.evaluations) == 11
    assert [item.prior_id for item in result.prior_resolutions.resolutions] == [
        "sglt2_ed_discharge",
        "mra_ed_start",
        "loop_continue_gdmt",
    ]
    assert [item.status for item in result.simulation.prior_simulations] == [
        "sampled",
        "sampled",
        "sampled",
    ]
    assert result.value_of_information.items[0].variable == "egfr"
    assert len(result.uncertainty_budget.items) == 7
    assert set(result.decision_profiles.profiles_by_option()) == {
        "admit_or_observe",
        "discharge_loop_continue_gdmt",
        "discharge_add_sglt2",
        "discharge_add_mra",
        "discharge_urgent_followup_no_new_dmt",
    }


def test_blocked_missing_and_deferred_statuses_remain_visible() -> None:
    domain = load_domain_pack(V03_DOMAIN)
    high_k = evaluate_cde(_cde(potassium=5.7), domain, n_iterations=10, random_seed=1)
    missing_k = evaluate_cde(_cde_without("potassium"), domain, n_iterations=10, random_seed=1)

    high_k_profiles = high_k.decision_profiles.profiles_by_option()
    missing_k_profiles = missing_k.decision_profiles.profiles_by_option()

    assert high_k_profiles["discharge_add_mra"].status == "blocked"
    assert high_k.safety_gates.hard_stops_by_option()["discharge_add_mra"] == [
        "hyperkalemia risk: potassium=5.7 meets >=5.5"
    ]
    assert missing_k_profiles["discharge_add_mra"].status == "missing"
    assert any(item.variable == "potassium" and item.status == "missing" for item in missing_k.value_of_information.items)
    assert any(item.status == "deferred" for item in high_k.uncertainty_budget.items)
    assert high_k.decision_profiles.deferred_inputs()


def test_pipeline_does_not_invent_final_recommendations() -> None:
    serialized = json.loads(
        run_evaluation_pipeline(
            cde_path=V03_CDE,
            domain_pack_path=V03_DOMAIN,
            n_iterations=10,
            random_seed=4,
        ).model_dump_json()
    )

    assert "final_recommendation" not in serialized
    assert "ranked_options" not in serialized
    for profile in serialized["decision_profiles"]["profiles"]:
        assert "final_recommendation" not in profile
        assert "rank" not in profile
        assert "category" not in profile
        assert "median_fitness" not in profile
        assert "uncertainty_interval" not in profile


def test_pipeline_result_serializes_with_all_major_components() -> None:
    result = run_evaluation_pipeline(
        cde_path=V03_CDE,
        domain_pack_path=V03_DOMAIN,
        n_iterations=5,
        random_seed=5,
    )

    serialized = json.loads(result.model_dump_json())

    assert serialized["safety_gates"]["evaluations"]
    assert serialized["prior_resolutions"]["resolutions"]
    assert serialized["simulation"]["prior_simulations"][0]["sample_count"] == 5
    assert serialized["value_of_information"]["items"]
    assert serialized["uncertainty_budget"]["items"]
    assert serialized["decision_profiles"]["profiles"]
