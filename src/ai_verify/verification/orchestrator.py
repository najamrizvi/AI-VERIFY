from pathlib import Path

from ai_verify.core.run_package import VerificationRun
from ai_verify.repository.analyzer import RepositoryAnalyzer
from ai_verify.verification.activity_runner import (
    VerificationActivityRequest,
    VerificationActivityRunner,
)
from ai_verify.verification.planner import VerificationPlanner
from ai_verify.verification.run import VerificationRunBuilder
from ai_verify.verification.scope import VerificationScopeBuilder


class VerificationOrchestrator:
    """Coordinate the deterministic verification workflow."""

    def __init__(
        self,
        repository_analyzer: RepositoryAnalyzer | None = None,
        scope_builder: VerificationScopeBuilder | None = None,
        planner: VerificationPlanner | None = None,
        activity_runner: VerificationActivityRunner | None = None,
        run_builder: VerificationRunBuilder | None = None,
    ) -> None:
        self._repository_analyzer = (
            repository_analyzer or RepositoryAnalyzer()
        )
        self._scope_builder = (
            scope_builder or VerificationScopeBuilder()
        )
        self._planner = planner or VerificationPlanner()
        self._activity_runner = (
            activity_runner or VerificationActivityRunner()
        )
        self._run_builder = run_builder or VerificationRunBuilder()

    def run(
        self,
        *,
        run_id: str,
        requirement: str,
        invariant: str,
        repository_root: Path | str,
        activities: tuple[VerificationActivityRequest, ...],
        provenance: dict,
    ) -> VerificationRun:
        analysis = self._repository_analyzer.analyze(
            repository_root
        )

        scope = self._scope_builder.build(
            requirement,
            invariant,
            analysis,
        )

        plan = self._planner.build(
            requirement,
            invariant,
            scope,
        )

        evidence = self._activity_runner.run(
            activities,
            repository_root,
        )

        return self._run_builder.build(
            run_id=run_id,
            requirement=requirement,
            invariant=invariant,
            plan=plan,
            evidence=evidence,
            provenance=provenance,
        )
