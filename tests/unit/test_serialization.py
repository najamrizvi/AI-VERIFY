from pathlib import Path

from ai_verify.core.models import (
    Evidence,
    EvidenceStatus,
    EvidenceType,
)
from ai_verify.core.decision import determine_verification
from ai_verify.core.run_package import VerificationRun
from ai_verify.reporting.report import VerificationReportBuilder
from ai_verify.reporting.serialization import serialize_report


def make_report():
    evidence = (
        Evidence(
            evidence_id="EV-SERIAL-001",
            status=EvidenceStatus.SUPPORTS,
            description="Serialization test evidence",
            source="tests/test_example.py",
            evidence_type=EvidenceType.RUNTIME,
            observation="Execution completed successfully.",
            execution_id="EXEC-SERIAL-001",
        ),
    )

    decision = determine_verification(
        evidence,
        required_evidence_count=1,
    )

    run = VerificationRun(
        run_id="RUN-SERIAL-001",
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
            "source": "BUILD-14-test",
        },
    )

    return VerificationReportBuilder().build(run)


def test_serialization_returns_dictionary() -> None:
    report = make_report()

    serialized = serialize_report(report)

    assert isinstance(serialized, dict)


def test_serialization_preserves_report_fields() -> None:
    report = make_report()

    serialized = serialize_report(report)

    assert serialized["run_id"] == report.run_id
    assert serialized["requirement"] == report.requirement
    assert serialized["invariant"] == report.invariant
    assert serialized["status"] == report.status
    assert serialized["decision_rule"] == report.decision_rule
    assert serialized["rationale"] == report.rationale


def test_serialization_preserves_scope_and_plan() -> None:
    report = make_report()

    serialized = serialize_report(report)

    assert serialized["scope"] == report.scope
    assert serialized["verification_plan"] == report.verification_plan


def test_serialization_preserves_evidence() -> None:
    report = make_report()

    serialized = serialize_report(report)

    assert serialized["evidence"] == [
        {
            "evidence_id": "EV-SERIAL-001",
            "status": "SUPPORTS",
            "description": "Serialization test evidence",
            "source": "tests/test_example.py",
            "evidence_type": "RUNTIME",
            "observation": "Execution completed successfully.",
            "execution_id": "EXEC-SERIAL-001",
        }
    ]


def test_serialization_preserves_provenance() -> None:
    report = make_report()

    serialized = serialize_report(report)

    assert serialized["provenance"] == report.provenance
