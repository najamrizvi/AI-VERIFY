from ai_verify.core.decision import determine_verification
from ai_verify.core.models import (
    Evidence,
    EvidenceStatus,
    VerificationStatus,
)


def evidence(
    evidence_id: str,
    status: EvidenceStatus,
) -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        status=status,
        description=f"Evidence {evidence_id}",
        source="test",
    )


def test_sufficient_supporting_evidence_is_verified():
    result = determine_verification(
        [
            evidence("E1", EvidenceStatus.SUPPORTS),
            evidence("E2", EvidenceStatus.SUPPORTS),
        ],
        required_evidence_count=2,
    )

    assert result.status == VerificationStatus.VERIFIED
    assert result.rule == "SUFFICIENT_SUPPORTING_EVIDENCE"


def test_insufficient_supporting_evidence_is_partially_verified():
    result = determine_verification(
        [evidence("E1", EvidenceStatus.SUPPORTS)],
        required_evidence_count=2,
    )

    assert result.status == VerificationStatus.PARTIALLY_VERIFIED
    assert result.rule == "INSUFFICIENT_OR_INCONCLUSIVE_EVIDENCE"


def test_inconclusive_evidence_is_partially_verified():
    result = determine_verification(
        [
            evidence("E1", EvidenceStatus.SUPPORTS),
            evidence("E2", EvidenceStatus.INCONCLUSIVE),
        ],
        required_evidence_count=2,
    )

    assert result.status == VerificationStatus.PARTIALLY_VERIFIED


def test_contradictory_evidence_is_not_verified():
    result = determine_verification(
        [
            evidence("E1", EvidenceStatus.SUPPORTS),
            evidence("E2", EvidenceStatus.CONTRADICTS),
        ],
        required_evidence_count=1,
    )

    assert result.status == VerificationStatus.NOT_VERIFIED
    assert result.rule == "CONTRADICTION_WINS"


def test_contradiction_wins_over_sufficient_supporting_evidence():
    result = determine_verification(
        [
            evidence("E1", EvidenceStatus.SUPPORTS),
            evidence("E2", EvidenceStatus.SUPPORTS),
            evidence("E3", EvidenceStatus.CONTRADICTS),
        ],
        required_evidence_count=2,
    )

    assert result.status == VerificationStatus.NOT_VERIFIED


def test_decision_is_deterministic():
    evidence_set = [
        evidence("E1", EvidenceStatus.SUPPORTS),
        evidence("E2", EvidenceStatus.INCONCLUSIVE),
    ]

    first = determine_verification(
        evidence_set,
        required_evidence_count=2,
    )
    second = determine_verification(
        evidence_set,
        required_evidence_count=2,
    )

    assert first == second
