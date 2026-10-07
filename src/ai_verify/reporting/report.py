from dataclasses import dataclass
from typing import Any

from ai_verify.core.run_package import VerificationRun


@dataclass(frozen=True)
class VerificationReport:
    run_id: str
    requirement: str
    invariant: str
    status: str
    decision_rule: str
    rationale: str
    scope: dict[str, Any]
    verification_plan: dict[str, Any]
    evidence: tuple[dict[str, Any], ...]
    provenance: dict[str, Any]


class VerificationReportBuilder:
    """Build a presentation-ready report from an authoritative run."""

    def build(
        self,
        run: VerificationRun,
    ) -> VerificationReport:
        evidence = tuple(
            {
                "evidence_id": item.evidence_id,
                "status": item.status.value,
                "description": item.description,
                "source": item.source,
                "evidence_type": item.evidence_type.value,
                "observation": item.observation,
                "execution_id": item.execution_id,
            }
            for item in run.evidence
        )

        return VerificationReport(
            run_id=run.run_id,
            requirement=run.requirement,
            invariant=run.invariant,
            status=run.decision.status.value,
            decision_rule=run.decision.rule,
            rationale=run.decision.rationale,
            scope=run.scope,
            verification_plan=run.verification_plan,
            evidence=evidence,
            provenance=run.provenance,
        )
