from pathlib import Path

from ai_verify.core.execution import ExecutionRequest
from ai_verify.core.models import (
    EvidenceStatus,
    VerificationStatus,
)
from ai_verify.verification.activity_runner import (
    VerificationActivityRequest,
)
from ai_verify.verification.service import VerificationService


def make_activity(
    activity_id: str,
    evidence_id: str,
    command: tuple[str, ...],
) -> VerificationActivityRequest:
    return VerificationActivityRequest(
        activity_id=activity_id,
        execution=ExecutionRequest(
            command=command,
            working_directory=".",
            timeout_seconds=5,
        ),
        evidence_id=evidence_id,
        description=f"End-to-end activity: {activity_id}",
        success_status=EvidenceStatus.SUPPORTS,
        failure_status=EvidenceStatus.INCONCLUSIVE,
    )


def test_complete_verification_flow(
    tmp_path: Path,
) -> None:
    (tmp_path / "example.py").write_text(
        "print('example')\n",
        encoding="utf-8",
    )

    activities = (
        make_activity(
            "positive-path",
            "EV-E2E-001",
            ("python", "-c", "print('positive')"),
        ),
        make_activity(
            "negative-path",
            "EV-E2E-002",
            ("python", "-c", "print('negative')"),
        ),
        make_activity(
            "edge-case",
            "EV-E2E-003",
            ("python", "-c", "print('edge')"),
        ),
    )

    run, report, serialized = VerificationService().verify(
        run_id="RUN-E2E-001",
        requirement="The requirement must be satisfied.",
        invariant="The required invariant holds.",
        repository_root=tmp_path,
        activities=activities,
        provenance={"source": "BUILD-15"},
    )

    assert run.decision.status == VerificationStatus.VERIFIED
    assert report.status == "VERIFIED"
    assert serialized["status"] == "VERIFIED"
    assert len(run.evidence) == 3


def test_end_to_end_partial_when_evidence_is_missing(
    tmp_path: Path,
) -> None:
    run, report, serialized = VerificationService().verify(
        run_id="RUN-E2E-002",
        requirement="Requirement",
        invariant="Invariant",
        repository_root=tmp_path,
        activities=(),
        provenance={"source": "BUILD-15"},
    )

    assert run.decision.status == VerificationStatus.PARTIALLY_VERIFIED
    assert report.status == "PARTIALLY VERIFIED"
    assert serialized["status"] == "PARTIALLY VERIFIED"
    assert serialized["evidence"] == []


def test_end_to_end_provenance_is_preserved(
    tmp_path: Path,
) -> None:
    activities = (
        make_activity(
            "positive-path",
            "EV-E2E-004",
            ("python", "-c", "print('positive')"),
        ),
        make_activity(
            "negative-path",
            "EV-E2E-005",
            ("python", "-c", "print('negative')"),
        ),
        make_activity(
            "edge-case",
            "EV-E2E-006",
            ("python", "-c", "print('edge')"),
        ),
    )

    provenance = {
        "source": "BUILD-15",
        "purpose": "integration-test",
    }

    run, report, serialized = VerificationService().verify(
        run_id="RUN-E2E-003",
        requirement="Requirement",
        invariant="Invariant",
        repository_root=tmp_path,
        activities=activities,
        provenance=provenance,
    )

    assert run.provenance == provenance
    assert report.provenance == provenance
    assert serialized["provenance"] == provenance
