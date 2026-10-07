import argparse
from pathlib import Path

from ai_verify.core.execution import ExecutionRequest
from ai_verify.core.models import EvidenceStatus
from ai_verify.reporting.writer import ReportWriter
from ai_verify.verification.activity_runner import (
    VerificationActivityRequest,
)
from ai_verify.verification.service import VerificationService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-verify",
        description=(
            "AI-VERIFY - Evidence-First Requirement Verification System"
        ),
    )

    parser.add_argument(
        "--repository",
        required=True,
        type=Path,
        help="Path to the repository being verified.",
    )

    parser.add_argument(
        "--requirement",
        required=True,
        help="Requirement to verify.",
    )

    parser.add_argument(
        "--invariant",
        required=True,
        help="Invariant representing the requirement.",
    )

    parser.add_argument(
        "--run-id",
        required=True,
        help="Unique identifier for the verification run.",
    )

    parser.add_argument(
        "--output-directory",
        type=Path,
        default=Path("reports"),
        help="Directory where JSON and Markdown reports are written.",
    )

    parser.add_argument(
        "--command",
        required=True,
        nargs=argparse.REMAINDER,
        help=(
            "Explicit verification command to execute. "
            "This must be the final CLI option."
        ),
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    activity = VerificationActivityRequest(
        activity_id="cli-activity",
        execution=ExecutionRequest(
            command=tuple(args.command),
            working_directory=".",
            timeout_seconds=60.0,
        ),
        evidence_id="cli-evidence",
        description=(
            "Evidence collected from the explicitly supplied CLI command."
        ),
        success_status=EvidenceStatus.SUPPORTS,
        failure_status=EvidenceStatus.INCONCLUSIVE,
    )

    service = VerificationService()
    writer = ReportWriter()

    _, report, _ = service.verify(
        run_id=args.run_id,
        requirement=args.requirement,
        invariant=args.invariant,
        repository_root=args.repository,
        activities=(activity,),
        provenance={
            "interface": "cli",
            "command": list(args.command),
        },
    )

    json_path, markdown_path = writer.write(
        report,
        args.output_directory,
    )

    print(f"Status: {report.status}")
    print(f"Rule: {report.decision_rule}")
    print(f"Rationale: {report.rationale}")
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {markdown_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())