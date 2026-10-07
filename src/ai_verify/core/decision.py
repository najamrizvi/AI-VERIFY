from collections.abc import Sequence

from .models import (
    DecisionResult,
    Evidence,
    EvidenceStatus,
    VerificationStatus,
)


def determine_verification(
    evidence: Sequence[Evidence],
    *,
    required_evidence_count: int,
) -> DecisionResult:
    """Determine the authoritative verification result.

    The decision is deterministic and does not depend on AI output.

    Rules:
    1. Any contradictory evidence means NOT VERIFIED.
    2. Without contradiction, insufficient or inconclusive evidence means
       PARTIALLY VERIFIED.
    3. Sufficient supporting evidence means VERIFIED.
    """

    contradictory = [
        item for item in evidence
        if item.status == EvidenceStatus.CONTRADICTS
    ]

    if contradictory:
        return DecisionResult(
            status=VerificationStatus.NOT_VERIFIED,
            rule="CONTRADICTION_WINS",
            rationale=(
                "Contradictory evidence was found; therefore the "
                "requirement cannot be considered verified."
            ),
        )

    supporting = [
        item for item in evidence
        if item.status == EvidenceStatus.SUPPORTS
    ]

    if len(supporting) < required_evidence_count:
        return DecisionResult(
            status=VerificationStatus.PARTIALLY_VERIFIED,
            rule="INSUFFICIENT_OR_INCONCLUSIVE_EVIDENCE",
            rationale=(
                "No contradiction was found, but the available supporting "
                "evidence is insufficient for verification."
            ),
        )

    return DecisionResult(
        status=VerificationStatus.VERIFIED,
        rule="SUFFICIENT_SUPPORTING_EVIDENCE",
        rationale=(
            "Required supporting evidence is present and no contradictory "
            "evidence was found."
        ),
    )
