from pathlib import Path

from ai_verify.core.models import (
    Evidence,
    EvidenceStatus,
    EvidenceType,
    VerificationStatus,
)
from ai_verify.repository.analyzer import (
    RepositoryAnalysis,
    RepositoryFile,
)
from ai_verify.verification.planner import VerificationPlanner
from ai_verify.verification.run import VerificationRunBuilder
from ai_verify.verification.scope import VerificationScopeBuilder


def make_plan():
    analysis = RepositoryAnalysis(
        root=Path("/repo"),
        python_files=(
            RepositoryFile(
                relative_path="src/service.py",
                absolute_path=Path("/repo/src/service.py"),
            ),
            RepositoryFile(
                relative_path="tests/test_service.py",
                absolute_path=Path("/repo/tests/test_service.py"),
            ),
        ),
    )

    scope = VerificationScopeBuilder().build(
        "A requirement.",
        "an invariant",
        analysis,
    )

    return VerificationPlanner().build(
        "A requirement.",
        "an invariant",
        scope,
    )


def make_evidence(
    evidence_id: str,
    status: EvidenceStatus,
) -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        status=status,
        description="Verification evidence.",
        source="/repo",
        evidence_type=EvidenceType.RUNTIME,
        observation="Observed behavior.",
    )


def test_builder_creates_verification_run() -> None:
    plan = make_plan()

    run = VerificationRunBuilder().build(
        run_id="RUN-001",
        requirement="A requirement.",
        invariant="an invariant",
        plan=plan,
        evidence=(
            make_evidence("EV-001", EvidenceStatus.SUPPORTS),
            make_evidence("EV-002", EvidenceStatus.SUPPORTS),
            make_evidence("EV-003", EvidenceStatus.SUPPORTS),
        ),
        provenance={"source": "test"},
    )

    assert run.run_id == "RUN-001"
    assert run.requirement == "A requirement."
    assert run.invariant == "an invariant"


def test_builder_uses_deterministic_decision_engine() -> None:
    plan = make_plan()

    run = VerificationRunBuilder().build(
        run_id="RUN-002",
        requirement="A requirement.",
        invariant="an invariant",
        plan=plan,
        evidence=(
            make_evidence("EV-001", EvidenceStatus.SUPPORTS),
            make_evidence("EV-002", EvidenceStatus.SUPPORTS),
            make_evidence("EV-003", EvidenceStatus.SUPPORTS),
        ),
        provenance={"source": "test"},
    )

    assert run.decision.status == VerificationStatus.VERIFIED
    assert run.decision.rule == "SUFFICIENT_SUPPORTING_EVIDENCE"


def test_contradiction_remains_authoritative() -> None:
    plan = make_plan()

    run = VerificationRunBuilder().build(
        run_id="RUN-003",
        requirement="A requirement.",
        invariant="an invariant",
        plan=plan,
        evidence=(
            make_evidence("EV-001", EvidenceStatus.SUPPORTS),
            make_evidence("EV-002", EvidenceStatus.SUPPORTS),
            make_evidence("EV-003", EvidenceStatus.CONTRADICTS),
        ),
        provenance={"source": "test"},
    )

    assert run.decision.status == VerificationStatus.NOT_VERIFIED
    assert run.decision.rule == "CONTRADICTION_WINS"


def test_insufficient_evidence_becomes_partial() -> None:
    plan = make_plan()

    run = VerificationRunBuilder().build(
        run_id="RUN-004",
        requirement="A requirement.",
        invariant="an invariant",
        plan=plan,
        evidence=(
            make_evidence("EV-001", EvidenceStatus.SUPPORTS),
        ),
        provenance={"source": "test"},
    )

    assert run.decision.status == VerificationStatus.PARTIALLY_VERIFIED
    assert (
        run.decision.rule
        == "INSUFFICIENT_OR_INCONCLUSIVE_EVIDENCE"
    )


def test_scope_is_preserved_in_run() -> None:
    plan = make_plan()

    run = VerificationRunBuilder().build(
        run_id="RUN-005",
        requirement="A requirement.",
        invariant="an invariant",
        plan=plan,
        evidence=(),
        provenance={"source": "test"},
    )

    paths = {
        item["relative_path"]
        for item in run.scope["files"]
    }

    assert paths == {
        "src/service.py",
        "tests/test_service.py",
    }


def test_verification_plan_is_preserved() -> None:
    plan = make_plan()

    run = VerificationRunBuilder().build(
        run_id="RUN-006",
        requirement="A requirement.",
        invariant="an invariant",
        plan=plan,
        evidence=(),
        provenance={"source": "test"},
    )

    assert len(run.verification_plan["activities"]) == 3
    assert (
        run.verification_plan["required_evidence_count"]
        == 3
    )


def test_provenance_is_preserved() -> None:
    plan = make_plan()

    provenance = {
        "source": "build-10-test",
        "tool": "ai-verify",
    }

    run = VerificationRunBuilder().build(
        run_id="RUN-007",
        requirement="A requirement.",
        invariant="an invariant",
        plan=plan,
        evidence=(),
        provenance=provenance,
    )

    assert run.provenance == provenance


def test_evidence_is_preserved_without_modification() -> None:
    plan = make_plan()

    evidence = (
        make_evidence("EV-001", EvidenceStatus.SUPPORTS),
    )

    run = VerificationRunBuilder().build(
        run_id="RUN-008",
        requirement="A requirement.",
        invariant="an invariant",
        plan=plan,
        evidence=evidence,
        provenance={"source": "test"},
    )

    assert run.evidence == evidence