from dataclasses import dataclass
from pathlib import Path

from ai_verify.core.execution import ExecutionRequest
from ai_verify.core.models import Evidence, EvidenceStatus
from ai_verify.verification.evidence_pipeline import EvidencePipeline


@dataclass(frozen=True)
class VerificationActivityRequest:
    activity_id: str
    execution: ExecutionRequest
    evidence_id: str
    description: str
    success_status: EvidenceStatus
    failure_status: EvidenceStatus


class VerificationActivityRunner:
    """Execute explicitly defined verification activities."""

    def __init__(
        self,
        pipeline: EvidencePipeline | None = None,
    ) -> None:
        self._pipeline = pipeline or EvidencePipeline()

    def run(
        self,
        activities: tuple[VerificationActivityRequest, ...],
        repository_root: Path | str,
    ) -> tuple[Evidence, ...]:
        evidence: list[Evidence] = []

        for activity in activities:
            evidence.append(
                self._pipeline.execute_and_collect(
                    activity.execution,
                    repository_root,
                    evidence_id=activity.evidence_id,
                    description=activity.description,
                    success_status=activity.success_status,
                    failure_status=activity.failure_status,
                )
            )

        return tuple(evidence)