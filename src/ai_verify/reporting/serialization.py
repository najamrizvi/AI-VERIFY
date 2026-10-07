from typing import Any

from ai_verify.reporting.report import VerificationReport


def serialize_report(
    report: VerificationReport,
) -> dict[str, Any]:
    """Convert a verification report into a JSON-compatible mapping."""

    return {
        "run_id": report.run_id,
        "requirement": report.requirement,
        "invariant": report.invariant,
        "status": report.status,
        "decision_rule": report.decision_rule,
        "rationale": report.rationale,
        "scope": report.scope,
        "verification_plan": report.verification_plan,
        "evidence": [
            dict(item)
            for item in report.evidence
        ],
        "provenance": report.provenance,
    }
