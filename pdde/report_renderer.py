"""Markdown Decision Profile report renderer.

The renderer converts an ``EvaluationPipelineResult`` into a deterministic
Markdown report. It presents existing component outputs and explicit deferrals;
it does not create recommendation rankings, final clinical conclusions, or
hidden scores.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from .pipeline_models import EvaluationPipelineResult
from .report_contract import REPORT_SECTIONS, validate_report_contract
from .status_ledger import build_status_ledger


def render_markdown_report(result: EvaluationPipelineResult) -> str:
    """Render an advisory-only Markdown report from pipeline output."""

    sections = [
        _header(result),
        *[_render_section(section.section_id, result) for section in REPORT_SECTIONS],
    ]
    markdown = "\n\n".join(section.rstrip() for section in sections) + "\n"
    validate_report_contract(markdown)
    return markdown


def _render_section(section_id: str, result: EvaluationPipelineResult) -> str:
    try:
        renderer = _SECTION_RENDERERS[section_id]
    except KeyError as exc:
        raise RuntimeError(f"missing report renderer for required section {section_id!r}") from exc
    return renderer(result)


def _header(result: EvaluationPipelineResult) -> str:
    metadata = [
        ("Case ID", result.cde.cde_id),
        ("Domain", result.cde.domain),
        ("Decision moment", result.cde.decision_moment),
        ("Domain pack", f"{result.domain_pack.domain_pack_id} ({result.domain_pack.version})"),
        ("Workflow", result.workflow_mode),
        ("Iterations", result.n_iterations),
        ("Random seed", result.random_seed),
        ("Domain calibration status", result.domain_pack.calibration_status),
        ("CDE source", result.cde_source),
        ("Domain source", result.domain_pack_source),
    ]
    rows = "\n".join(f"**{label}:** {_inline(value)}" for label, value in metadata)
    return f"# PDDE Decision Profile Report\n\n{rows}"


def _advisory_status() -> str:
    return (
        "## Advisory Status\n\n"
        "> Advisory-only decision-profile report. This output is not clinically validated, "
        "does not determine truth, and is not a final clinical recommendation. It displays "
        "explicit assumptions, safety gates, draft priors, calibration pending status, "
        "and deferred inputs from the deterministic pipeline."
    )


def _decision_episode_summary(result: EvaluationPipelineResult) -> str:
    patient_state = _dict_items(result.cde.patient_state)
    source_recommendations = [
        f"{item.source}: {item.text}" for item in result.cde.source_recommendations
    ] or ["None provided."]
    rows = [
        ("Case text", result.cde.case_text or "n/a"),
        ("Candidate options", result.cde.candidate_options),
        ("Patient state", patient_state),
        ("Source recommendations", source_recommendations),
        ("Local context metadata", _safe_local_context_items(result.cde.local_context) or ["n/a"]),
        ("Outcome tracking", _dict_items(result.cde.outcome_tracking) or ["n/a"]),
    ]
    return "## Decision Episode Summary\n\n" + _table(["Field", "Value"], rows)


def _safety_gate_results(result: EvaluationPipelineResult) -> str:
    mapping_context = ""
    if result.ai_answer_mapping.claims:
        mapping_rows = [
            (
                claim.claim_id,
                claim.status,
                claim.claim_type or "n/a",
                claim.matched_terms or "none",
                claim.source,
                claim.reason,
            )
            for claim in result.ai_answer_mapping.claims
        ]
        mapping_context = (
            "AI-answer mapping inputs are structured deterministic claim metadata only. "
            "Raw answer text is not printed and no answer grade is computed.\n\n"
            + _table(
                ["Claim ID", "Status", "Claim type", "Matched terms", "Source", "Reason"],
                mapping_rows,
            )
            + "\n\n"
        )

    rows = [
        (
            evaluation.gate_group,
            evaluation.option_id or evaluation.claim_type or "unmapped",
            evaluation.variable or "n/a",
            evaluation.condition or "n/a",
            evaluation.status,
            evaluation.evidence,
        )
        for evaluation in result.safety_gates.evaluations
    ]
    return "## Safety Gate Results\n\n" + mapping_context + _table(
        ["Gate group", "Target", "Variable", "Condition", "Status", "Evidence"],
        rows,
    )


def _decision_profile_statuses(result: EvaluationPipelineResult) -> str:
    rows = [
        (
            profile.option_id,
            profile.option_label or "n/a",
            profile.status,
            profile.active_blockers or "none",
            profile.active_triggers or "none",
            profile.missing_data or "none",
            profile.unsupported_inputs or "none",
            profile.reason,
        )
        for profile in result.decision_profiles.profiles
    ]
    return (
        "## Decision Profile Statuses\n\n"
        "Profiles are shown in domain-pack input order. No option ranking or final "
        "recommendation is computed by this report.\n\n"
        + _table(
            [
                "Option ID",
                "Label",
                "Status",
                "Blockers",
                "Triggers",
                "Missing data",
                "Unsupported inputs",
                "Reason",
            ],
            rows,
        )
    )


def _why_no_top_option() -> str:
    return (
        "## Why There Is No Top Option\n\n"
        "The current v0.3 source files do not define a decision-fitness formula, option "
        "utility, ranking threshold, or prior-to-option weighting model. This report "
        "therefore preserves profile status evidence without naming a top option or "
        "turning eligibility into a recommendation."
    )


def _missing_and_value_of_information(result: EvaluationPipelineResult) -> str:
    rows = [
        (
            item.rank or "n/a",
            item.variable,
            item.status,
            item.actionable,
            item.could_change_decision,
            item.source_field or "n/a",
            item.required_data or "none",
            item.related_gate_groups or "none",
            item.reason,
        )
        for item in result.value_of_information.items
    ]
    return "## Missing Variables And Value Of Information\n\n" + _table(
        [
            "Rank",
            "Variable",
            "Status",
            "Actionable",
            "Could change decision",
            "Source field",
            "Required data",
            "Related gates",
            "Reason",
        ],
        rows,
    )


def _uncertainty_budget(result: EvaluationPipelineResult) -> str:
    rows = [
        (
            item.category,
            item.status,
            item.actionable,
            item.could_change_decision,
            item.related_variables or item.related_prior_ids or item.related_gate_groups or "none",
            item.required_data or "none",
            item.source_fields or "none",
            item.reason,
            item.source,
        )
        for item in result.uncertainty_budget.items
    ]
    return "## Uncertainty Budget\n\n" + _table(
        [
            "Category",
            "Status",
            "Actionable",
            "Could change decision",
            "Related inputs",
            "Required data",
            "Source fields",
            "Reason",
            "Source",
        ],
        rows,
    )


def _local_execution_checklist(result: EvaluationPipelineResult) -> str:
    overlay_rows = [
        (
            item.overlay_id,
            item.status,
            _present(item.owner),
            _present(item.source_reference),
            _present(item.review_cadence),
            _present(item.last_reviewed),
            item.missing_fields or "none",
            item.reason,
        )
        for item in result.local_overlay.items
    ]
    local_items = [
        item
        for item in result.uncertainty_budget.items
        if item.category in {"local_execution_uncertainty", "monitoring_rescue_uncertainty"}
    ]
    rows = [
        (
            item.category,
            item.status,
            item.required_data or "none",
            item.reason,
        )
        for item in local_items
    ]
    if not rows:
        rows = [("local_execution_uncertainty", "deferred", "n/a", "No local execution items returned.")]
    return (
        "## Local Execution Checklist\n\n"
        "The pipeline records local overlay verification metadata only. It does not apply "
        "local workflow rules, and raw local workflow text is not printed.\n\n"
        "### Local Overlay Verification\n\n"
        + _table(
            [
                "Overlay",
                "Status",
                "Owner",
                "Source",
                "Review cadence",
                "Last reviewed",
                "Missing fields",
                "Reason",
            ],
            overlay_rows,
        )
        + "\n\n### Local Uncertainty Items\n\n"
        + _table(["Item", "Status", "Required data", "Reason"], rows)
    )


def _patient_feasibility_preference_gaps(result: EvaluationPipelineResult) -> str:
    variables = {"medication_access", "patient_preference", "follow_up_available"}
    rows = [
        (
            item.variable,
            item.status,
            item.source_field or "n/a",
            item.required_data or "none",
            item.reason,
        )
        for item in result.value_of_information.items
        if item.variable in variables
    ]
    if not rows:
        rows = [("n/a", "deferred", "n/a", "n/a", "No patient feasibility/preference items returned.")]
    return "## Patient Feasibility And Preference Gaps\n\n" + _table(
        ["Variable", "Status", "Source field", "Required data", "Reason"],
        rows,
    )


def _prior_provenance(result: EvaluationPipelineResult) -> str:
    rows = [
        (
            resolution.prior_id,
            resolution.status,
            resolution.distribution or "n/a",
            _parameters(resolution.parameters),
            resolution.provenance_class or "n/a",
            resolution.normalized_provenance_class or "n/a",
            resolution.confidence_class or "n/a",
            resolution.calibration_status or "n/a",
            resolution.warning or "none",
            resolution.source or "n/a",
            resolution.reason,
        )
        for resolution in result.prior_resolutions.resolutions
    ]
    return "## Prior Provenance\n\n" + _table(
        [
            "Prior ID",
            "Status",
            "Distribution",
            "Parameters",
            "Provenance",
            "Normalized provenance",
            "Confidence",
            "Calibration",
            "Warning",
            "Source",
            "Reason",
        ],
        rows,
    )


def _monte_carlo_summaries(result: EvaluationPipelineResult) -> str:
    rows = [
        (
            simulation.prior_id,
            simulation.status,
            simulation.sample_count,
            _float(simulation.sample_median),
            _float(simulation.p5),
            _float(simulation.p95),
            _float(simulation.interval_width),
            simulation.calibration_status or "n/a",
            simulation.source or "n/a",
            simulation.reason,
        )
        for simulation in result.simulation.prior_simulations
    ]
    return (
        "## Monte Carlo Prior Summaries\n\n"
        "Monte Carlo output is prior-level only. It is not an option ranking and cannot "
        "override a deterministic safety gate.\n\n"
        + _table(
            [
                "Prior ID",
                "Status",
                "Samples",
                "Median",
                "P5",
                "P95",
                "Interval width",
                "Calibration",
                "Source",
                "Reason",
            ],
            rows,
        )
    )


def _items_requiring_attention(result: EvaluationPipelineResult) -> str:
    ledger = build_status_ledger(result)
    rows: list[tuple[Any, ...]] = [
        (
            row.component,
            row.identifier,
            row.status,
            row.source or "n/a",
            row.reason,
        )
        for row in ledger.unresolved_rows()
    ]
    if not rows:
        rows = [("pipeline", "none", "none", "n/a", "No missing, unsupported, blocked, active, or deferred items.")]
    return "## Missing Unsupported Deferred And Blocked Items\n\n" + _table(
        ["Component", "Identifier", "Status", "Source", "Reason"],
        rows,
    )


def _calibration_status(result: EvaluationPipelineResult) -> str:
    prior_rows = [
        (resolution.prior_id, resolution.calibration_status or "n/a", resolution.confidence_class or "n/a")
        for resolution in result.prior_resolutions.resolutions
    ]
    return (
        "## Calibration Status\n\n"
        + _table(
            ["Field", "Value"],
            [
                ("Domain pack calibration", result.domain_pack.calibration_status),
                ("Outcome tracking", _dict_items(result.cde.outcome_tracking) or "n/a"),
                ("Pipeline statement", "calibration pending; not clinically validated"),
            ],
        )
        + "\n\n"
        + _table(["Prior ID", "Calibration", "Confidence"], prior_rows)
    )


def _provenance_references(result: EvaluationPipelineResult) -> str:
    references = _unique(
        [
            result.cde_source,
            result.domain_pack_source,
            *[claim.source for claim in result.ai_answer_mapping.claims],
            *[item.source for item in result.prior_resolutions.resolutions],
            *[item.source for item in result.simulation.prior_simulations],
            *[item.source for item in result.value_of_information.items],
            *[item.source for item in result.uncertainty_budget.items],
            *[item.source for item in result.local_overlay.items],
            *[item.source for item in result.decision_profiles.input_summaries],
            *[
                reference
                for profile in result.decision_profiles.profiles
                for reference in profile.provenance_references
            ],
        ]
    )
    lines = "\n".join(f"- {_inline(reference)}" for reference in references) or "- n/a"
    return f"## Provenance References\n\n{lines}"


def _limitations() -> str:
    limitations = [
        "This report is advisory-only and not clinically validated.",
        "No final clinical recommendation, safe discharge conclusion, unsafe discharge conclusion, or top option is generated.",
        "No hidden scoring, option utility, or ranking formula is applied.",
        "Monte Carlo summaries are prior-level only and cannot override safety gates.",
        "Wrong-indication claim gates that require AI answer mapping remain unsupported in direct CDE simulation.",
        "Local workflow and monitoring pathways remain draft or deferred unless explicitly verified in source data.",
        "Local overlay verification records metadata presence only and does not activate local clinical rules.",
        "No PHI should be used; current fixtures are synthetic.",
    ]
    return "## Limitations\n\n" + "\n".join(f"- {item}" for item in limitations)


_SECTION_RENDERERS: dict[str, Callable[[EvaluationPipelineResult], str]] = {
    "advisory_status": lambda _result: _advisory_status(),
    "decision_episode_summary": _decision_episode_summary,
    "safety_gate_results": _safety_gate_results,
    "decision_profile_statuses": _decision_profile_statuses,
    "why_no_top_option": lambda _result: _why_no_top_option(),
    "missing_and_value_of_information": _missing_and_value_of_information,
    "uncertainty_budget": _uncertainty_budget,
    "local_execution_checklist": _local_execution_checklist,
    "patient_feasibility_preference_gaps": _patient_feasibility_preference_gaps,
    "prior_provenance": _prior_provenance,
    "monte_carlo_summaries": _monte_carlo_summaries,
    "items_requiring_attention": _items_requiring_attention,
    "calibration_status": _calibration_status,
    "provenance_references": _provenance_references,
    "limitations": lambda _result: _limitations(),
}


def _table(headers: list[str], rows: Iterable[tuple[Any, ...]]) -> str:
    header_line = "| " + " | ".join(_cell(header) for header in headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    row_lines = [
        "| " + " | ".join(_cell(value) for value in row) + " |"
        for row in rows
    ]
    return "\n".join([header_line, separator, *row_lines])


def _cell(value: Any) -> str:
    return _inline(value).replace("|", "\\|")


def _inline(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return _float(value)
    if isinstance(value, dict):
        return "<br>".join(f"{key}={_inline(value[key])}" for key in sorted(value)) or "none"
    if isinstance(value, list | tuple | set):
        values = list(value)
        return "<br>".join(_inline(item) for item in values) if values else "none"
    return str(value).replace("\n", "<br>").strip() or "n/a"


def _dict_items(value: dict[str, Any]) -> list[str]:
    return [f"{key}={_inline(value[key])}" for key in sorted(value)]


def _safe_local_context_items(value: dict[str, Any]) -> list[str]:
    safe_keys = {
        "derived_from",
        "fixture_kind",
        "overlay_status",
        "phi_status",
        "synthetic",
        "variant_focus",
    }
    items = [f"{key}={_inline(value[key])}" for key in sorted(value) if key in safe_keys]
    hidden_count = len([key for key in value if key not in safe_keys])
    if hidden_count:
        items.append(f"redacted_local_context_fields={hidden_count}")
    return items


def _present(value: Any | None) -> str:
    return "present" if value is not None else "missing"


def _parameters(parameters: dict[str, float] | None) -> str:
    if not parameters:
        return "n/a"
    return ", ".join(f"{key}={_float(parameters[key])}" for key in sorted(parameters))


def _float(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.3f}"


def _unique(values: Iterable[str | None]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value is None or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
