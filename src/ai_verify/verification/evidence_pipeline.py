from pathlib import Path

from ai_verify.core.execution import ExecutionRequest
from ai_verify.core.models import Evidence, EvidenceStatus
from ai_verify.verification.evidence import EvidenceCollector, EvidenceObservation
from ai_verify.verification.evidence_adapter import ExecutionEvidenceAdapter
from ai_verify.verification.executor import ControlledExecutor


class EvidencePipeline:
    """Execute a verification activity and collect structured evidence."""

    def __init__(
        self,
        executor: ControlledExecutor | None = None,
        adapter: ExecutionEvidenceAdapter | None = None,
        collector: EvidenceCollector | None = None,
    ) -> None:
        self._executor = executor or ControlledExecutor()
        self._adapter = adapter or ExecutionEvidenceAdapter()
        self._collector = collector or EvidenceCollector()

    def execute_and_collect(
        self,
        request: ExecutionRequest,
        repository_root: Path | str,
        *,
        evidence_id: str,
        description: str,
        success_status: EvidenceStatus,
        failure_status: EvidenceStatus,
    ) -> Evidence:
        execution = self._executor.execute(
            request,
            repository_root,
        )

        observation = self._adapter.adapt(
            execution,
            evidence_id=evidence_id,
            description=description,
            success_status=success_status,
            failure_status=failure_status,
        )

        return self._collector.collect(observation)