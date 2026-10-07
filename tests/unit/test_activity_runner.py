from pathlib import Path

from ai_verify.core.execution import ExecutionRequest
from ai_verify.core.models import EvidenceStatus
from ai_verify.verification.activity_runner import (
    VerificationActivityRequest,
    VerificationActivityRunner,
)


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
        description=f"Verification activity: {activity_id}",
        success_status=EvidenceStatus.SUPPORTS,
        failure_status=EvidenceStatus.INCONCLUSIVE,
    )


def test_runner_executes_single_activity(
    tmp_path: Path,
) -> None:
    activities = (
        make_activity(
            "positive-path",
            "EV-ACT-001",
            (
                "python",
                "-c",
                "print('positive')",
            ),
        ),
    )

    evidence = VerificationActivityRunner().run(
        activities,
        tmp_path,
    )

    assert len(evidence) == 1
    assert evidence[0].evidence_id == "EV-ACT-001"
    assert evidence[0].status == EvidenceStatus.SUPPORTS


def test_runner_executes_multiple_activities(
    tmp_path: Path,
) -> None:
    activities = (
        make_activity(
            "positive-path",
            "EV-ACT-002",
            (
                "python",
                "-c",
                "print('positive')",
            ),
        ),
        make_activity(
            "negative-path",
            "EV-ACT-003",
            (
                "python",
                "-c",
                "print('negative')",
            ),
        ),
        make_activity(
            "edge-case",
            "EV-ACT-004",
            (
                "python",
                "-c",
                "print('edge')",
            ),
        ),
    )

    evidence = VerificationActivityRunner().run(
        activities,
        tmp_path,
    )

    assert len(evidence) == 3
    assert [item.evidence_id for item in evidence] == [
        "EV-ACT-002",
        "EV-ACT-003",
        "EV-ACT-004",
    ]


def test_runner_preserves_activity_order(
    tmp_path: Path,
) -> None:
    activities = (
        make_activity(
            "edge-case",
            "EV-ACT-005",
            ("python", "-c", "print('edge')"),
        ),
        make_activity(
            "positive-path",
            "EV-ACT-006",
            ("python", "-c", "print('positive')"),
        ),
    )

    evidence = VerificationActivityRunner().run(
        activities,
        tmp_path,
    )

    assert [item.evidence_id for item in evidence] == [
        "EV-ACT-005",
        "EV-ACT-006",
    ]


def test_runner_returns_empty_tuple_for_no_activities(
    tmp_path: Path,
) -> None:
    evidence = VerificationActivityRunner().run(
        (),
        tmp_path,
    )

    assert evidence == ()


def test_failed_execution_does_not_become_contradiction_automatically(
    tmp_path: Path,
) -> None:
    activity = make_activity(
        "failure-case",
        "EV-ACT-007",
        (
            "python",
            "-c",
            "raise SystemExit(1)",
        ),
    )

    evidence = VerificationActivityRunner().run(
        (activity,),
        tmp_path,
    )

    assert evidence[0].status == EvidenceStatus.INCONCLUSIVE