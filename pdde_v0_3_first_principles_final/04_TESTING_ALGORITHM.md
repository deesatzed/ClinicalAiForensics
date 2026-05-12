# Testing Algorithm v0.3

## Test Philosophy

Because there is no single oracle, tests should emphasize invariants, monotonicity, metamorphic behavior, and safety boundaries.

## Test Types

### 1. Unit Tests

- schema validation,
- safety gate parsing,
- prior resolution,
- Monte Carlo determinism,
- report completeness.

### 2. Metamorphic Tests

Change one variable and require directionally appropriate output shift.

Examples:

- eGFR 60 → 18 should lower MRA and SGLT2 fitness.
- K 4.2 → 5.8 should make MRA unsafe.
- SBP 120 → 86 should raise admit/observe.
- follow-up yes → no should lower local executability.
- no DKA risk → prior euglycemic DKA should lower SGLT2.

### 3. Missingness Tests

Removing critical data should not improve recommendations.

Expected:

- interval widens,
- “needs more data” probability rises,
- value-of-information ranks missing gate highly.

### 4. Hard-Stop Tests

Hard stops cannot be overcome by favorable soft priors.

Examples:

- active ketosis blocks routine SGLT2.
- K 5.8 blocks MRA.
- sotalol as HF GDMT is unsafe/wrong indication.
- persistent hypoxia/severe congestion raises admit/observe.

### 5. Uncertainty Budget Tests

Every report must decompose uncertainty into sources.

Minimum categories:

- evidence,
- patient context,
- local execution,
- monitoring/rescue,
- harm,
- preference/feasibility,
- prior quality.

### 6. Report Tests

Every report must include:

- advisory status,
- calibration status,
- prior provenance,
- local rule status,
- missing variables,
- value-of-information.

## Phase 0 Test Fixtures

1. HF_STABLE
2. HF_LOW_EGFR
3. HF_HIGH_K
4. HF_LOW_SBP
5. HF_NO_FOLLOWUP
6. HF_PRIOR_DKA
7. HF_MISSING_LABS
8. HF_STILL_CONGESTED
9. HF_HFMREF
10. HF_UNSAFE_MEDICATION_CLAIM

## Pass Standard

For Phase 0, tests pass if model behavior is directionally correct, not if exact numeric outputs match.
