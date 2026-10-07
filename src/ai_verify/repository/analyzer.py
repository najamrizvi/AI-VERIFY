from dataclasses import dataclass
from pathlib import Path


DEFAULT_IGNORED_DIRECTORIES = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "node_modules",
    }
)


@dataclass(frozen=True)
class RepositoryFile:
    relative_path: str
    absolute_path: Path


@dataclass(frozen=True)
class RepositoryAnalysis:
    root: Path
    python_files: tuple[RepositoryFile, ...]


class RepositoryAnalyzer:
    """Safely discover Python files within a selected repository root."""

    def __init__(
        self,
        ignored_directories: frozenset[str] = DEFAULT_IGNORED_DIRECTORIES,
    ) -> None:
        self._ignored_directories = ignored_directories

    def analyze(self, repository_root: Path | str) -> RepositoryAnalysis:
        root = Path(repository_root).expanduser().resolve()

        if not root.exists():
            raise FileNotFoundError(
                f"Repository root does not exist: {root}"
            )

        if not root.is_dir():
            raise NotADirectoryError(
                f"Repository root is not a directory: {root}"
            )

        files: list[RepositoryFile] = []

        for path in root.rglob("*.py"):
            if self._is_ignored(path, root):
                continue

            resolved = path.resolve()

            if not self._is_within_root(resolved, root):
                continue

            files.append(
                RepositoryFile(
                    relative_path=resolved.relative_to(root).as_posix(),
                    absolute_path=resolved,
                )
            )

        files.sort(key=lambda item: item.relative_path)

        return RepositoryAnalysis(
            root=root,
            python_files=tuple(files),
        )

    def _is_ignored(self, path: Path, root: Path) -> bool:
        relative_parts = path.relative_to(root).parts

        return any(
            part in self._ignored_directories
            for part in relative_parts[:-1]
        )

    @staticmethod
    def _is_within_root(path: Path, root: Path) -> bool:
        try:
            path.relative_to(root)
            return True
        except ValueError:
            return False
