from __future__ import annotations

import re
from pathlib import Path

from pdde.cde_loader import load_cde
from pdde.domain_pack_loader import load_domain_pack
from pdde.evaluation_pipeline import evaluate_cde, run_evaluation_pipeline
from pdde.models import ClinicalDecisionEpisode
from pdde.report_contract import REQUIRED_REPORT_HEADINGS
from pdde.report_renderer import render_markdown_report


ROOT = Path(__file__).resolve().parents[1]
V03_CDE = ROOT / "pdde_v0_3_first_principles_final/examples/hf_cde_stable.json"
V03_DOMAIN = (
    ROOT / "pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml"
)


def _canonical_report() -> str:
    result = run_evaluation_pipeline(
        cde_path=V03_CDE,
        domain_pack_path=V03_DOMAIN,
        n_iterations=20,
        random_seed=11,
    )
    return render_markdown_report(result)


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


def test_renders_valid_pipeline_result_to_markdown() -> None:
    report = _canonical_report()

    assert report.startswith("# PDDE Decision Profile Report\n")
    assert "**Case ID:** hf_cde_stable" in report
    assert "**Domain:** hf_ed_discharge" in report
    assert "**Workflow:** direct_cde_simulation" in report
    assert "Advisory-only decision-profile report" in report
    assert "not a final clinical recommendation" in report
    assert "uncalibrated" in report


def test_major_report_sections_are_present() -> None:
    report = _canonical_report()

    for heading in REQUIRED_REPORT_HEADINGS:
        assert heading in report


def test_report_sections_follow_registry_order() -> None:
    report = _canonical_report()

    rendered_headings = re.findall(r"^## .+$", report, flags=re.MULTILINE)

    assert rendered_headings == list(REQUIRED_REPORT_HEADINGS)


def test_blocked_missing_deferred_and_unsupported_statuses_are_visible() -> None:
    domain = load_domain_pack(V03_DOMAIN)

    high_k = evaluate_cde(_cde(potassium=5.7), domain, n_iterations=10, random_seed=1)
    high_k_report = render_markdown_report(high_k)
    assert "blocked" in high_k_report
    assert "hyperkalemia risk" in high_k_report
    assert "potassium=5.7 meets >=5.5" in high_k_report

    missing_k = evaluate_cde(_cde_without("potassium"), domain, n_iterations=10, random_seed=1)
    missing_k_report = render_markdown_report(missing_k)
    assert "missing" in missing_k_report
    assert "patient_state.potassium is absent" in missing_k_report
    assert "Provide CDE patient_state.potassium." in missing_k_report

    canonical_report = _canonical_report()
    assert "unsupported" in canonical_report
    assert "claim_type gate 'sotalol_as_hf_beta_blocker' requires mapped claim types" in canonical_report
    assert "deferred" in canonical_report
    assert "monitoring/rescue category is explicit" in canonical_report
    assert "| safety_gate | wrong_indication_blocks:sotalol_as_hf_beta_blocker | unsupported |" in canonical_report
    assert "| decision_profiler | decision_fitness_formula | deferred |" in canonical_report


def test_provenance_and_source_references_are_preserved() -> None:
    report = _canonical_report()

    assert str(V03_CDE) in report
    assert str(V03_DOMAIN) in report
    assert "domain_pack:hf_ed_discharge_v0_3.prior_policy.sglt2_ed_discharge" in report
    assert "domain_pack:hf_ed_discharge_v0_3.mappings.prior_to_options.sglt2_ed_discharge" in report
    assert "domain_pack:hf_ed_discharge_v0_3.mappings.safety_gate_targets.sglt2_blocks" in report
    assert "domain_pack:hf_ed_discharge_v0_3.value_of_information_variables" in report
    assert "pdde_v0_3_first_principles_final/05_PRIOR_AND_UNCERTAINTY_GOVERNANCE.md#Uncertainty Budget" in report
    assert "pdde_v0_3_first_principles_final/schemas/decision_profile.schema.json" in report


def test_report_does_not_invent_final_conclusions_or_rankings() -> None:
    report = _canonical_report().lower()

    for forbidden in [
        "top-ranked",
        "highest-fitness",
        "defensible conclusion",
        "we recommend",
        "ranked decision options",
        "category probabilities",
        "median fitness",
        "| rank | option |",
    ]:
        assert forbidden not in report

    assert "no option ranking" in report
    assert "no final clinical recommendation" in report
