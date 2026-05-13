# FIRST_TASK.md

Concrete first action for Claude Code. After reading `CLAUDE.md` and `docs/non_negotiable_constraints.md`, do this.

---

## Your immediate first task

Create the project skeleton. Do exactly these steps, in this order. Stop after step 8 and report status.

### Step 1: Create pyproject.toml

Copy `build/pyproject_template.toml` to repo root as `pyproject.toml`. Make these substitutions:

- `{author_email}` → ask user, or leave as placeholder

### Step 2: Create the package directory

```bash
mkdir -p pdde
touch pdde/__init__.py
```

In `pdde/__init__.py`:

```python
"""PDDE — Probabilistic Defensible Decision Engine."""

__version__ = "0.1.0"
```

### Step 3: Create CLI stub

Create `pdde/__main__.py`:

```python
"""CLI entry point for PDDE."""

import click


@click.group()
@click.version_option()
def cli() -> None:
    """PDDE — Probabilistic Defensible Decision Engine."""


@cli.command()
def run() -> None:
    """Run PDDE on a case (not yet implemented)."""
    click.echo("Not yet implemented — see build/build_order.md")


@cli.command()
def validate() -> None:
    """Validate a network or case (not yet implemented)."""
    click.echo("Not yet implemented — see build/build_order.md")


if __name__ == "__main__":
    cli()
```

### Step 4: Install in editable mode

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Step 5: Verify install works

```bash
python -m pdde --help
```

Expected output: click's help text showing `run` and `validate` subcommands.

### Step 6: Create the tests directory

```bash
mkdir -p tests
touch tests/__init__.py
touch tests/conftest.py
```

In `tests/conftest.py`:

```python
"""Shared pytest fixtures."""

from pathlib import Path
import pytest


@pytest.fixture
def repo_root() -> Path:
    return Path(__file__).parent.parent


@pytest.fixture
def network_path(repo_root: Path) -> Path:
    return repo_root / "networks" / "hf_ed_discharge_v0.yaml"


@pytest.fixture
def sample_case_path(repo_root: Path) -> Path:
    return repo_root / "examples" / "sample_case_HF-001.json"
```

### Step 7: First smoke test

Create `tests/test_smoke.py`:

```python
"""Smoke test: package imports and CLI runs."""

import subprocess


def test_package_imports():
    import pdde
    assert pdde.__version__ == "0.1.0"


def test_cli_help_works():
    result = subprocess.run(["python", "-m", "pdde", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "PDDE" in result.stdout
```

Run:

```bash
pytest tests/test_smoke.py -v
```

Both tests should pass.

### Step 8: Git init and first commit

```bash
git init
git add .
git commit -m "Initial scaffolding: pyproject, CLI stub, smoke test"
```

Also create `.gitignore`:

```
.venv/
__pycache__/
*.pyc
.pytest_cache/
.coverage
*.egg-info/
dist/
build/
logs/
.env
.DS_Store
```

---

## After step 8

Report back to user:

> Project skeleton complete. Smoke tests pass. Ready to start Task 0.1 (Pydantic data models). See `build/build_order.md`.

Then wait for user direction. Do **not** automatically proceed to Task 0.1 unless instructed.

---

## Why stop here?

This is the first checkpoint. The project reviewer wants visibility into early progress before you build the data models. The skeleton is independently verifiable, and any tooling issues (Python version, venv, click installed correctly, pytest discovered) will surface here, not 10 tasks deeper.

If anything fails in steps 1-8, surface it immediately rather than working around it.

---

## What "ready" looks like

After step 8:
- `python -m pdde --help` works
- `pytest tests/test_smoke.py -v` shows 2 passed
- Git log shows one commit
- `tree -L 2` shows:

```
.
├── CLAUDE.md
├── README.md
├── pyproject.toml
├── pdde/
│   ├── __init__.py
│   └── __main__.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_smoke.py
├── docs/...
├── networks/...
├── examples/...
├── specs/...
├── prompts/...
├── tests/...
└── build/...
```

(The `docs`, `networks`, `examples`, `specs`, `prompts`, and `build` directories are the build package contents copied into the repo.)
