"""Clinical Decision Episode file loader."""

from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path

from pydantic import ValidationError

from .input_models import ClinicalDecisionEpisode
from .loader_errors import LoaderError, validation_summary


def load_cde(path: str | Path) -> ClinicalDecisionEpisode:
    """Read and validate a Clinical Decision Episode JSON file."""

    cde_path = Path(path)
    try:
        payload = json.loads(cde_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise LoaderError(f"CDE file not found: {cde_path}") from exc
    except IsADirectoryError as exc:
        raise LoaderError(f"CDE path is a directory: {cde_path}") from exc
    except OSError as exc:
        raise LoaderError(f"Could not read CDE file {cde_path}: {exc}") from exc
    except JSONDecodeError as exc:
        raise LoaderError(f"Could not parse CDE JSON {cde_path}: line {exc.lineno}: {exc.msg}") from exc

    if not isinstance(payload, dict):
        raise LoaderError(f"CDE file must contain a JSON object: {cde_path}")

    try:
        return ClinicalDecisionEpisode.model_validate(payload)
    except ValidationError as exc:
        raise LoaderError(f"CDE validation failed for {cde_path}: {validation_summary(exc)}") from exc
