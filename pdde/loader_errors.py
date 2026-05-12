"""Shared loader exceptions and formatting helpers."""

from __future__ import annotations

from pydantic import ValidationError


class LoaderError(ValueError):
    """Raised when an input file cannot be read, parsed, or validated."""


def validation_summary(exc: ValidationError) -> str:
    first = exc.errors()[0] if exc.errors() else {}
    loc = ".".join(str(part) for part in first.get("loc", ())) or "<root>"
    msg = first.get("msg", str(exc))
    return f"{loc}: {msg}"

