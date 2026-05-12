from __future__ import annotations

from pathlib import Path

import pytest

from pdde.evaluation_pipeline import run_evaluation_pipeline
from pdde.report_contract import (
    FORBIDDEN_FINAL_RECOMMENDATION_PHRASES,
    REPORT_SECTIONS,
    REQUIRED_GUARDRAIL_PHRASES,
    STATUS_PRESERVATION_OBLIGATIONS,
    ReportContractError,
    validate_report_contract,
)
from pdde.report_renderer import render_markdown_report


ROOT = Path(__file__).resolve().parents[1]
V03_CDE = ROOT / "pdde_v0_3_first_principles_final/examples/hf_cde_stable.json"
V03_DOMAIN = (
    ROOT / "pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml"
)
HIGH_K_CDE = ROOT / "examples/hf_cde_high_k.json"


def _report(cde_path: Path = V03_CDE) -> str:
    result = run_evaluation_pipeline(
        cde_path=cde_path,
        domain_pack_path=V03_DOMAIN,
        n_iterations=5,
        random_seed=17,
    )
    return render_markdown_report(result)


def test_report_contract_defines_required_sections_once() -> None:
    section_ids = [section.section_id for section in REPORT_SECTIONS]
    headings = [section.heading for section in REPORT_SECTIONS]

    assert len(section_ids) == len(set(section_ids))
    assert len(headings) == len(set(headings))
    assert headings[0] == "## Advisory Status"
    assert headings[-1] == "## Limitations"
    assert all(section.obligation for section in REPORT_SECTIONS)


def test_rendered_report_satisfies_contract() -> None:
    report = _report()

    validate_report_contract(report)

    lower_report = report.lower()
    for phrase in REQUIRED_GUARDRAIL_PHRASES:
        assert phrase in lower_report
    for phrase in FORBIDDEN_FINAL_RECOMMENDATION_PHRASES:
        assert phrase not in lower_report


def test_contract_fails_clearly_when_required_section_is_dropped() -> None:
    report = _report().replace("## Limitations", "## Dropped Limitations", 1)

    with pytest.raises(ReportContractError, match="missing required section: ## Limitations"):
        validate_report_contract(report)


def test_contract_fails_clearly_when_guardrail_language_is_dropped() -> None:
    report = _report().replace("not a final clinical recommendation", "not a clinical note", 1)

    with pytest.raises(ReportContractError, match="missing required guardrail phrase"):
        validate_report_contract(report)


def test_status_preservation_obligations_remain_visible_across_reports() -> None:
    reports = "\n".join([_report(), _report(HIGH_K_CDE)]).lower()

    for status in STATUS_PRESERVATION_OBLIGATIONS:
        assert status in reports
