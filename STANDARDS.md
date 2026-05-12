# Project Standards

Initialized: 2026-05-11

## Operating Rules

- Read `GOAL.md`, `STANDARDS.md`, `IMPLEMENT.md`, `DECISIONS.md`, and `PROGRESS.md` before coding.
- Keep changes small and reviewable.
- Follow existing source direction before inventing new architecture.
- Update `PROGRESS.md` after meaningful work.
- Update `DECISIONS.md` when making or changing architecture, dependency, security, privacy, data model, UI/UX, deployment, or scope decisions.
- Do not mark a task done unless acceptance criteria and verification steps are satisfied.

## Clinical Safety Rules

- Advisory-only: Phase 0 is a development/research artifact, not clinical decision support.
- No PHI. Use synthetic fixtures only.
- Hard safety gates run before probabilistic scoring.
- Hard stops cannot be overridden by favorable Monte Carlo outputs.
- Missing data cannot improve recommendation certainty.
- Unknown or unmapped observations are not neutral; they should increase review pressure, missingness, uncertainty, or value-of-information priority.
- No outcome claims without outcome data and appropriate governance.
- No clinical deployment until calibration logging exists and governance has approved the mode.

## Output Rules

- No single truth score, trust score, or hidden composite as the primary result.
- Output is a Decision Profile: category, median fitness, interval, hard stops, missing variables, value-of-information, uncertainty budget, local execution checklist, prior provenance, and calibration status.
- Every visible probability or interval must carry provenance and uncertainty-budget context.
- Reports must state "advisory-only", "uncalibrated", and "not clinically validated" where applicable.
- Report language should use "uncertainty interval", "draft prior", "policy prior", and "calibration pending".
- Avoid "true probability", "validated risk", "AI confidence", "trust score", and "gold standard".

## Prior And Governance Rules

- Every prior must include distribution, parameters, provenance class, elicitation method or source basis, confidence class, review status, calibration status, owner, and review date when available.
- Phase 0 direct simulation must not use LLM-unverified priors.
- Draft policy priors may be used only when visibly labeled as draft and uncalibrated.
- Local rules must include owner and status. Draft local rules must be visibly marked in reports.
- A model may propose candidate knowledge in later phases, but deterministic validators and governance decide promotion.

## Engineering Standards

- Runtime target: Python 3.12+.
- Structured data should use Pydantic v2 models.
- Use PyYAML for domain packs, NumPy for Monte Carlo sampling, SciPy where correlations are needed, and pytest for tests.
- Prefer pure functions at module boundaries.
- Use typed models for data crossing boundaries.
- Keep HF clinical specifics in domain packs or fixtures, not hard-coded across the engine.
- Keep Phase 0 CLI-only. Do not add frontend, auth, persistence beyond JSONL logs, PDF, or async infrastructure.
- Use deterministic seeds in tests.
- Prefer simple, readable code over over-engineered abstractions.

## Verification Standards

Before marking implementation tasks complete:

- Run available tests.
- Add or update focused tests for changed behavior.
- Verify hard stops, missingness behavior, metamorphic shifts, and report completeness.
- Document tests run in `PROGRESS.md`.
- If tests cannot be run, document why in `PROGRESS.md`.

Required Phase 0 test classes:

- schema/model validation,
- domain pack and CDE loading,
- deterministic safety gates,
- prior resolver provenance validation,
- Monte Carlo reproducibility,
- hard-stop tests,
- missingness tests,
- metamorphic tests,
- uncertainty budget tests,
- value-of-information tests,
- report completeness tests,
- CLI run and validate tests.

## Provenance And Audit Standards

- Every run should eventually create JSONL-compatible log records for run metadata, priors used, and decision profiles.
- Logs are for calibration and audit structure, not clinical deployment.
- Agent_Pidgeon patterns may inform receipt and trace shape, but Phase 0 should not add Agent_Pidgeon as a dependency unless explicitly approved later.

