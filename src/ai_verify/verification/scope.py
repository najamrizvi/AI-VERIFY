from dataclasses import dataclass
from pathlib import Path

from ai_verify.repository.analyzer import RepositoryAnalysis


@dataclass(frozen=True)
class ScopeFile:
    relative_path: str
    absolute_path: Path
    role: str


@dataclass(frozen=True)
class VerificationScope:
    requirement: str
    invariant: str
    files: tuple[ScopeFile, ...]


class VerificationScopeBuilder:
    """Build a deterministic verification scope from repository analysis."""

    def build(
        self,
        requirement: str,
        invariant: str,
        analysis: RepositoryAnalysis,
    ) -> VerificationScope:
        files = [
            ScopeFile(
                relative_path=item.relative_path,
                absolute_path=item.absolute_path,
                role=self._classify_role(item.relative_path),
            )
            for item in analysis.python_files
        ]

        files.sort(key=lambda item: item.relative_path)

        return VerificationScope(
            requirement=requirement,
            invariant=invariant,
            files=tuple(files),
        )

    @staticmethod
    def _classify_role(relative_path: str) -> str:
        parts = Path(relative_path).parts

        if "test" in parts or relative_path.startswith("tests/"):
            return "test"

        return "source"