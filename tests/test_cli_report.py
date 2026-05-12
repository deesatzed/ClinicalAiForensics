from __future__ import annotations

import json
from pathlib import Path

from pdde.run_cde import main


ROOT = Path(__file__).resolve().parents[1]
V03_CDE = ROOT / "pdde_v0_3_first_principles_final/examples/hf_cde_stable.json"
V03_DOMAIN = (
    ROOT / "pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml"
)


def test_report_command_prints_markdown_to_stdout(capsys) -> None:
    assert (
        main(
            [
                "report",
                "--cde",
                str(V03_CDE),
                "--domain",
                str(V03_DOMAIN),
                "--iterations",
                "5",
                "--seed",
                "17",
            ]
        )
        == 0
    )
    captured = capsys.readouterr()

    assert captured.err == ""
    assert captured.out.startswith("# PDDE Decision Profile Report\n")
    assert "## Safety Gate Results" in captured.out
    assert "## Missing Unsupported Deferred And Blocked Items" in captured.out
    assert "unsupported" in captured.out
    assert "deferred" in captured.out


def test_report_command_writes_markdown_to_output_file(tmp_path: Path, capsys) -> None:
    output_path = tmp_path / "hf_report.md"

    assert (
        main(
            [
                "report",
                "--cde",
                str(V03_CDE),
                "--domain",
                str(V03_DOMAIN),
                "--output",
                str(output_path),
                "--iterations",
                "5",
                "--seed",
                "17",
            ]
        )
        == 0
    )
    captured = capsys.readouterr()

    assert f"Report written: {output_path}" in captured.out
    assert captured.err == ""
    assert output_path.exists()
    report = output_path.read_text(encoding="utf-8")
    assert "# PDDE Decision Profile Report" in report
    assert "## Prior Provenance" in report


def test_report_command_writes_provenance_log_with_output_file(tmp_path: Path, capsys) -> None:
    output_path = tmp_path / "hf_report.md"
    log_path = tmp_path / "hf_report.jsonl"

    assert (
        main(
            [
                "report",
                "--cde",
                str(V03_CDE),
                "--domain",
                str(V03_DOMAIN),
                "--output",
                str(output_path),
                "--log",
                str(log_path),
                "--iterations",
                "5",
                "--seed",
                "17",
            ]
        )
        == 0
    )
    captured = capsys.readouterr()

    assert f"Report written: {output_path}" in captured.out
    assert f"Log written: {log_path}" in captured.err
    assert output_path.exists()
    assert log_path.exists()

    records = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    assert records[0]["log_type"] == "run_metadata"
    assert records[0]["payload"]["command_name"] == "report"
    assert records[0]["payload"]["report_path"] == str(output_path)
    assert any(record["log_type"] == "prior_resolution" for record in records)
    assert any(record["log_type"] == "decision_profile" for record in records)


def test_run_cde_alias_writes_markdown_to_out_file(tmp_path: Path, capsys) -> None:
    output_path = tmp_path / "run_cde_report.md"

    assert (
        main(
            [
                "run-cde",
                "--cde",
                str(V03_CDE),
                "--domain",
                str(V03_DOMAIN),
                "--out",
                str(output_path),
                "--iterations",
                "5",
                "--seed",
                "17",
            ]
        )
        == 0
    )
    captured = capsys.readouterr()

    assert f"Report written: {output_path}" in captured.out
    assert captured.err == ""
    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8").startswith("# PDDE Decision Profile Report\n")


def test_legacy_run_cde_module_arguments_write_report(tmp_path: Path, capsys) -> None:
    output_path = tmp_path / "legacy_run_cde_report.md"

    assert (
        main(
            [
                "--cde",
                str(V03_CDE),
                "--domain",
                str(V03_DOMAIN),
                "--out",
                str(output_path),
                "--iterations",
                "5",
                "--seed",
                "17",
            ]
        )
        == 0
    )
    captured = capsys.readouterr()

    assert f"Report written: {output_path}" in captured.out
    assert captured.err == ""
    assert output_path.exists()
    assert "## Safety Gate Results" in output_path.read_text(encoding="utf-8")


def test_report_command_does_not_invent_final_recommendations(capsys) -> None:
    assert (
        main(
            [
                "report",
                "--cde",
                str(V03_CDE),
                "--domain",
                str(V03_DOMAIN),
                "--iterations",
                "5",
            ]
        )
        == 0
    )
    report = capsys.readouterr().out.lower()

    for forbidden in [
        "top-ranked",
        "highest-fitness",
        "defensible conclusion",
        "we recommend",
        "ranked decision options",
        "category probabilities",
        "median fitness",
    ]:
        assert forbidden not in report
    assert "no final clinical recommendation" in report


def test_report_command_returns_nonzero_for_missing_cde(tmp_path: Path, capsys) -> None:
    missing_cde = tmp_path / "missing.json"

    assert main(["report", "--cde", str(missing_cde), "--domain", str(V03_DOMAIN)]) == 1
    captured = capsys.readouterr()

    assert "CDE file not found" in captured.err
    assert captured.out == ""


def test_report_command_returns_nonzero_for_malformed_cde(tmp_path: Path, capsys) -> None:
    bad_cde = tmp_path / "bad_cde.json"
    bad_cde.write_text('{"cde_id": ', encoding="utf-8")

    assert main(["report", "--cde", str(bad_cde), "--domain", str(V03_DOMAIN)]) == 1
    captured = capsys.readouterr()

    assert "Could not parse CDE JSON" in captured.err
    assert captured.out == ""


def test_report_command_rejects_invalid_iterations(capsys) -> None:
    assert (
        main(
            [
                "report",
                "--cde",
                str(V03_CDE),
                "--domain",
                str(V03_DOMAIN),
                "--iterations",
                "0",
            ]
        )
        == 1
    )
    captured = capsys.readouterr()

    assert "--iterations must be >= 1" in captured.err
