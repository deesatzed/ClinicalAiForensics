# Risk Register — Phase 0 Build

Risks Claude Code should watch for during construction.

---

## R1: Garbage priors → confident wrong outputs

**Likelihood:** High
**Impact:** High
**Mitigation:**
- Every prior in YAML has `provenance_class` and `confidence_class`
- LLM-elicited priors are tagged `llm_unverified` / `low_unverified`
- Report includes provenance warning section when any unverified prior is used
- Pydantic validation rejects priors without provenance fields

**Build-time check:** Run `python -m pdde validate --network networks/hf_ed_discharge_v0.yaml` and verify every prior has full provenance.

---

## R2: LLM hallucinates citations or claims

**Likelihood:** Medium
**Impact:** High
**Mitigation:**
- Claim extractor uses temperature=0 for deterministic extraction
- Post-extraction validation against `Claim` Pydantic schema
- No claim is treated as truth; all flow into adjudication
- Citation auditing (existence check) deferred to v1 but logged for v0

**Build-time check:** Manually inspect a sample of extracted claims against the source text to verify faithful extraction.

---

## R3: Monte Carlo false precision

**Likelihood:** High
**Impact:** High
**Mitigation:**
- Wide credible intervals are surfaced prominently, not hidden
- Missing-data handling widens distributions rather than narrowing
- Report explicitly states "no claim that MC makes weak evidence strong"
- Sensitivity drivers surface uncertainty sources

**Build-time check:** Run the sample case and verify intervals are visibly wide for the SGLT2 option (target: interval width >0.20).

---

## R4: Overfitting to HF case

**Likelihood:** High
**Impact:** Medium
**Mitigation:**
- Code structured so adding a second case (Phase 2) doesn't require rewrites
- Generic interfaces between modules
- No HF-specific assumptions in `pdde/monte_carlo.py` or `pdde/sensitivity.py`
- YAML-driven; only `networks/hf_ed_discharge_v0.yaml` has HF specifics

**Build-time check:** Could the same code load a hypothetical `chest_pain_disposition_v0.yaml`? If not, refactor before declaring Phase 0 done.

---

## R5: Clinician over-reliance on output

**Likelihood:** Medium
**Impact:** High
**Mitigation:**
- Provenance warnings visible at top of report
- "Non-Negotiable Reminders" section at bottom of every report
- Explicit "This is not a verdict" language
- v0 explicitly not for clinical deployment

**Build-time check:** Read a sample report. Could a busy clinician miss the warnings? If yes, make them more prominent.

---

## R6: Spec ambiguity slowing build

**Likelihood:** Medium
**Impact:** Medium
**Mitigation:**
- Each spec includes acceptance tests
- "When to ask vs proceed" guidance in `CLAUDE.md`
- Default to simplest implementation when ambiguous; document choice in code comments

**Build-time check:** If you find yourself blocked on a spec ambiguity for >30 minutes, document the question in `BUILD_LOG.md` and pick the simplest path.

---

## R7: LLM API costs spiral

**Likelihood:** Low
**Impact:** Low (financial only)
**Mitigation:**
- Phase 0 only calls LLM for claim extraction (one call per case)
- Use Anthropic prompt caching for repeated system prompts
- Mock LLM in unit tests; only integration tests use real API

**Build-time check:** Track API spend; alert if >$10 for Phase 0 development.

---

## R8: YAML schema drift between runs

**Likelihood:** Medium
**Impact:** Medium
**Mitigation:**
- `schema_version` field in network YAML
- Loader validates schema_version matches expected
- Breaking schema changes require version bump

**Build-time check:** Pin schema_version to "pdde-belief-network-0.1" for Phase 0.

---

## R9: Performance bottleneck

**Likelihood:** Low
**Impact:** Low
**Mitigation:**
- Vectorized NumPy operations in Monte Carlo
- Single-pass sensitivity computation
- Profile before optimizing

**Build-time check:** Time the 10K-iteration sample case run. Target <5 seconds; if >10 seconds, profile.

---

## R10: Test fragility from non-determinism

**Likelihood:** Medium
**Impact:** Low
**Mitigation:**
- Use `--seed` in tests for reproducibility
- Use tolerance ranges in numerical assertions (e.g., `assert median < 0.30` not `assert median == 0.27`)
- Mock LLM calls in unit tests

**Build-time check:** Run the full test suite 3 times. If results vary, fix non-determinism before merging.

---

## R11: Phase 0 scope creep

**Likelihood:** High
**Impact:** Medium
**Mitigation:**
- Build order is fixed; do not deviate
- Phase 0 explicitly forbids: frontend, auth, DB, PDF, citation auditing beyond DOI check
- "Toy expected to be thrown away" philosophy in CLAUDE.md

**Build-time check:** If a task seems necessary but isn't in `build_order.md`, add it to `BUILD_LOG.md` for Phase 1 and move on.

---

## R12: Conflating Workflow A and Workflow B

**Likelihood:** Medium
**Impact:** Medium
**Mitigation:**
- Two clear workflow modes in `BeliefNetwork.workflow_modes`
- Workflow A requires an AI answer; Workflow B does not
- Report sections conditional on workflow mode (claims section only in A)
- CLI flag `--ai-answer` makes the choice explicit

**Build-time check:** Run sample case in both workflows. Reports should differ in structure (claims section present/absent).

---

## What to do if you encounter a new risk

Add to this file. Don't try to remember it. Update `BUILD_LOG.md` with the discovered risk and how you addressed it.
