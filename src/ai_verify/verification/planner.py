from dataclasses import dataclass

from ai_verify.verification.scope import VerificationScope


@dataclass(frozen=True)
class VerificationActivity:
    activity_id: str
    category: str
    objective: str
    required: bool = True


@dataclass(frozen=True)
class VerificationPlan:
    requirement: str
    invariant: str
    scope: VerificationScope
    activities: tuple[VerificationActivity, ...]
    required_evidence_count: int


class VerificationPlanner:
    """Create a deterministic verification plan."""

    def build(
        self,
        requirement: str,
        invariant: str,
        scope: VerificationScope,
    ) -> VerificationPlan:
        activities = (
            VerificationActivity(
                activity_id="positive-path",
                category="positive",
                objective=(
                    "Verify that the implementation satisfies the "
                    "requirement under the expected valid behavior."
                ),
            ),
            VerificationActivity(
                activity_id="negative-path",
                category="negative",
                objective=(
                    "Verify that invalid or prohibited behavior is "
                    "rejected or prevented."
                ),
            ),
            VerificationActivity(
                activity_id="edge-case",
                category="edge",
                objective=(
                    "Verify boundary or unusual conditions that could "
                    "invalidate the requirement."
                ),
            ),
        )

        return VerificationPlan(
            requirement=requirement,
            invariant=invariant,
            scope=scope,
            activities=activities,
            required_evidence_count=3,
        )