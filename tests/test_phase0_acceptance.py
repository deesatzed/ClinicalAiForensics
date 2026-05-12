from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest

from pdde.cde_loader import load_cde
from pdde.domain_pack_loader import load_domain_pack
from pdde.evaluation_pipeline import run_evaluation_pipeline
from pdde.provenance_logger import create_provenance_records, records_to_jsonl
from pdde.report_renderer import render_markdown_report


ROOT = Path(__file__).resolve().parents[1]
V03_CDE = ROOT / "pdde_v0_3_first_principles_final/examples/hf_cde_stable.json"
V03_DOMAIN = (
    ROOT / "pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml"
)
EXAMPLES = ROOT / "examples"
TIMESTAMP = "2026-05-11T00:00:00Z"

EXPECTED_REPORT_SECTIONS = [
    "## Advisory Status",
    "## Decision Episode Summary",
    "## Safety Gate Results",
    "## Decision Profile Statuses",
    "## Why There Is No Top Option",
    "## Missing Variables And Value Of Information",
    "## Uncertainty Budget",
    "## Local Execution Checklist",
    "## Patient Feasibility And Preference Gaps",
    "## Prior Provenance",
    "## Monte Carlo Prior Summaries",
    "## Missing Unsupported Deferred And Blocked Items",
    "## Calibration Status",
    "## Provenance References",
    "## Limitations",
]

FORBIDDEN_FINAL_RECOMMENDATION_TEXT = [
    "top-ranked",
    "highest-fitness",
    "defensible conclusion",
    "we recommend",
    "ranked decision options",
    "category probabilities",
    "median fitness",
]

RAW_FIXTURE_TEXT_THAT_SHOULD_NOT_BE_LOGGED = [
    "Known HFrEF/HFmrEF",
    "wants discharge if safe",
    "sbp=118",
    "potassium=4.5",
    '"patient_state":',
    '"case_text":',
]


