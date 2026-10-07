from pathlib import Path

import pytest

from ai_verify.core.execution import (
    ExecutionResult,
    ExecutionStatus,
)
from ai_verify.core.models import EvidenceStatus, EvidenceType
from ai_verify.verification.evidence_adapter import (
    ExecutionEvidenceAdapter,
)


def make_execution(
    *,
    status: ExecutionStatus = ExecutionStatus.COMPLETED,
    exit_code: int | None = 0,
    stdout: str = "success",
    stderr: str = "",
) -> ExecutionResult:
    return ExecutionResult(
        command=("python", "-c", "print('success')"),
        working_directory=Path("/repo").as_posix(),
        status=status,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        timeout_seconds=5,
    )


def test_successful_execution_uses_success_status() -> None:
    observation = ExecutionEvidenceAdapter().adapt(
        make_execution(),
        evidence_id="EV-001",
        description="Positive-path verification.",
        success_status=EvidenceStatus.SUPPORTS,
        failure_status=EvidenceStatus.CONTRADICTS,
    )

    assert observation.status == EvidenceStatus.SUPPORTS


def test_failed_execution_uses_explicit_failure_status() -> None:
    observation = ExecutionEvidenceAdapter().adapt(
        make_execution(exit_code=1, stdout="failure"),
        evidence_id="EV-002",
        description="Negative-path verification.",
        success_status=EvidenceStatus.SUPPORTS,
        failure_status=EvidenceStatus.CONTRADICTS,
    )

    assert observation.status == EvidenceStatus.CONTRADICTS


def test_failure_status_can_be_inconclusive() -> None:
    observation = ExecutionEvidenceAdapter().adapt(
        make_execution(exit_code=1),
        evidence_id="EV-003",
        description="Environment-sensitive verification.",
        success_status=EvidenceStatus.SUPPORTS,
        failure_status=EvidenceStatus.INCONCLUSIVE,
    )

    assert observation.status == EvidenceStatus.INCONCLUSIVE


def test_timeout_is_always_inconclusive() -> None:
    observation = ExecutionEvidenceAdapter().adapt(
        make_execution(
            status=ExecutionStatus.TIMED_OUT,
            exit_code=None,
            stdout="",
        ),
        evidence_id="EV-004",
        description="Timeout verification.",
        success_status=EvidenceStatus.SUPPORTS,
        failure_status=EvidenceStatus.CONTRADICTS,
    )

    assert observation.status == EvidenceStatus.INCONCLUSIVE


def test_failed_execution_is_not_automatically_not_verified() -> None:
    observation = ExecutionEvidenceAdapter().adapt(
        make_execution(exit_code=2),
        evidence_id="EV-005",
        description="Controlled execution.",
        success_status=EvidenceStatus.SUPPORTS,
        failure_status=EvidenceStatus.INCONCLUSIVE,
    )

    assert observation.status == EvidenceStatus.INCONCLUSIVE


def test_runtime_evidence_type_is_preserved() -> None:
    observation = ExecutionEvidenceAdapter().adapt(
        make_execution(),
        evidence_id="EV-006",
        description="Runtime verification.",
        success_status=EvidenceStatus.SUPPORTS,
        failure_status=EvidenceStatus.CONTRADICTS,
    )

    assert observation.evidence_type == EvidenceType.RUNTIME


def test_execution_output_is_preserved_in_observation() -> None:
    observation = ExecutionEvidenceAdapter().adapt(
        make_execution(
            stdout="expected output",
            stderr="warning output",
        ),
        evidence_id="EV-007",
        description="Output verification.",
        success_status=EvidenceStatus.SUPPORTS,
        failure_status=EvidenceStatus.CONTRADICTS,
    )

    assert "expected output" in observation.observation
    assert "warning output" in observation.observation


def test_evidence_id_is_required() -> None:
    with pytest.raises(ValueError, match="Evidence ID"):
        ExecutionEvidenceAdapter().adapt(
            make_execution(),
            evidence_id=" ",
            description="Verification.",
            success_status=EvidenceStatus.SUPPORTS,
            failure_status=EvidenceStatus.CONTRADICTS,
        )


def test_description_is_required() -> None:
    with pytest.raises(ValueError, match="Evidence description"):
        ExecutionEvidenceAdapter().adapt(
            make_execution(),
            evidence_id="EV-008",
            description=" ",
            success_status=EvidenceStatus.SUPPORTS,
            failure_status=EvidenceStatus.CONTRADICTS,
        )