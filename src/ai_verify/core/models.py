from dataclasses import dataclass
from enum import Enum


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    PARTIALLY_VERIFIED = "PARTIALLY VERIFIED"
    NOT_VERIFIED = "NOT VERIFIED"


class EvidenceStatus(str, Enum):
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    INCONCLUSIVE = "INCONCLUSIVE"


class EvidenceType(str, Enum):
    STATIC = "STATIC"
    TEST = "TEST"
    RUNTIME = "RUNTIME"
    STRUCTURAL = "STRUCTURAL"


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    status: EvidenceStatus
    description: str
    source: str
    evidence_type: EvidenceType = EvidenceType.RUNTIME
    observation: str = ""
    execution_id: str | None = None


@dataclass(frozen=True)
class DecisionResult:
    status: VerificationStatus
    rule: str
    rationale: str