from pathlib import Path

from ai_verify.core.execution import ExecutionRequest
from ai_verify.core.models import EvidenceStatus, VerificationStatus
from ai_verify.verification.activity_runner import (
    VerificationActivityRequest,
)
from ai_verify.verification.orchestrator import (
    VerificationOrchestrator,
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


def test_orchestrator_builds_verification_run(
    tmp_path: Path,
) -> None:
    activities = (
        make_activity(
            "positive-path",
            "EV-ORCH-001",
            ("python", "-c", "print('positive')"),
        ),
        make_activity(
            "negative-path",
            "EV-ORCH-002",
            ("python", "-c", "print('negative')"),
        ),
        make_activity(
            "edge-case",
            "EV-ORCH-003",
            ("python", "-c", "print('edge')"),
        ),
    )

    run = VerificationOrchestrator().run(
        run_id="RUN-001",
        requirement="The requirement must be satisfied.",
        invariant="The required invariant holds.",
        repository_root=tmp_path,
        activities=activities,
        provenance={"source": "BUILD-12-test"},
    )

    assert run.run_id == "RUN-001"
    assert run.requirement == "The requirement must be satisfied."
    assert run.invariant == "The required invariant holds."
    assert run.decision.status == VerificationStatus.VERIFIED


def test_orchestrator_preserves_scope(
    tmp_path: Path,
) -> None:
    (tmp_path / "app.py").write_text(
        "print('app')\n",
        encoding="utf-8",
    )

    activities = (
        make_activity(
            "positive-path",
            "EV-ORCH-004",
            ("python", "-c", "print('positive')"),
        ),
        make_activity(
            "negative-path",
            "EV-ORCH-005",
            ("python", "-c", "print('negative')"),
        ),
        make_activity(
            "edge-case",
            "EV-ORCH-006",
            ("python", "-c", "print('edge')"),
        ),
    )

    run = VerificationOrchestrator().run(
        run_id="RUN-002",
        requirement="Requirement",
        invariant="Invariant",
        repository_root=tmp_path,
        activities=activities,
        provenance={},
    )

    paths = [
        item["relative_path"]
        for item in run.scope["files"]
    ]

    assert "app.py" in paths


def test_orchestrator_preserves_evidence_order(
    tmp_path: Path,
) -> None:
    activities = (
        make_activity(
            "edge-case",
            "EV-ORCH-007",
            ("python", "-c", "print('edge')"),
        ),
        make_activity(
            "positive-path",
            "EV-ORCH-008",
            ("python", "-c", "print('positive')"),
        ),
        make_activity(
            "negative-path",
            "EV-ORCH-009",
            ("python", "-c", "print('negative')"),
        ),
    )

    run = VerificationOrchestrator().run(
        run_id="RUN-003",
        requirement="Requirement",
        invariant="Invariant",
        repository_root=tmp_path,
        activities=activities,
        provenance={},
    )

    assert [item.evidence_id for item in run.evidence] == [
        "EV-ORCH-007",
        "EV-ORCH-008",
        "EV-ORCH-009",
    ]


def test_orchestrator_preserves_provenance(
    tmp_path: Path,
) -> None:
    activities = (
        make_activity(
            "positive-path",
            "EV-ORCH-010",
            ("python", "-c", "print('positive')"),
        ),
        make_activity(
            "negative-path",
            "EV-ORCH-011",
            ("python", "-c", "print('negative')"),
        ),
        make_activity(
            "edge-case",
            "EV-ORCH-012",
            ("python", "-c", "print('edge')"),
        ),
    )

    provenance = {
        "source": "BUILD-12",
        "operator": "test",
    }

    run = VerificationOrchestrator().run(
        run_id="RUN-004",
        requirement="Requirement",
        invariant="Invariant",
        repository_root=tmp_path,
        activities=activities,
        provenance=provenance,
    )

    assert run.provenance == provenance


def test_orchestrator_without_evidence_is_partial(
    tmp_path: Path,
) -> None:
    run = VerificationOrchestrator().run(
        run_id="RUN-005",
        requirement="Requirement",
        invariant="Invariant",
        repository_root=tmp_path,
        activities=(),
        provenance={},
    )

    assert run.evidence == ()
    assert run.decision.status == VerificationStatus.PARTIALLY_VERIFIED
