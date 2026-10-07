from pathlib import Path

from ai_verify.core.decision import determine_verification
from ai_verify.core.models import (
    Evidence,
    EvidenceStatus,
    EvidenceType,
)
from ai_verify.core.run_package import VerificationRun
from ai_verify.reporting.report import (
    VerificationReportBuilder,
)
from ai_verify.verification.planner import (
    VerificationActivity,
    VerificationPlan,
)
from ai_verify.verification.scope import (
    ScopeFile,
    VerificationScope,
)


def make_run(
    *,
    status: EvidenceStatus = EvidenceStatus.SUPPORTS,
) -> VerificationRun:
    evidence = (
        Evidence(
            evidence_id="EV-REPORT-001",
            status=status,
            description="Report test evidence",
            source="tests/test_example.py",
            evidence_type=EvidenceType.RUNTIME,
            observation="Execution completed successfully.",
            execution_id="EXEC-001",
        ),
    )

    decision = determine_verification(
        evidence,
        required_evidence_count=1,
    )

    scope = VerificationScope(
        requirement="Requirement",
        invariant="Invariant",
        files=(
            ScopeFile(
                relative_path="src/example.py",
                absolute_path=Path("src/example.py"),
                role="source",
            ),
        ),
    )

    plan = VerificationPlan(
        requirement="Requirement",
        invariant="Invariant",
        scope=scope,
        activities=(
            VerificationActivity(
                activity_id="positive-path",
                category="positive",
                objective="Verify valid behavior.",
            ),
        ),
        required_evidence_count=1,
    )

    return VerificationRun(
        run_id="RUN-REPORT-001",
        requirement="Requirement",
        invariant="Invariant",
        scope={
            "files": [
                {
                    "relative_path": "src/example.py",
                    "role": "source",
                },
            ],
        },
        verification_plan={
            "activities": [
                {
                    "activity_id": "positive-path",
                    "category": "positive",
                    "objective": "Verify valid behavior.",
                    "required": True,
                },
            ],
            "required_evidence_count": 1,
        },
        evidence=evidence,
        decision=decision,
        provenance={
            "source": "BUILD-13-test",
        },
    )


def test_report_preserves_authoritative_decision() -> None:
    run = make_run()

    report = VerificationReportBuilder().build(run)

    assert report.status == run.decision.status.value
    assert report.decision_rule == run.decision.rule
    assert report.rationale == run.decision.rationale


def test_report_preserves_requirement_and_invariant() -> None:
    run = make_run()

    report = VerificationReportBuilder().build(run)

    assert report.requirement == run.requirement
    assert report.invariant == run.invariant


def test_report_preserves_scope_and_plan() -> None:
    run = make_run()

    report = VerificationReportBuilder().build(run)

    assert report.scope == run.scope
    assert report.verification_plan == run.verification_plan


def test_report_preserves_evidence_details() -> None:
    run = make_run()

    report = VerificationReportBuilder().build(run)

    assert len(report.evidence) == 1
    assert report.evidence[0] == {
        "evidence_id": "EV-REPORT-001",
        "status": "SUPPORTS",
        "description": "Report test evidence",
        "source": "tests/test_example.py",
        "evidence_type": "RUNTIME",
        "observation": "Execution completed successfully.",
        "execution_id": "EXEC-001",
    }


def test_report_preserves_provenance() -> None:
    run = make_run()

    report = VerificationReportBuilder().build(run)

    assert report.run_id == run.run_id
    assert report.provenance == run.provenance
