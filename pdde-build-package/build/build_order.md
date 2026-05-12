# Build Order

Sequential, dependency-ordered task list for Phase 0. Each task lists its inputs (what must exist before it starts), deliverables (what it produces), and acceptance criteria.

Do not skip tasks. Do not work on tasks before their dependencies are satisfied. If a task seems unnecessary, ask before skipping.

---

## Task 0.0: Project setup

**Inputs:** None
**Effort:** ~1h
**Deliverables:**
- `pyproject.toml` (use `build/pyproject_template.toml` as starting point)
- Virtual environment with dependencies installed
- `pdde/` package directory with `__init__.py`
- `pdde/__main__.py` stub
- Git repo initialized

**Acceptance:** `python -m pdde --help` runs without error.

---

## Task 0.1: Pydantic data models

**Spec:** `specs/01_data_models.md`
**Inputs:** Task 0.0 complete
**Effort:** ~3h
**Deliverables:**
- `pdde/models.py` with all Pydantic models from spec
- `tests/test_models.py` with unit tests for each model

**Acceptance:**
- All models from spec are importable
- `Prior` model rejects a prior without `provenance_class` and `confidence_class`
- `LocalRule` model rejects a rule without `status` and `owner`

---

## Task 0.2: YAML loader

**Spec:** Implicit; load `networks/hf_ed_discharge_v0.yaml` into typed Pydantic models from Task 0.1
**Inputs:** Tasks 0.0, 0.1
**Effort:** ~2h
**Deliverables:**
- `pdde/network_loader.py` with `load_network(path: Path) -> BeliefNetwork`
- `tests/test_network_loader.py`

**Acceptance:**
- `load_network("networks/hf_ed_discharge_v0.yaml")` returns a `BeliefNetwork` with no validation errors
- All six decision options present
- All three prohibited recommendations present
- Every prior has provenance fields populated

---

## Task 0.3: Case loader

**Spec:** Load `examples/sample_case_HF-001.json` into typed Pydantic models
**Inputs:** Tasks 0.0, 0.1
**Effort:** ~1h
**Deliverables:**
- `pdde/case_loader.py` with `load_case(path: Path) -> ClinicalCase`

**Acceptance:** `load_case("examples/sample_case_HF-001.json")` returns a typed object.

---

## Task 0.4: Monte Carlo engine

**Spec:** `specs/04_monte_carlo_engine.md`
**Inputs:** Tasks 0.1, 0.2, 0.3
**Effort:** ~6h
**Deliverables:**
- `pdde/monte_carlo.py` with `simulate(network, case, n_iterations=10000) -> SimulationResult`
- `tests/test_monte_carlo.py`

**Acceptance:**
- Runs 10,000 iterations on sample case in <5 seconds on M4
- Output is reproducible given a seed
- Posterior distributions returned for each of the six decision options
- Each option has: samples array, median, 5th/95th percentiles, category probabilities

---

## Task 0.5: Decision option scorer

**Spec:** Part of `specs/04_monte_carlo_engine.md`
**Inputs:** Task 0.4
**Effort:** ~3h
**Deliverables:**
- Scoring logic integrated into the Monte Carlo engine
- Per-option fitness computed using the formula in the YAML's `computed_nodes.decision_fitness`
- Gate-based eligibility filters applied (e.g., MRA requires `mra_eligible`)

**Acceptance:**
- Sample case produces a ranking (continue GDMT > urgent follow-up > SGLT2 > others) approximately matching `examples/sample_report_HF-001.md`
- Order does not have to match exactly; structure and direction must be right

---

## Task 0.6: Prohibited recommendation detector

**Spec:** Use `prohibited_recommendations` block in the YAML
**Inputs:** Tasks 0.1, 0.2
**Effort:** ~2h
**Deliverables:**
- `pdde/prohibited_detector.py`
- Function: `detect_prohibited(ai_answer_text: str, network: BeliefNetwork) -> list[ProhibitedHit]`
- Use simple substring matching from the `detection_pattern` field for Phase 0; do not invent complex NLP

**Acceptance:**
- Detects sotalol-as-HF-beta-blocker in `examples/adversarial_sotalol.txt`
- Detects GLP-1 RA for HF prevention in `examples/adversarial_glp1.txt`
- Returns empty list when no patterns present

---

## Task 0.7: Sensitivity analyzer

**Spec:** `specs/05_sensitivity_analyzer.md`
**Inputs:** Task 0.4
**Effort:** ~3h
**Deliverables:**
- `pdde/sensitivity.py` with `analyze(simulation_result) -> SensitivityAnalysis`
- Variance decomposition via Spearman rank correlation on Monte Carlo samples
- Per-variable variance contribution ranking

**Acceptance:**
- For the sample case, top-3 drivers include at least one of: `follow_up_reliability`, `local_executability`, or specific gate variables
- Output is a sorted list of (variable_name, variance_contribution) pairs

---

## Task 0.8: Report generator

