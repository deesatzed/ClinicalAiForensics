"""Domain pack file loader."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError
from yaml import YAMLError

from .input_models import DomainPack
from .loader_errors import LoaderError, validation_summary


def load_domain_pack(path: str | Path) -> DomainPack:
    """Read and validate a domain pack YAML file."""

    domain_path = Path(path)
    try:
        payload = yaml.safe_load(domain_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise LoaderError(f"Domain pack file not found: {domain_path}") from exc
    except IsADirectoryError as exc:
        raise LoaderError(f"Domain pack path is a directory: {domain_path}") from exc
    except OSError as exc:
        raise LoaderError(f"Could not read domain pack file {domain_path}: {exc}") from exc
    except YAMLError as exc:
        raise LoaderError(f"Could not parse domain pack YAML {domain_path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise LoaderError(f"Domain pack file must contain a YAML object: {domain_path}")

    try:
        return DomainPack.model_validate(payload)
    except ValidationError as exc:
        raise LoaderError(
            f"Domain pack validation failed for {domain_path}: {validation_summary(exc)}"
        ) from exc
