# Unit Test Specifications

Per-component unit tests. These complement the integration-level Phase 0 acceptance tests.

Test discovery uses pytest defaults: any `test_*.py` in `tests/` directory.

---

## tests/test_models.py

Tests for `pdde/models.py` (Pydantic schemas).

```python
def test_prior_requires_provenance_class():
    """Prior without provenance_class raises ValidationError."""

def test_prior_unverified_requires_warning():
    """Prior with low_unverified confidence but no warning raises ValidationError."""

def test_local_rule_verified_requires_verifier():
    """LocalRule with status=verified but verified_by=None raises ValidationError."""

def test_beta_prior_requires_positive_params():
    """Beta distribution with alpha<=0 or beta<=0 raises ValidationError."""

def test_decision_option_loads_with_empty_requires():
    """DecisionOption can have empty requires list."""

def test_belief_network_loads_full_yaml():
    """Full HF YAML parses into BeliefNetwork without error."""

def test_clinical_case_workflow_mode_enum():
    """ClinicalCase rejects invalid workflow_mode."""
```

---

## tests/test_network_loader.py

```python
def test_load_hf_network():
    """networks/hf_ed_discharge_v0.yaml loads successfully."""

def test_network_has_six_options():
    """HF network defines exactly six decision options."""

def test_network_has_three_prohibited():
    """HF network defines exactly three prohibited recommendations."""

def test_all_priors_have_provenance():
    """Every node prior in the loaded network has provenance_class set."""

def test_invalid_yaml_path_raises():
    """load_network on missing file raises FileNotFoundError."""

def test_malformed_yaml_raises():
    """load_network on malformed YAML raises with helpful message."""
```

---

## tests/test_case_loader.py

```python
def test_load_sample_case():
    """sample_case_HF-001.json loads successfully."""

def test_case_network_id_match_validation():
    """Loading case whose network_id doesn't match the network raises."""
```

---

## tests/test_monte_carlo.py

```python
def test_simulate_returns_six_options():
    """simulate() returns SimulationResult with 6 OptionPosteriors."""

def test_seeded_simulation_reproducible():
    """Two runs with same seed produce identical samples."""

def test_n_iterations_respected():
    """simulate(n_iterations=500) returns 500 samples per option."""

def test_classification_probabilities_sum_to_one():
    """For each option, category_probabilities sum to 1.0 (±0.001)."""

def test_admit_observe_lower_when_patient_stable():
    """For sample case (stable patient), admit_or_observe ranks lower than discharge_continue_gdmt."""

def test_egfr_15_lowers_sglt2():
    """Counterfactual: eGFR=15 case has lower SGLT2 median than baseline."""

def test_potassium_57_makes_mra_unsafe():
    """K=5.7 case classifies discharge_add_mra as unsafe or discouraged."""

def test_sbp_86_raises_admit_observe():
    """SBP=86 case ranks admit_or_observe higher than baseline."""

def test_performance_10k_iterations_under_5_seconds():
    """10K iterations on sample case completes in <5 seconds."""
```

---

## tests/test_sensitivity.py

```python
def test_analyze_returns_drivers():
    """analyze() returns at least one driver per option."""

def test_drivers_sorted_by_contribution():
    """Drivers are sorted descending by variance_contribution."""

def test_ranks_match_sort():
    """rank field is 1-indexed and matches sort order."""

def test_best_next_data_populated():
    """best_next_data_to_collect has at least one entry."""

def test_drivers_capped_at_5():
    """Returns at most 5 top drivers per option."""
```

---

## tests/test_prohibited_detector.py

```python
def test_sotalol_detected():
    """detect_prohibited() returns hit for sotalol-as-HF-BB text."""

def test_glp1_for_hf_detected():
    """detect_prohibited() returns hit for GLP-1-as-HF-prevention text."""

def test_digoxin_acute_detected():
    """detect_prohibited() returns hit for digoxin-as-acute-disposition text."""

def test_no_hits_when_clean():
    """detect_prohibited() returns empty list for benign text."""

def test_case_insensitive_matching():
    """Detection is case-insensitive."""
```

