from dataclasses import dataclass
from typing import Any

from .models import DecisionResult, Evidence


RUN_PACKAGE_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class VerificationRun:
    run_id: str
    requirement: str
    invariant: str
    scope: dict[str, Any]
    verification_plan: dict[str, Any]
    evidence: tuple[Evidence, ...]
    decision: DecisionResult
    provenance: dict[str, Any]
    schema_version: str = RUN_PACKAGE_SCHEMA_VERSION
