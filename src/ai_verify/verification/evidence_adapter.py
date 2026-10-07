from ai_verify.core.execution import ExecutionResult, ExecutionStatus
from ai_verify.core.models import EvidenceStatus, EvidenceType
from ai_verify.verification.evidence import EvidenceObservation


class ExecutionEvidenceAdapter:
    """Translate execution facts into structured evidence observations."""

    def adapt(
        self,
        execution: ExecutionResult,
        *,
        evidence_id: str,
        description: str,
        success_status: EvidenceStatus,
        failure_status: EvidenceStatus,
    ) -> EvidenceObservation:
        if not evidence_id.strip():
            raise ValueError("Evidence ID must not be empty.")

        if not description.strip():
            raise ValueError("Evidence description must not be empty.")

        if execution.status == ExecutionStatus.COMPLETED:
            status = (
                success_status
                if execution.exit_code == 0
                else failure_status
            )
        else:
            status = EvidenceStatus.INCONCLUSIVE

        observation = self._build_observation(execution)

        return EvidenceObservation(
            evidence_id=evidence_id,
            status=status,
            description=description,
            source=execution.working_directory,
            evidence_type=EvidenceType.RUNTIME,
            observation=observation,
            execution_id=None,
        )

    @staticmethod
    def _build_observation(execution: ExecutionResult) -> str:
        parts = [
            f"Execution status: {execution.status.value}.",
            f"Exit code: {execution.exit_code}.",
        ]

        if execution.stdout:
            parts.append(f"stdout: {execution.stdout.strip()}")

        if execution.stderr:
            parts.append(f"stderr: {execution.stderr.strip()}")

        return " ".join(parts)