def _run_pdde(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    for key in [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "OPENROUTER_API_KEY",
    ]:
        env.pop(key, None)
    return subprocess.run(
        [sys.executable, "-m", "pdde", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )


def _parse_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _assert_phase0_report_guardrails(report: str) -> None:
    assert report.startswith("# PDDE Decision Profile Report\n")
    assert "advisory-only" in report.lower()
    assert "not clinically validated" in report.lower()
    assert "not a final clinical recommendation" in report.lower()
    assert "unsupported" in report
    assert "deferred" in report
    for heading in EXPECTED_REPORT_SECTIONS:
        assert heading in report
    lower_report = report.lower()
    for forbidden in FORBIDDEN_FINAL_RECOMMENDATION_TEXT:
        assert forbidden not in lower_report


def _assert_phase0_log_guardrails(records: list[dict[str, object]], raw_text: str) -> None:
    assert records
    assert records[0]["log_type"] == "run_metadata"
    assert any(record["log_type"] == "component_status_summary" for record in records)
    assert any(record["log_type"] == "safety_gate_result" for record in records)
    assert any(record["log_type"] == "prior_resolution" for record in records)
    assert any(record["log_type"] == "monte_carlo_prior" for record in records)
    assert any(record["log_type"] == "uncertainty_budget_item" for record in records)
    assert any(record["log_type"] == "value_of_information_item" for record in records)
    assert any(record["log_type"] == "decision_profile" for record in records)
    for forbidden in RAW_FIXTURE_TEXT_THAT_SHOULD_NOT_BE_LOGGED:
        assert forbidden not in raw_text


def test_phase0_cli_acceptance_help_validate_report_output_and_log(tmp_path: Path) -> None:
    help_result = _run_pdde("--help")
    assert help_result.returncode == 0
    assert "PDDE Phase 0 Clinical Decision Episode simulator" in help_result.stdout
    assert "validate" in help_result.stdout
    assert "report" in help_result.stdout
    assert "run-cde" in help_result.stdout

    validate_result = _run_pdde("validate", "--cde", str(V03_CDE), "--domain", str(V03_DOMAIN))
    assert validate_result.returncode == 0
    assert "CDE valid:" in validate_result.stdout
    assert "Domain pack valid:" in validate_result.stdout
    assert validate_result.stderr == ""

    stdout_report = _run_pdde(
        "report",
        "--cde",
        str(V03_CDE),
        "--domain",
        str(V03_DOMAIN),
        "--iterations",
        "5",
        "--seed",
        "17",
    )
    assert stdout_report.returncode == 0
    assert stdout_report.stderr == ""
    _assert_phase0_report_guardrails(stdout_report.stdout)

    report_path = tmp_path / "phase0_report.md"
    log_path = tmp_path / "phase0_run.jsonl"
    file_report = _run_pdde(
        "report",
        "--cde",
        str(V03_CDE),
        "--domain",
        str(V03_DOMAIN),
        "--output",
        str(report_path),
        "--log",
        str(log_path),
        "--iterations",
        "5",
        "--seed",
        "17",
    )
    assert file_report.returncode == 0
    assert f"Report written: {report_path}" in file_report.stdout
    assert f"Log written: {log_path}" in file_report.stderr
    assert report_path.exists()
    assert log_path.exists()

    _assert_phase0_report_guardrails(report_path.read_text(encoding="utf-8"))
    log_text = log_path.read_text(encoding="utf-8")
    records = _parse_jsonl(log_path)
    _assert_phase0_log_guardrails(records, log_text)
    assert records[0]["payload"]["command_name"] == "report"
    assert records[0]["payload"]["report_path"] == str(report_path)


def test_phase0_python_api_acceptance_without_network_or_credentials(monkeypatch) -> None:
    def blocked_socket(*_args: object, **_kwargs: object) -> socket.socket:
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "socket", blocked_socket)
    for key in [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "OPENROUTER_API_KEY",
    ]:
        monkeypatch.delenv(key, raising=False)

    cde = load_cde(V03_CDE)
    domain_pack = load_domain_pack(V03_DOMAIN)
    assert cde.cde_id == "hf_cde_stable"
    assert domain_pack.domain_pack_id == "hf_ed_discharge_v0_3"

    result = run_evaluation_pipeline(
        cde_path=V03_CDE,
        domain_pack_path=V03_DOMAIN,
        n_iterations=5,
        random_seed=17,
    )
    report = render_markdown_report(result)
    _assert_phase0_report_guardrails(report)

    records = create_provenance_records(
        result,
        command_name="api_acceptance",
        report_path="reports/phase0_acceptance.md",
        timestamp=TIMESTAMP,
        run_id="run_phase0_acceptance",
    )
    jsonl = records_to_jsonl(records)
    parsed = [json.loads(line) for line in jsonl.splitlines()]

    assert parsed == records
    _assert_phase0_log_guardrails(records, jsonl)
    assert create_provenance_records(
        result,
        command_name="api_acceptance",
        report_path="reports/phase0_acceptance.md",
        timestamp=TIMESTAMP,
        run_id="run_phase0_acceptance",
    ) == records


@pytest.mark.parametrize(
    ("name", "fixture_path", "expected_report_text"),
    [
        (
            "stable",
            EXAMPLES / "hf_cde_stable.json",
            [
                "No option ranking or final recommendation is computed",
                "claim_type gate 'sotalol_as_hf_beta_blocker' requires mapped claim types",
                "monitoring/rescue category is explicit",
            ],
        ),
        (
            "low_egfr",
            EXAMPLES / "hf_cde_low_egfr.json",
            ["egfr=15 meets <20", "egfr=15 meets <30", "blocked"],
        ),
        (
            "high_potassium",
            EXAMPLES / "hf_cde_high_k.json",
            ["potassium=5.7 meets >=5.5", "blocked"],
        ),
        ("low_sbp", EXAMPLES / "hf_cde_low_sbp.json", ["hypotension", "sbp=86 meets <90", "triggered"]),
        (
            "no_followup",
            EXAMPLES / "hf_cde_no_followup.json",
            ["no follow-up for required monitoring", "follow_up_available=False meets false"],
        ),
        (
            "prior_dka",
            EXAMPLES / "hf_cde_prior_dka.json",
            [
                "ketoacidosis risk",
                "prior_euglycemic_dka",
                "active_ketosis_or_prior_euglycemic_dka_high_risk",
            ],
        ),
        (
            "missing_labs",
            EXAMPLES / "hf_cde_missing_labs.json",
            [
                "patient_state.egfr is absent",
                "patient_state.potassium is absent",
                "Provide CDE patient_state.egfr.",
                "Provide CDE patient_state.potassium.",
                "oxygen_requirement is missing",
                "missing",
            ],
        ),
    ],
)
def test_phase0_variant_acceptance_preserves_statuses_in_reports(
    name: str,
    fixture_path: Path,
    expected_report_text: list[str],
) -> None:
    result = run_evaluation_pipeline(
        cde_path=fixture_path,
        domain_pack_path=V03_DOMAIN,
        n_iterations=5,
        random_seed=17,
    )
    report = render_markdown_report(result)

    assert result.cde.cde_id == fixture_path.stem
    assert result.cde.local_context["fixture_kind"] == "synthetic_non_phi"
    assert result.cde.local_context["synthetic"] is True
    assert result.cde.local_context["phi_status"] == "no_phi"
    assert (
        result.cde.local_context["derived_from"]
        == "pdde_v0_3_first_principles_final/examples/hf_cde_stable.json"
    )
    assert result.domain_pack.domain_pack_id == "hf_ed_discharge_v0_3"
    _assert_phase0_report_guardrails(report)
    for expected in expected_report_text:
        assert expected in report, name


@pytest.mark.parametrize(
    "fixture_path",
    [
        EXAMPLES / "hf_cde_stable.json",
        EXAMPLES / "hf_cde_low_egfr.json",
        EXAMPLES / "hf_cde_high_k.json",
        EXAMPLES / "hf_cde_low_sbp.json",
        EXAMPLES / "hf_cde_no_followup.json",
        EXAMPLES / "hf_cde_prior_dka.json",
        EXAMPLES / "hf_cde_missing_labs.json",
    ],
)
def test_phase1_example_fixtures_validate_through_cli(fixture_path: Path) -> None:
    loaded = load_cde(fixture_path)
    assert loaded.local_context["fixture_kind"] == "synthetic_non_phi"
    assert loaded.local_context["phi_status"] == "no_phi"

    validate_result = _run_pdde("validate", "--cde", str(fixture_path), "--domain", str(V03_DOMAIN))

    assert validate_result.returncode == 0
    assert f"CDE valid: {fixture_path}" in validate_result.stdout
    assert "Domain pack valid:" in validate_result.stdout
    assert validate_result.stderr == ""
