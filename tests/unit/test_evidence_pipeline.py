from pathlib import Path

from ai_verify.core.execution import ExecutionRequest, ExecutionStatus
from ai_verify.core.models import EvidenceStatus, EvidenceType
from ai_verify.verification.evidence_pipeline import EvidencePipeline


def make_request(command: tuple[str, ...]) -> ExecutionRequest:
    return ExecutionRequest(
        command=command,
        working_directory=".",
        timeout_seconds=5,
    )


def test_successful_execution_becomes_supporting_evidence(
    tmp_path: Path,
) -> None:
    evidence = EvidencePipeline().execute_and_collect(
        make_request(
            (
                "python",
                "-c",
                "print('verification passed')",
            )
        ),
        tmp_path,
        evidence_id="EV-PIPE-001",
        description="Positive verification activity.",
        success_status=EvidenceStatus.SUPPORTS,
        failure_status=EvidenceStatus.CONTRADICTS,
    )

    assert evidence.status == EvidenceStatus.SUPPORTS
    assert evidence.evidence_type == EvidenceType.RUNTIME
    assert "verification passed" in evidence.observation


def test_failed_execution_remains_inconclusive(
    tmp_path: Path,
) -> None:
    evidence = EvidencePipeline().execute_and_collect(
        make_request(
            (
                "python",
                "-c",
                "raise SystemExit(1)",
            )
        ),
        tmp_path,
        evidence_id="EV-PIPE-002",
        description="Execution-failure activity.",
        success_status=EvidenceStatus.SUPPORTS,
        failure_status=EvidenceStatus.CONTRADICTS,
    )

    assert evidence.status == EvidenceStatus.INCONCLUSIVE


def test_failed_execution_can_remain_inconclusive(
    tmp_path: Path,
) -> None:
    evidence = EvidencePipeline().execute_and_collect(
        make_request(
            (
                "python",
                "-c",
                "raise SystemExit(2)",
            )
        ),
        tmp_path,
        evidence_id="EV-PIPE-003",
        description="Environment-sensitive activity.",
        success_status=EvidenceStatus.SUPPORTS,
        failure_status=EvidenceStatus.INCONCLUSIVE,
    )

    assert evidence.status == EvidenceStatus.INCONCLUSIVE


def test_timeout_becomes_inconclusive(
    tmp_path: Path,
) -> None:
    evidence = EvidencePipeline().execute_and_collect(
        ExecutionRequest(
            command=(
                "python",
                "-c",
                "import time; time.sleep(2)",
            ),
            working_directory=".",
            timeout_seconds=0.1,
        ),
        tmp_path,
        evidence_id="EV-PIPE-004",
        description="Timeout activity.",
        success_status=EvidenceStatus.SUPPORTS,
        failure_status=EvidenceStatus.CONTRADICTS,
    )

    assert evidence.status == EvidenceStatus.INCONCLUSIVE


def test_pipeline_preserves_evidence_metadata(
    tmp_path: Path,
) -> None:
    evidence = EvidencePipeline().execute_and_collect(
        make_request(
            (
                "python",
                "-c",
                "print('metadata check')",
            )
        ),
        tmp_path,
        evidence_id="EV-PIPE-005",
        description="Metadata verification.",
        success_status=EvidenceStatus.SUPPORTS,
        failure_status=EvidenceStatus.CONTRADICTS,
    )

    assert evidence.evidence_id == "EV-PIPE-005"
    assert evidence.description == "Metadata verification."
    assert evidence.source == tmp_path.resolve().as_posix()
    assert evidence.evidence_type == EvidenceType.RUNTIME
    assert evidence.execution_id is None


def test_pipeline_does_not_make_final_verification_decision(
    tmp_path: Path,
) -> None:
    evidence = EvidencePipeline().execute_and_collect(
        make_request(
            (
                "python",
                "-c",
                "print('support')",
            )
        ),
        tmp_path,
        evidence_id="EV-PIPE-006",
        description="Decision-boundary verification.",
        success_status=EvidenceStatus.SUPPORTS,
        failure_status=EvidenceStatus.CONTRADICTS,
    )

    assert evidence.status == EvidenceStatus.SUPPORTS
    assert not hasattr(evidence, "verification_status")