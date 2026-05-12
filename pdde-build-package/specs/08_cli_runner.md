# 08 — CLI Runner

The user-facing entry point. Glues all modules together.

## Purpose

Provide a clean command-line interface for running PDDE on a case, with optional AI answer adjudication.

## Commands

### `run` — Main command

```bash
python -m pdde run \
  --case examples/sample_case_HF-001.json \
  --network networks/hf_ed_discharge_v0.yaml \
  --output report.md \
  [--ai-answer examples/adversarial_sotalol.txt] \
  [--iterations 10000] \
  [--seed 42] \
  [--verbose]
```

Arguments:

| Flag | Required | Default | Description |
|---|---|---|---|
| `--case` | Yes | — | Path to case JSON |
| `--network` | Yes | — | Path to network YAML |
| `--output` | Yes | — | Path for output report markdown |
| `--ai-answer` | No | None | Path to pasted AI answer (enables Workflow A) |
| `--iterations` | No | 10000 | Monte Carlo iterations |
| `--seed` | No | None | Random seed for reproducibility |
| `--verbose` | No | False | Log detailed progress |

### `validate` — Validate a network or case

```bash
python -m pdde validate --network networks/hf_ed_discharge_v0.yaml
python -m pdde validate --case examples/sample_case_HF-001.json
```

Checks structure, required fields, value constraints. Reports issues found.

### `--help`

Standard help output for all commands.

## Pipeline

```python
def run_command(case_path, network_path, output_path, ai_answer_path=None, iterations=10000, seed=None):
    # 1. Load network and case
    network = load_network(network_path)
    case = load_case(case_path)

    # 2. Validate case matches network
    assert case.network_id == network.network_id

    # 3. Start provenance logging
    logger = ProvenanceLogger()
    run_id = logger.start_run(case, network)

    # 4. Workflow A: extract claims from AI answer if provided
    claims = []
    prohibited_hits = []
    claim_evaluations = []
    if ai_answer_path:
        ai_text = ai_answer_path.read_text()
        claims = extract_claims(ai_text)
        prohibited_hits = detect_prohibited(ai_text, network)
        for claim in claims:
            priors = parameterize(claim, network)
            claim_evaluations.append(ClaimEvaluation(claim=claim, priors=priors))

    # 5. Run Monte Carlo
    simulation = simulate(network, case, n_iterations=iterations, random_seed=seed)

    # 6. Log priors used
    for node_name, prior in simulation.priors_used.items():
        logger.log_prior(node_name, prior, warning_displayed=prior.warning is not None)

    # 7. Compute sensitivities
    sensitivities = analyze(simulation)

    # 8. Generate report
    report_md = generate_report(
        simulation=simulation,
        sensitivities=sensitivities,
        prohibited_hits=prohibited_hits,
        network=network,
        case=case,
        claim_evaluations=claim_evaluations if ai_answer_path else None,
    )

    # 9. Write report
    output_path.write_text(report_md)

    # 10. Log predictions
    for option in simulation.per_option:
        logger.log_prediction(option)

    # 11. End run
    logger.end_run()

    # 12. Print summary to stdout
    print(f"Report written to {output_path}")
    print(f"Top option: {simulation.per_option[0].option_id} (median fitness {simulation.per_option[0].median:.2f})")
```

## Error handling

- Missing files: clear error message, exit code 1
- YAML/JSON parse errors: report file and approximate location, exit code 1
- Validation errors: report specific field and constraint violated, exit code 1
- LLM API failure: log warning, proceed with Workflow A degraded mode (empty claims list), exit code 0
- Other unexpected errors: print stack trace if --verbose, otherwise concise error, exit code 2

## Output to stdout

In normal mode:

```
PDDE v0.1.0
Network: hf_ed_discharge_v0 (version 0.1)
Case: HF-001-stable-postdiuresis
Workflow: B (decision simulation)
Running 10,000 Monte Carlo iterations... done (2.3s)
Computing sensitivities... done (0.4s)
Generating report... done (0.1s)

Top-ranked option: discharge_continue_gdmt (median fitness 0.81)
Report written to report.md
```

In `--verbose` mode, log every step including LLM calls, individual node sampling stats, sensitivity computation, etc.

## Acceptance tests

1. `python -m pdde --help` prints help without error
2. `python -m pdde run --case examples/sample_case_HF-001.json --network networks/hf_ed_discharge_v0.yaml --output /tmp/report.md` produces a report file
3. Missing required arg produces helpful error and non-zero exit
4. `--seed 42` produces reproducible results across two runs
5. `--ai-answer` flag triggers Workflow A and the report includes a claims section
6. `--verbose` produces detailed log output

## Things to NOT do in Phase 0

- Do not add a TUI or interactive prompts (Phase 1+)
- Do not add a `--config` file (Phase 1 if needed)
- Do not add streaming output beyond basic progress (Phase 1)
- Do not add subcommands beyond `run` and `validate`
