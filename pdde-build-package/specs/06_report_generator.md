# 06 — Report Generator

Produces the Decision Fitness Report in markdown format, matching the structure of `examples/sample_report_HF-001.md`.

## Purpose

Convert structured `SimulationResult` + `SensitivityAnalysis` + prohibited hits + network/case context into a clinician-readable markdown report.

## Function signature

```python
def generate_report(
    simulation: SimulationResult,
    sensitivities: list[SensitivityAnalysis],
    prohibited_hits: list[ProhibitedHit],
    network: BeliefNetwork,
    case: ClinicalCase,
    claim_evaluations: list[ClaimEvaluation] | None = None,  # Workflow A
) -> str:
    """Returns markdown string matching the structure of sample_report_HF-001.md."""
```

## Required sections (in order)

The report must include all of these sections. Use the sample report as a literal template.

### 1. Header
```markdown
# Decision Fitness Report

**Case ID:** {case_id}
**Generated:** {timestamp}
**Network:** {network_id} (version {network_version})
**Workflow:** {A_answer_adjudication | B_decision_simulation}
**Iterations:** {n_iterations}
```

### 2. Provenance warning (CONDITIONAL but mandatory if applicable)

If ANY prior used in the simulation has `confidence_class` of `moderate_unverified` or `low_unverified`, prepend a warning section:

```markdown
## ⚠️ PROVENANCE WARNING

This report uses placeholder priors (`confidence_class: moderate_unverified` or `low_unverified`)
for [list nodes]. These values **have not been formally elicited from a clinician panel**
and should be treated as illustrative until prior elicitation is complete.
Calibration is pending outcome data.

Do not use this output for actual clinical decision-making in v0.
```

This section is required when any unverified prior is used. Skipping it is a constraint violation.

### 3. Executive summary
Brief prose summary stating: case description, top 1-3 ranked options with median fitness, and the most sensitive variables.

### 4. Ranked decision options (table)

```markdown
| Rank | Option | Median Fitness | 90% Credible Interval | Category Probabilities |
|------|--------|---------------:|----------------------:|------------------------|
| 1    | ...    | ...            | ...                   | ...                    |
```

Sort by `median_fitness` descending. Include all six options. Format intervals as `[p5 – p95]`.

### 5. Sensitivity drivers

For the top-ranked option (or all options if you have space):

```markdown
## Sensitivity Drivers (variance decomposition)

For Option {N} ({option label}):

| Variable | Variance Contribution | Status |
|----------|----------------------:|--------|
| ... | 24% | ... |
```

Followed by:

```markdown
**Best next data to collect:**
1. ...
2. ...
```

### 6. Claim-level evidence maturity (Workflow A only)

If `claim_evaluations` is provided (Workflow A):

```markdown
## Claim-Level Evidence Maturity

| Claim | Evidence Maturity | Confidence Class |
|-------|-------------------|------------------|
| ... | ... | ... |
```

For Workflow B, replace with a note: "Workflow B (decision simulation); no AI answer evaluated."

### 7. Patient eligibility gates

```markdown
## Patient Eligibility Gates

| Gate | Value | Status | Impact |
|------|------:|--------|--------|
| SBP | 118 | action_ready | supports all discharge options |
```

Show all gates evaluated, including missing ones (mark as "missing" in Value column).

### 8. Local overlay status

```markdown
## Local Overlay Status ({institution})

⚠️ All Example Health System synthetic demo rules below are status: draft. They have not been verified by Example governance reviewers. They are metadata-only, non-activating, and not approved for clinical use.

| Item | Draft Value | Verification Status |
|------|-------------|---------------------|
| ... | ... | pending ... |
```

Pull from `network.local_overlay`. Display the warning whenever any local rule has `status != "verified"`.

### 9. Prohibited recommendation check

```markdown
## Prohibited Recommendation Check

| Pattern | Detected? |
|---------|-----------|
| Sotalol as HF beta-blocker | {Yes/No} |
| GLP-1 RA for HFrEF admission prevention | {Yes/No} |
| Digoxin as acute ED disposition-saver | {Yes/No} |
```

If detected, include a sub-section with the matched text and rationale.

### 10. Evidence-in-motion

```markdown
## Evidence-in-Motion (recent trials/guidelines)
```

Phase 0: hard-code a small list relevant to HF (DECISION trial, 2024 ACC consensus, 2022 guideline). Phase 1 will pull from a live evidence feed.

### 11. Defensible conclusion

Prose section synthesizing the findings. Should explicitly:
- Name the top-ranked option(s)
- Acknowledge wide intervals where present
- Identify which variables drive uncertainty
- Distinguish "patient profile supports X" from "local pathway supports X"

### 12. Reasonable clinicians could defend

A short prose section listing what reasonable practice variants the system considers defensible. Example:

> Reasonable clinicians could defend either:
> - The top option (continue GDMT + loop + follow-up) without ED initiation of new agents
> - The second option (add SGLT2i) **if local pathway gates are confirmed at the time of discharge**

### 13. Non-negotiable reminders

A fixed footer listing the design constraints in user-facing language:

```markdown
## Non-Negotiable Reminders

- This is not a verdict. It is a defensibility distribution.
- Placeholder priors are clearly labeled and should not be treated as validated.
- The engine cannot replace clinician judgment, especially for missing variables it flagged.
- Calibration data is not yet collected; predicted confidence has not been empirically validated.
```

## Output

The function returns a single markdown string. The CLI runner writes it to the specified output file.

## Style guidelines

- Use markdown tables for all structured data
- Use `>` blockquotes for warnings and key messages
- Use `**bold**` for emphasis sparingly
- Use `⚠️` emoji for warnings (the actual emoji, not text)
- Format percentages as `XX%` (no decimals unless needed)
- Format fitness scores as `0.XX` (two decimals)
- Format intervals as `[0.XX – 0.XX]`

## Acceptance tests

1. Output contains all 13 sections from the spec
2. Provenance warning section appears when any unverified prior is used
3. Provenance warning section is omitted when all priors are `confidence_class: high`
4. Local overlay warning appears when any rule has `status != "verified"`
5. Decision options table has six rows
6. Sensitivity drivers table has at least 3 rows
7. Generated report renders correctly in standard markdown viewers (GitHub, VS Code preview)
8. Report length is 60-200 lines (not too sparse, not bloated)

## Things to NOT do in Phase 0

- Do not generate PDF (Phase 1)
- Do not generate HTML (Phase 1)
- Do not embed interactive visualizations (Phase 2+)
- Do not internationalize (always English in Phase 0)
- Do not personalize tone or style based on user (Phase 2+)
