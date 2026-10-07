from dataclasses import dataclass
from enum import Enum


class ExecutionStatus(str, Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"


@dataclass(frozen=True)
class ExecutionRequest:
    command: tuple[str, ...]
    working_directory: str
    timeout_seconds: float


@dataclass(frozen=True)
class ExecutionResult:
    command: tuple[str, ...]
    working_directory: str
    status: ExecutionStatus
    exit_code: int | None
    stdout: str
    stderr: str
    timeout_seconds: float