**Spec:** `specs/06_report_generator.md`
**Inputs:** Tasks 0.4, 0.6, 0.7
**Effort:** ~5h
**Deliverables:**
- `pdde/report.py` with `generate_report(simulation, sensitivity, prohibited, network, case) -> str`
- Output is markdown matching the structure of `examples/sample_report_HF-001.md`

**Acceptance:**
- All sections from the target sample report are present in output
- Provenance warnings appear when any prior used has `confidence_class: moderate_unverified` or `low_unverified`
- Local overlay section shows `status: draft` markers
- Sensitivity drivers section has at least 3 entries
- Prohibited-recommendation check section present (empty list when no AI answer)

---

## Task 0.9: CLI runner

**Spec:** `specs/08_cli_runner.md`
**Inputs:** Tasks 0.2, 0.3, 0.4, 0.6, 0.7, 0.8
**Effort:** ~3h
**Deliverables:**
- `pdde/__main__.py` with argument parsing (use `argparse` or `click`)
- Commands: `run`, `validate`

**Acceptance:**
- `python -m pdde run --case examples/sample_case_HF-001.json --network networks/hf_ed_discharge_v0.yaml --output /tmp/report.md` produces a report file
- Output report has all required sections
- Exits with non-zero status on error
- `python -m pdde validate --network networks/hf_ed_discharge_v0.yaml` checks YAML structure and reports issues

---

## Task 0.10: Claim extractor (Workflow A)

**Spec:** `specs/02_claim_extractor.md`
**Prompt:** `prompts/claim_extraction.md`
**Inputs:** Tasks 0.1, 0.9
**Effort:** ~4h
**Deliverables:**
- `pdde/claim_extractor.py` with `extract_claims(ai_answer_text: str) -> list[Claim]`
- Uses Anthropic API (model from env var `PDDE_LLM_MODEL`, default `claude-opus-4-7`)
- Retries on malformed JSON; returns empty list on persistent failure (do not block report generation)
- CLI updated: `--ai-answer <path>` flag enables Workflow A

**Acceptance:**
- Extracts ≥3 distinct claims from `examples/adversarial_sotalol.txt`
- Each extracted claim has `claim_text`, `action`, `therapy`, `target_condition` populated
- Workflow A report includes a "Claims extracted from AI answer" section

---

## Task 0.11: Node parameterizer

**Spec:** `specs/03_node_parameterizer.md`
**Prompt:** `prompts/node_parameterization.md`
**Inputs:** Tasks 0.1, 0.10
**Effort:** ~3h
**Deliverables:**
- `pdde/parameterizer.py` with `parameterize(claim: Claim, network: BeliefNetwork) -> dict[str, Prior]`
- Maps a Claim to the relevant `by_claim_type` entries in the YAML's `evidence_applicability` node
- For unknown claim types, returns an LLM-elicited prior with `provenance_class: llm_unverified` and `confidence_class: low_unverified`

**Acceptance:**
- Maps "use loop diuretic plan" claim to `loop_diuretic_plan_after_diuresis` node
- Maps "start SGLT2" claim to `sglt2_ed_discharge_initiation` node
- For unknown claim, returns LLM-unverified prior with warning

---

## Task 0.12: Phase 0 acceptance test suite

**Spec:** `tests/phase_0_acceptance.md`
**Inputs:** All previous tasks
**Effort:** ~4h
**Deliverables:**
- `tests/test_phase_0_acceptance.py` implementing the 6 acceptance tests
- All tests pass

**Acceptance:** All 6 tests in `tests/phase_0_acceptance.md` pass.

---

## Task 0.13: Adversarial test suite

**Spec:** `tests/adversarial_suite.md`
**Inputs:** All previous tasks
**Effort:** ~4h
**Deliverables:**
- `tests/test_adversarial.py` with the 10 adversarial cases
- Document which pass and which fail (failures are expected and informative for Phase 0)

**Acceptance:** At least 5 of 10 adversarial tests pass. Failures are documented in `BUILD_LOG.md` for Phase 1 to address.

---

## Task 0.14: Build log

**Inputs:** All previous tasks
**Effort:** ~2h
**Deliverables:**
- `BUILD_LOG.md` at repo root documenting:
  - Ontology problems discovered
  - Specs that were wrong or ambiguous
  - Adversarial test failures with hypotheses for why
  - Recommendations for Phase 1 redesign

**Acceptance:** Wayne reads it and the next phase of work is clearly informed.

---

## Total effort estimate

~46 hours solo, faster with Claude Code. Aim for 2 weeks of calendar time with reasonable interruption tolerance.

## What "done" looks like

When Phase 0 is done, Wayne can run:

```bash
python -m pdde run \
  --case examples/sample_case_HF-001.json \
  --network networks/hf_ed_discharge_v0.yaml \
  --output report.md
```

…and get a Decision Fitness Report that is structurally similar to `examples/sample_report_HF-001.md`, with honest provenance warnings, sensible decision rankings, and a clear list of what would need to change to advance to Phase 1.

The report does not need to be clinically perfect. It needs to be honestly structured and reveal the ontology problems that need fixing.