---

## tests/test_report.py

```python
def test_report_has_all_sections():
    """Generated report contains all 13 required sections (header, executive summary, etc.)."""

def test_provenance_warning_when_unverified():
    """When any prior is moderate_unverified, report includes provenance warning."""

def test_no_provenance_warning_when_all_verified():
    """When all priors are high confidence, no provenance warning section."""

def test_local_overlay_draft_warning():
    """When any local rule is status=draft, report shows local overlay warning."""

def test_six_options_in_table():
    """Ranked decision options table has six rows."""

def test_table_sorted_by_fitness():
    """Decision options table is sorted by median fitness descending."""

def test_report_renders_valid_markdown():
    """Generated report passes basic markdown validation (no broken tables, no unclosed code blocks)."""
```

---

## tests/test_claim_extractor.py

These tests use a mocked Anthropic client; only `test_real_api_call` uses the actual API and is marked `@pytest.mark.integration`.

```python
@pytest.fixture
def mock_anthropic_client(monkeypatch):
    """Provide a mock that returns canned responses."""

def test_extract_claims_from_sotalol_answer(mock_anthropic_client):
    """Mocked response yields the expected Claim objects."""

def test_malformed_json_triggers_retry(mock_anthropic_client):
    """Bad JSON triggers retry, eventually returns empty list."""

def test_api_failure_returns_empty_list(mock_anthropic_client):
    """Network error returns empty list, not exception."""

def test_therapy_normalization_applied():
    """Post-extraction normalization handles aliases like 'dapagliflozin' -> 'SGLT2 inhibitor'."""

def test_sotalol_not_normalized_to_beta_blocker():
    """Sotalol stays as 'sotalol' even though it's a beta blocker chemically."""

@pytest.mark.integration
def test_real_api_call():
    """Live test against Anthropic API; requires ANTHROPIC_API_KEY env var."""
```

---

## tests/test_parameterizer.py

```python
def test_known_claim_maps_to_node():
    """SGLT2 claim maps to sglt2_ed_discharge_initiation node."""

def test_sotalol_maps_to_sotalol_node():
    """Sotalol claim maps to sotalol_as_hf_beta_blocker (not evidence_based_beta_blocker)."""

def test_unknown_claim_triggers_llm_fallback(mock_anthropic_client):
    """Unknown claim returns LLM-elicited prior."""

def test_llm_fallback_prior_is_unverified(mock_anthropic_client):
    """LLM-fallback prior has provenance_class=LLM_UNVERIFIED."""

def test_llm_fallback_prior_has_warning(mock_anthropic_client):
    """LLM-fallback prior has non-null warning field."""
```

---

## tests/test_provenance_logger.py

```python
def test_start_run_creates_entry():
    """start_run() appends to runs.jsonl."""

def test_log_prior_creates_entry():
    """log_prior() appends to priors.jsonl with correct run_id."""

def test_log_prediction_creates_entry():
    """log_prediction() appends to predictions.jsonl with correct run_id."""

def test_jsonl_files_are_valid_json():
    """Every line in each .jsonl file parses as JSON."""

def test_two_runs_have_different_run_ids():
    """Successive start_run() calls produce different run_ids."""
```

---

## tests/test_cli.py

```python
def test_help_works():
    """python -m pdde --help exits 0."""

def test_run_with_valid_args(tmp_path):
    """python -m pdde run with valid args produces a report file."""

def test_missing_required_arg_exits_nonzero():
    """Missing --case flag produces non-zero exit."""

def test_seed_produces_reproducible_output(tmp_path):
    """--seed 42 produces identical reports across two runs."""

def test_validate_command(tmp_path):
    """python -m pdde validate --network valid.yaml exits 0."""

def test_validate_command_fails_on_bad_yaml(tmp_path):
    """python -m pdde validate --network bad.yaml exits nonzero."""
```

---

## Coverage target

Phase 0 coverage target: **>70% line coverage** in `pdde/` package.

Use `pytest --cov=pdde --cov-report=term-missing` to check.
