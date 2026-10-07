from dataclasses import dataclass

from ai_verify.core.models import Evidence, EvidenceStatus, EvidenceType


@dataclass(frozen=True)
class EvidenceObservation:
    """Raw observation supplied by a trusted collection mechanism."""

    evidence_id: str
    status: EvidenceStatus
    description: str
    source: str
    evidence_type: EvidenceType
    observation: str
    execution_id: str | None = None


class EvidenceCollector:
    """Convert validated observations into immutable evidence records."""

    def collect(
        self,
        observation: EvidenceObservation,
    ) -> Evidence:
        if not observation.evidence_id.strip():
            raise ValueError("Evidence ID must not be empty.")

        if not observation.description.strip():
            raise ValueError("Evidence description must not be empty.")

        if not observation.source.strip():
            raise ValueError("Evidence source must not be empty.")

        if not observation.observation.strip():
            raise ValueError("Evidence observation must not be empty.")

        return Evidence(
            evidence_id=observation.evidence_id,
            status=observation.status,
            description=observation.description,
            source=observation.source,
            evidence_type=observation.evidence_type,
            observation=observation.observation,
            execution_id=observation.execution_id,
        )