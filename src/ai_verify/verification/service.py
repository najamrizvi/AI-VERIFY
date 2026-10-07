from pathlib import Path

from ai_verify.core.run_package import VerificationRun
from ai_verify.reporting.report import (
    VerificationReport,
    VerificationReportBuilder,
)
from ai_verify.reporting.serialization import serialize_report
from ai_verify.verification.activity_runner import (
    VerificationActivityRequest,
)
from ai_verify.verification.orchestrator import (
    VerificationOrchestrator,
)


class VerificationService:
    """Run the complete deterministic verification workflow."""

    def __init__(
        self,
        orchestrator: VerificationOrchestrator | None = None,
        report_builder: VerificationReportBuilder | None = None,
    ) -> None:
        self._orchestrator = (
            orchestrator or VerificationOrchestrator()
        )
        self._report_builder = (
            report_builder or VerificationReportBuilder()
        )

    def verify(
        self,
        *,
        run_id: str,
        requirement: str,
        invariant: str,
        repository_root: Path | str,
        activities: tuple[VerificationActivityRequest, ...],
        provenance: dict,
    ) -> tuple[VerificationRun, VerificationReport, dict]:
        run = self._orchestrator.run(
            run_id=run_id,
            requirement=requirement,
            invariant=invariant,
            repository_root=repository_root,
            activities=activities,
            provenance=provenance,
        )

        report = self._report_builder.build(run)
        serialized = serialize_report(report)

        return run, report, serialized
