# Tech Stack

## Language and runtime

- **Python 3.12+**
- **Platform**: macOS (Apple Silicon optimized), Linux supported

## Core dependencies

| Package | Version | Purpose |
|---|---|---|
| `pydantic` | `^2.7` | Data validation and schemas |
| `pyyaml` | `^6.0` | Load belief network YAML |
| `numpy` | `^1.26` | Monte Carlo sampling |
| `scipy` | `^1.13` | Statistical distributions, correlations |
| `anthropic` | `^0.34` | Claude API for claim extraction |
| `click` | `^8.1` | CLI framework (alternative: argparse from stdlib) |
| `rich` | `^13.7` | Terminal output formatting (optional but nice) |

## Dev dependencies

| Package | Version | Purpose |
|---|---|---|
| `pytest` | `^8.0` | Test runner |
| `pytest-cov` | `^5.0` | Coverage |
| `ruff` | `^0.5` | Linter and formatter |
| `mypy` | `^1.10` | Type checking |

## Deferred to later phases

- `numpyro` / `jax` — full Bayesian inference (Phase 1+)
- `sentence-transformers` — abstract-claim alignment (Phase 1+)
- `fastapi` — web backend (Phase 1+)
- `weasyprint` — PDF generation (Phase 1+)
- `sqlalchemy` + `postgresql` — persistence (Phase 1+)
- `react` + `tailwind` — frontend (Phase 1+)

## Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | For Workflow A | LLM access |
| `PDDE_LLM_MODEL` | Optional | Default `claude-opus-4-7` |
| `PDDE_RANDOM_SEED` | Optional | Reproducible Monte Carlo |
| `PDDE_LOG_LEVEL` | Optional | Default `INFO` |

## Suggested repo structure

```
pdde/
├── pyproject.toml
├── README.md
├── CLAUDE.md
├── BUILD_LOG.md          # Created at end of Phase 0
├── pdde/                 # Package source
│   ├── __init__.py
│   ├── __main__.py       # CLI entry
│   ├── models.py         # Pydantic models
│   ├── network_loader.py
│   ├── case_loader.py
│   ├── monte_carlo.py
│   ├── sensitivity.py
│   ├── prohibited_detector.py
│   ├── report.py
│   ├── claim_extractor.py
│   ├── parameterizer.py
│   └── prompts.py        # LLM prompt strings
├── networks/
│   └── hf_ed_discharge_v0.yaml
├── examples/
│   ├── sample_case_HF-001.json
│   ├── sample_report_HF-001.md
│   ├── adversarial_sotalol.txt
│   └── adversarial_glp1.txt
├── docs/
│   └── (from build package)
├── specs/
│   └── (from build package, for reference during build)
├── tests/
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_network_loader.py
│   ├── test_monte_carlo.py
│   ├── test_sensitivity.py
│   ├── test_report.py
│   ├── test_phase_0_acceptance.py
│   └── test_adversarial.py
└── .gitignore
```

## Code style

- Type hints everywhere (`from __future__ import annotations` at top of every file)
- Pydantic models for all structured data crossing module boundaries
- Pure functions where possible; stateful logic isolated to clearly named classes
- Docstrings on all public functions
- No clever code; readable code

## Testing approach

- Unit tests per module (in corresponding `test_*.py`)
- Integration tests at the `phase_0_acceptance.py` level
- Use `pytest` fixtures for sample case/network loading
- Use `pytest.mark.parametrize` for adversarial test cases
- Mock the Anthropic API in unit tests; use real API for integration tests only

## Performance budget for Phase 0

- Monte Carlo 10K iterations on sample case: **<5 seconds** on M4
- Full report generation (Workflow B, no LLM): **<10 seconds**
- Full report generation (Workflow A, with claim extraction): **<60 seconds** including LLM call
- YAML loading: **<500ms**

If any of these exceed the budget, profile before optimizing — the bottleneck is probably not where you expect.

## API cost budget for Phase 0

- Claim extraction: ~$0.05 per case (one API call, ~2K tokens in/out)
- Phase 0 total: <$10 even with extensive testing
