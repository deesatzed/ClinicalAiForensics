# Phase 0 Acceptance Tests

These are the six tests that determine whether Phase 0 is complete. Implement these as pytest tests in `tests/test_phase_0_acceptance.py`.

All six must pass.

---

## Test 1: Sotalol flagged as unsafe/wrong indication

**Setup:** Run the system in Workflow A with `examples/adversarial_sotalol.txt` as the AI answer.

**Assertion:** The generated report's "Prohibited Recommendation Check" section detects the sotalol-as-HF-beta-blocker pattern with `severity: unsafe_wrong_indication`.

```python
def test_sotalol_detected_as_unsafe():
    result = run_pipeline(
        case_path="examples/sample_case_HF-001.json",
        network_path="networks/hf_ed_discharge_v0.yaml",
        ai_answer_path="examples/adversarial_sotalol.txt",
    )
    assert any(
        hit.prohibited_id == "sotalol_as_hf_bb" and hit.severity == "unsafe_wrong_indication"
        for hit in result.prohibited_hits
    )
```

---

## Test 2: GLP-1 RA flagged as unsupported

**Setup:** Run with `examples/adversarial_glp1.txt` as the AI answer.

**Assertion:** Report detects the GLP-1-for-HF-prevention pattern with `severity: unsupported`.

```python
def test_glp1_detected_as_unsupported():
    result = run_pipeline(
        case_path="examples/sample_case_HF-001.json",
        network_path="networks/hf_ed_discharge_v0.yaml",
        ai_answer_path="examples/adversarial_glp1.txt",
    )
    assert any(
        hit.prohibited_id == "glp1_hf_admission_prevention" and hit.severity == "unsupported"
        for hit in result.prohibited_hits
    )
```

---

## Test 3: SGLT2 treated as conditional, not universal action-ready

**Setup:** Run Workflow B on `examples/sample_case_HF-001.json` (favorable patient profile).

**Assertion:** The `discharge_add_sglt2` option's classification is `conditionally_defensible` OR has `category_probabilities.conditionally_defensible` ≥ `category_probabilities.action_ready` (i.e., not predominantly action-ready).

```python
def test_sglt2_conditional_not_universal():
    result = run_pipeline_workflow_b(
        case_path="examples/sample_case_HF-001.json",
        network_path="networks/hf_ed_discharge_v0.yaml",
    )
    sglt2 = next(o for o in result.simulation.per_option if o.option_id == "discharge_add_sglt2")
    assert sglt2.classification in ("conditionally_defensible", "needs_more_data")
    assert sglt2.category_probabilities["conditionally_defensible"] >= sglt2.category_probabilities["action_ready"]
```

---

## Test 4: Missing data widens uncertainty

**Setup:** Create a copy of the sample case with `egfr`, `potassium`, and `follow_up_available` set to None. Run Workflow B.

**Assertion:** The `discharge_add_sglt2` option's interval width is at least 0.20 wider than in the full-data baseline run.

```python
def test_missing_data_widens_interval():
    baseline = run_pipeline_workflow_b(case_path="examples/sample_case_HF-001.json", ...)
    sparse = run_pipeline_workflow_b(case_path="examples/case_missing_labs.json", ...)

    sglt2_baseline = next(o for o in baseline.simulation.per_option if o.option_id == "discharge_add_sglt2")
    sglt2_sparse = next(o for o in sparse.simulation.per_option if o.option_id == "discharge_add_sglt2")

    assert sglt2_sparse.interval_width >= sglt2_baseline.interval_width + 0.20
```

(Create `examples/case_missing_labs.json` as part of this test.)

---

## Test 5: Variable changes shift recommendations appropriately

This is three sub-tests for counterfactual perturbations:

**5a:** Setting `egfr` from 45 to 15 should *decrease* median fitness for `discharge_add_sglt2` and `discharge_add_mra`.

**5b:** Setting `potassium` from 4.2 to 5.7 should produce near-zero fitness or "unsafe" classification for `discharge_add_mra`.

**5c:** Setting `sbp` from 118 to 86 should raise the rank of `admit_or_observe`.

```python
def test_egfr_drop_lowers_sglt2_fitness():
    baseline = run_pipeline_workflow_b(case_path="examples/sample_case_HF-001.json", ...)
    low_egfr_case = modify_case(baseline_case, egfr=15)
    low_egfr_result = run_pipeline_workflow_b(case=low_egfr_case, ...)

    sglt2_baseline = next(o for o in baseline.simulation.per_option if o.option_id == "discharge_add_sglt2")
    sglt2_low_egfr = next(o for o in low_egfr_result.simulation.per_option if o.option_id == "discharge_add_sglt2")

    assert sglt2_low_egfr.median < sglt2_baseline.median - 0.10

def test_high_potassium_makes_mra_unsafe():
    case = modify_case(baseline_case, potassium=5.7)
    result = run_pipeline_workflow_b(case=case, ...)
    mra = next(o for o in result.simulation.per_option if o.option_id == "discharge_add_mra")
    assert mra.median < 0.30 or mra.classification == "unsafe"

def test_low_sbp_raises_admit_observe():
    baseline = run_pipeline_workflow_b(case_path="examples/sample_case_HF-001.json", ...)
    low_sbp_case = modify_case(baseline_case, sbp=86)
    low_sbp_result = run_pipeline_workflow_b(case=low_sbp_case, ...)

    baseline_admit_rank = rank_of(baseline.simulation.per_option, "admit_or_observe")
    low_sbp_admit_rank = rank_of(low_sbp_result.simulation.per_option, "admit_or_observe")

    assert low_sbp_admit_rank < baseline_admit_rank  # lower rank number = higher position
```

---

## Test 6: Output is clinically reasonable without UI cosmetics

This is a *manual* test, executed by an Example governance reviewer or another clinician reviewer.

**Procedure:**
1. Run the system in Workflow B on `examples/sample_case_HF-001.json`
2. Read the generated report
3. Without UI polish, does the structured output convey:
   - The right top recommendation (continue GDMT)?
   - Appropriate uncertainty about SGLT2 ED-initiation?
   - Visible flags for unverified priors?
   - Reasonable sensitivity drivers?
   - A defensible conclusion statement?

**Pass criteria:** An Example governance reviewer reads the report and says "yes, this is structurally what a clinician would want to see — content needs work but the form is right."

This is the only subjective test in the suite, by design. The point of Phase 0 is to surface structural problems for Phase 1 to fix; ontology issues cannot all be caught by automated tests.

---

## Acceptance summary

Phase 0 is complete when:

- [ ] Test 1 passes (sotalol flagged unsafe)
- [ ] Test 2 passes (GLP-1 flagged unsupported)
- [ ] Test 3 passes (SGLT2 conditional, not universal)
- [ ] Test 4 passes (missing data widens interval)
- [ ] Test 5a passes (eGFR drop lowers SGLT2 fitness)
- [ ] Test 5b passes (high K makes MRA unsafe)
- [ ] Test 5c passes (low SBP raises admit_or_observe)
- [ ] Test 6 passes (an Example governance reviewer approves the structural form)

If any of 1-5 fail, fix before declaring Phase 0 done.
If Test 6 fails, document what's structurally wrong in `BUILD_LOG.md` and discuss with an Example governance reviewer before proceeding to Phase 1.
