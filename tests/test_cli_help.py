from __future__ import annotations

from pdde.run_cde import main


def test_cli_help_exits_successfully(capsys) -> None:
    assert main(["--help"]) == 0
    output = capsys.readouterr().out
    assert "PDDE Phase 0 Clinical Decision Episode simulator" in output
    assert "report" in output
    assert "run-cde" in output
    assert "validate" in output
