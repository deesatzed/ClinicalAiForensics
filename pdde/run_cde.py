"""Command-line interface for Phase 0 Clinical Decision Episode simulation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from . import __version__
from .cde_loader import load_cde
from .domain_pack_loader import load_domain_pack
from .evaluation_pipeline import run_evaluation_pipeline
from .loader_errors import LoaderError
from .monte_carlo_engine import DEFAULT_ITERATIONS
from .provenance_logger import write_provenance_log
from .report_renderer import render_markdown_report


DEFAULT_DOMAIN_PATH = Path("domain_packs/hf_ed_discharge/domain_pack.yaml")
DEFAULT_REPORT_PATH = Path("reports/hf_cde_stable_report.md")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pdde",
        description="PDDE Phase 0 Clinical Decision Episode simulator.",
    )
    parser.add_argument("--version", action="version", version=f"pdde {__version__}")

    subcommands = parser.add_subparsers(dest="command")

    run_cde = subcommands.add_parser(
        "run-cde",
        help="Run a CDE simulation and write a Markdown report.",
    )
    run_cde.add_argument("--cde", type=Path, required=True, help="Clinical Decision Episode JSON.")
    run_cde.add_argument(
        "--domain",
        type=Path,
        default=DEFAULT_DOMAIN_PATH,
        help=f"Domain pack YAML. Default: {DEFAULT_DOMAIN_PATH}",
    )
    run_cde.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help=f"Markdown report output path. Default: {DEFAULT_REPORT_PATH}",
    )
    run_cde.add_argument(
        "--iterations",
        type=int,
        default=DEFAULT_ITERATIONS,
        help=f"Monte Carlo iterations for explicit resolved priors. Default: {DEFAULT_ITERATIONS}",
    )
    run_cde.add_argument("--seed", type=int, help="Deterministic Monte Carlo seed.")
    run_cde.add_argument("--log", type=Path, help="Write JSONL provenance log to this path.")
    run_cde.set_defaults(handler=_report_command)

    report = subcommands.add_parser(
        "report",
        help="Run the full evaluation pipeline and render Markdown.",
    )
    report.add_argument("--cde", type=Path, required=True, help="Clinical Decision Episode JSON.")
    report.add_argument("--domain", type=Path, required=True, help="Domain pack YAML.")
    report.add_argument(
        "--output",
        type=Path,
        help="Write Markdown report to this path. If omitted, Markdown is printed to stdout.",
    )
    report.add_argument(
        "--iterations",
        type=int,
        default=DEFAULT_ITERATIONS,
        help=f"Monte Carlo iterations for explicit resolved priors. Default: {DEFAULT_ITERATIONS}",
    )
    report.add_argument("--seed", type=int, help="Deterministic Monte Carlo seed.")
    report.add_argument("--log", type=Path, help="Write JSONL provenance log to this path.")
    report.set_defaults(handler=_report_command)

    validate = subcommands.add_parser(
        "validate",
        help="Validate a CDE or domain pack.",
    )
    validate.add_argument("--cde", type=Path, help="Clinical Decision Episode JSON.")
    validate.add_argument("--domain", type=Path, help="Domain pack YAML.")
    validate.set_defaults(handler=_validate_command)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    normalized_argv = _normalize_argv(argv)
    parser = build_parser()
    try:
        args = parser.parse_args(normalized_argv)
    except SystemExit as exc:
        return int(exc.code or 0)
    if not hasattr(args, "handler"):
        parser.print_help()
        return 0
    return int(args.handler(args))


def _normalize_argv(argv: Sequence[str] | None) -> list[str]:
    args = list(sys.argv[1:] if argv is None else argv)
    subcommands = {"run-cde", "report", "validate"}
    if args and args[0] not in subcommands and "--cde" in args:
        return ["run-cde", *args]
    return args


def _validate_command(args: argparse.Namespace) -> int:
    if args.cde is None and args.domain is None:
        print("validate requires --cde, --domain, or both.", file=sys.stderr)
        return 1

    try:
        if args.cde is not None:
            cde = load_cde(args.cde)
            print(f"CDE valid: {args.cde} ({cde.cde_id})")
        if args.domain is not None:
            domain_pack = load_domain_pack(args.domain)
            print(f"Domain pack valid: {args.domain} ({domain_pack.domain_pack_id})")
    except LoaderError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    return 0


def _report_command(args: argparse.Namespace) -> int:
    if args.iterations < 1:
        print("--iterations must be >= 1.", file=sys.stderr)
        return 1

    try:
        result = run_evaluation_pipeline(
            cde_path=args.cde,
            domain_pack_path=args.domain,
            n_iterations=args.iterations,
            random_seed=args.seed,
        )
    except LoaderError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    markdown = render_markdown_report(result)
    output_path: Path | None = getattr(args, "output", None) or getattr(args, "out", None)
    log_path: Path | None = getattr(args, "log", None)
    if output_path is None:
        if log_path is not None and not _write_log(result, args, log_path, report_path=None):
            return 1
        print(markdown, end="")
        return 0

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    except OSError as exc:
        print(f"Could not write report {output_path}: {exc}", file=sys.stderr)
        return 1

    if log_path is not None and not _write_log(result, args, log_path, report_path=output_path):
        return 1

    print(f"Report written: {output_path}")
    return 0


def _write_log(
    result,
    args: argparse.Namespace,
    log_path: Path,
    *,
    report_path: Path | None,
) -> bool:
    try:
        write_provenance_log(
            result,
            log_path,
            command_name=args.command or "run-cde",
            report_path=report_path,
        )
    except OSError as exc:
        print(f"Could not write provenance log {log_path}: {exc}", file=sys.stderr)
        return False
    print(f"Log written: {log_path}", file=sys.stderr)
    return True


if __name__ == "__main__":
    raise SystemExit(main())
