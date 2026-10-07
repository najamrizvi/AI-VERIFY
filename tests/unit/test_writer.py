from pathlib import Path

from ai_verify.core.decision import determine_verification
from ai_verify.core.models import (
    Evidence,
    EvidenceStatus,
    EvidenceType,
)
from ai_verify.core.run_package import VerificationRun
from ai_verify.reporting.report import VerificationReportBuilder
from ai_verify.reporting.writer import ReportWriter


def make_report():
    evidence = (
        Evidence(
            evidence_id="EV-WRITER-001",
            status=EvidenceStatus.SUPPORTS,
            description="Writer test evidence",
            source="tests/test_writer.py",
            evidence_type=EvidenceType.RUNTIME,
            observation="Execution completed successfully.",
            execution_id="EXEC-WRITER-001",
        ),
    )

    decision = determine_verification(
        evidence,
        required_evidence_count=1,
    )

    run = VerificationRun(
        run_id="RUN-WRITER-001",
        requirement="The requirement must be satisfied.",
        invariant="The required invariant holds.",
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
            "source": "BUILD-17-test",
        },
    )

    return VerificationReportBuilder().build(run)


def test_write_json_creates_report_file(tmp_path: Path) -> None:
    report = make_report()

    output_path = ReportWriter().write_json(
        report,
        tmp_path / "reports",
    )

    assert output_path == tmp_path / "reports" / "RUN-WRITER-001.json"
    assert output_path.exists()


def test_write_json_preserves_serialized_report(
    tmp_path: Path,
) -> None:
    import json

    report = make_report()

    output_path = ReportWriter().write_json(
        report,
        tmp_path / "reports",
    )

    payload = json.loads(
        output_path.read_text(encoding="utf-8")
    )

    assert payload["run_id"] == report.run_id
    assert payload["requirement"] == report.requirement
    assert payload["invariant"] == report.invariant
    assert payload["status"] == report.status
    assert payload["decision_rule"] == report.decision_rule
    assert payload["evidence"][0]["evidence_id"] == (
        "EV-WRITER-001"
    )


def test_write_markdown_creates_report_file(
    tmp_path: Path,
) -> None:
    report = make_report()

    output_path = ReportWriter().write_markdown(
        report,
        tmp_path / "reports",
    )

    assert output_path == tmp_path / "reports" / "RUN-WRITER-001.md"
    assert output_path.exists()


def test_write_markdown_contains_required_sections(
    tmp_path: Path,
) -> None:
    report = make_report()

    output_path = ReportWriter().write_markdown(
        report,
        tmp_path / "reports",
    )

    content = output_path.read_text(encoding="utf-8")

    assert "# AI-VERIFY Verification Report" in content
    assert "## Verification Result" in content
    assert "## Requirement" in content
    assert "## Invariant" in content
    assert "## Verification Scope" in content
    assert "## Verification Plan" in content
    assert "## Evidence" in content
    assert "## Provenance" in content
    assert "VERIFIED" in content
    assert "EV-WRITER-001" in content


def test_write_creates_both_formats(
    tmp_path: Path,
) -> None:
    report = make_report()

    json_path, markdown_path = ReportWriter().write(
        report,
        tmp_path / "reports",
    )

    assert json_path.exists()
    assert markdown_path.exists()
    assert json_path.suffix == ".json"
    assert markdown_path.suffix == ".md"


def test_writer_creates_nested_output_directory(
    tmp_path: Path,
) -> None:
    report = make_report()

    output_directory = (
        tmp_path
        / "nested"
        / "verification"
        / "reports"
    )

    json_path, markdown_path = ReportWriter().write(
        report,
        output_directory,
    )

    assert output_directory.is_dir()
    assert json_path.exists()
    assert markdown_path.exists()


def test_writer_uses_run_id_for_both_filenames(
    tmp_path: Path,
) -> None:
    report = make_report()

    json_path, markdown_path = ReportWriter().write(
        report,
        tmp_path,
    )

    assert json_path.name == "RUN-WRITER-001.json"
    assert markdown_path.name == "RUN-WRITER-001.md"

def test_write_json_matches_authoritative_serialization(
    tmp_path: Path,
) -> None:
    import json

    from ai_verify.reporting.serialization import serialize_report

    report = make_report()

    output_path = ReportWriter().write_json(
        report,
        tmp_path,
    )

    written = json.loads(
        output_path.read_text(encoding="utf-8")
    )

    assert written == serialize_report(report)
