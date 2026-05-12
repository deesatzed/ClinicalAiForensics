"""Report section and guardrail contract for Markdown rendering."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReportSection:
    """Required Markdown report section metadata."""

    section_id: str
    heading: str
    obligation: str


REPORT_TITLE = "# PDDE Decision Profile Report"

REPORT_SECTIONS: tuple[ReportSection, ...] = (
    ReportSection(
        section_id="advisory_status",
        heading="## Advisory Status",
        obligation="Display advisory-only, non-validated, non-recommendation language.",
    ),
    ReportSection(
        section_id="decision_episode_summary",
        heading="## Decision Episode Summary",
        obligation="Display case/domain identifiers and structured CDE context.",
    ),
    ReportSection(
        section_id="safety_gate_results",
        heading="## Safety Gate Results",
        obligation="Display deterministic gate statuses, including missing and unsupported gates.",
    ),
    ReportSection(
        section_id="decision_profile_statuses",
        heading="## Decision Profile Statuses",
        obligation="Display profile statuses without ranking options or making recommendations.",
    ),
    ReportSection(
        section_id="why_no_top_option",
        heading="## Why There Is No Top Option",
        obligation="Explain why no final top option or decision formula is produced.",
    ),
    ReportSection(
        section_id="missing_and_value_of_information",
        heading="## Missing Variables And Value Of Information",
        obligation="Display explicit VOI items and missing required data.",
    ),
    ReportSection(
        section_id="uncertainty_budget",
        heading="## Uncertainty Budget",
        obligation="Display uncertainty-budget item statuses and deferred requirements.",
    ),
    ReportSection(
        section_id="local_execution_checklist",
        heading="## Local Execution Checklist",
        obligation="Display local execution state without verifying draft local workflow.",
    ),
    ReportSection(
        section_id="patient_feasibility_preference_gaps",
        heading="## Patient Feasibility And Preference Gaps",
        obligation="Display patient feasibility/preference VOI fields when available.",
    ),
    ReportSection(
        section_id="prior_provenance",
        heading="## Prior Provenance",
        obligation="Display prior status, source, provenance, confidence, and calibration.",
    ),
    ReportSection(
        section_id="monte_carlo_summaries",
        heading="## Monte Carlo Prior Summaries",
        obligation="Display prior-level simulation summaries without option ranking.",
    ),
    ReportSection(
        section_id="items_requiring_attention",
        heading="## Missing Unsupported Deferred And Blocked Items",
        obligation="Display unresolved status-ledger rows so statuses do not disappear.",
    ),
    ReportSection(
        section_id="calibration_status",
        heading="## Calibration Status",
        obligation="Display calibration pending and not-clinically-validated status.",
    ),
    ReportSection(
        section_id="provenance_references",
        heading="## Provenance References",
        obligation="Display source references used by the pipeline and report.",
    ),
    ReportSection(
        section_id="limitations",
        heading="## Limitations",
        obligation="Display advisory limitations and prohibited capability claims.",
    ),
)

REQUIRED_REPORT_HEADINGS = tuple(section.heading for section in REPORT_SECTIONS)

REQUIRED_GUARDRAIL_PHRASES = (
    "advisory-only",
    "not clinically validated",
    "not a final clinical recommendation",
    "uncalibrated",
)

STATUS_PRESERVATION_OBLIGATIONS = (
    "missing",
    "unsupported",
    "blocked",
    "deferred",
)

FORBIDDEN_FINAL_RECOMMENDATION_PHRASES = (
    "top-ranked",
    "highest-fitness",
    "defensible conclusion",
    "we recommend",
    "ranked decision options",
    "category probabilities",
    "median fitness",
    "| rank | option |",
)


class ReportContractError(ValueError):
    """Raised when rendered Markdown violates the report contract."""


def validate_report_contract(markdown: str) -> None:
    """Validate required report title, section order, and guardrail language."""

    if not markdown.startswith(f"{REPORT_TITLE}\n"):
        raise ReportContractError(f"report must start with {REPORT_TITLE!r}")

    _require_sections_in_order(markdown)

    lower_markdown = markdown.lower()
    for phrase in REQUIRED_GUARDRAIL_PHRASES:
        if phrase not in lower_markdown:
            raise ReportContractError(f"report is missing required guardrail phrase: {phrase!r}")

    for phrase in FORBIDDEN_FINAL_RECOMMENDATION_PHRASES:
        if phrase in lower_markdown:
            raise ReportContractError(f"report contains forbidden recommendation phrase: {phrase!r}")


def _require_sections_in_order(markdown: str) -> None:
    last_position = -1
    for heading in REQUIRED_REPORT_HEADINGS:
        position = markdown.find(f"\n{heading}\n")
        if position == -1:
            raise ReportContractError(f"report is missing required section: {heading}")
        if position <= last_position:
            raise ReportContractError(f"report section is out of order: {heading}")
        last_position = position
