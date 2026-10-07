import pytest

from ai_verify.core.models import EvidenceStatus, EvidenceType
from ai_verify.verification.evidence import (
    EvidenceCollector,
    EvidenceObservation,
)


def make_observation() -> EvidenceObservation:
    return EvidenceObservation(
        evidence_id="EV-001",
        status=EvidenceStatus.SUPPORTS,
        description="Positive-path test passed.",
        source="tests/test_invoice_service.py::test_valid_amount",
        evidence_type=EvidenceType.TEST,
        observation="Test completed successfully with exit code 0.",
        execution_id="EXEC-001",
    )


def test_collect_creates_evidence() -> None:
    evidence = EvidenceCollector().collect(make_observation())

    assert evidence.evidence_id == "EV-001"
    assert evidence.status == EvidenceStatus.SUPPORTS
    assert evidence.evidence_type == EvidenceType.TEST


def test_collect_preserves_provenance() -> None:
    evidence = EvidenceCollector().collect(make_observation())

    assert evidence.source == (
        "tests/test_invoice_service.py::test_valid_amount"
    )
    assert evidence.execution_id == "EXEC-001"


def test_collect_preserves_observation() -> None:
    evidence = EvidenceCollector().collect(make_observation())

    assert evidence.observation == (
        "Test completed successfully with exit code 0."
    )


def test_empty_evidence_id_is_rejected() -> None:
    observation = make_observation()
    observation = EvidenceObservation(
        evidence_id=" ",
        status=observation.status,
        description=observation.description,
        source=observation.source,
        evidence_type=observation.evidence_type,
        observation=observation.observation,
        execution_id=observation.execution_id,
    )

    with pytest.raises(ValueError, match="Evidence ID"):
        EvidenceCollector().collect(observation)


def test_empty_source_is_rejected() -> None:
    observation = make_observation()
    observation = EvidenceObservation(
        evidence_id=observation.evidence_id,
        status=observation.status,
        description=observation.description,
        source=" ",
        evidence_type=observation.evidence_type,
        observation=observation.observation,
        execution_id=observation.execution_id,
    )

    with pytest.raises(ValueError, match="Evidence source"):
        EvidenceCollector().collect(observation)


def test_empty_observation_is_rejected() -> None:
    observation = make_observation()
    observation = EvidenceObservation(
        evidence_id=observation.evidence_id,
        status=observation.status,
        description=observation.description,
        source=observation.source,
        evidence_type=observation.evidence_type,
        observation=" ",
        execution_id=observation.execution_id,
    )

    with pytest.raises(ValueError, match="Evidence observation"):
        EvidenceCollector().collect(observation)


def test_collected_evidence_is_immutable() -> None:
    evidence = EvidenceCollector().collect(make_observation())

    with pytest.raises(AttributeError):
        evidence.status = EvidenceStatus.CONTRADICTS
