from ai_verify.core.decision import determine_verification
from ai_verify.core.models import Evidence
from ai_verify.core.run_package import VerificationRun
from ai_verify.verification.planner import VerificationPlan


class VerificationRunBuilder:
    """Assemble a deterministic verification run from validated components."""

    def build(
        self,
        *,
        run_id: str,
        requirement: str,
        invariant: str,
        plan: VerificationPlan,
        evidence: tuple[Evidence, ...],
        provenance: dict,
    ) -> VerificationRun:
        decision = determine_verification(
            evidence,
            required_evidence_count=plan.required_evidence_count,
        )

        return VerificationRun(
            run_id=run_id,
            requirement=requirement,
            invariant=invariant,
            scope={
                "files": [
                    {
                        "relative_path": item.relative_path,
                        "role": item.role,
                    }
                    for item in plan.scope.files
                ]
            },
            verification_plan={
                "activities": [
                    {
                        "activity_id": activity.activity_id,
                        "category": activity.category,
                        "objective": activity.objective,
                        "required": activity.required,
                    }
                    for activity in plan.activities
                ],
                "required_evidence_count": (
                    plan.required_evidence_count
                ),
            },
            evidence=evidence,
            decision=decision,
            provenance=provenance,
        )