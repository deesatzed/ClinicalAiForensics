"""Shared base types for PDDE Pydantic models."""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, StringConstraints


NonEmptyString = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
JsonObject = dict[str, Any]


class StrictModel(BaseModel):
    """Base model with explicit fields only."""

    model_config = ConfigDict(extra="forbid")
