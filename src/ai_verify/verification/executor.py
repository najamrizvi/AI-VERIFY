import subprocess
from pathlib import Path

from ai_verify.core.execution import (
    ExecutionRequest,
    ExecutionResult,
    ExecutionStatus,
)


class ControlledExecutor:
    """Execute explicitly supplied commands inside a selected repository."""

    def execute(
        self,
        request: ExecutionRequest,
        repository_root: Path | str,
    ) -> ExecutionResult:
        root = Path(repository_root).expanduser().resolve()

        if not root.exists():
            raise FileNotFoundError(
                f"Repository root does not exist: {root}"
            )

        if not root.is_dir():
            raise NotADirectoryError(
                f"Repository root is not a directory: {root}"
            )

        if not request.command:
            raise ValueError("Execution command must not be empty.")

        working_directory = (
            root / request.working_directory
        ).resolve()

        if not working_directory.is_dir():
            raise NotADirectoryError(
                f"Working directory is not a directory: "
                f"{working_directory}"
            )

        if not self._is_within_root(working_directory, root):
            raise ValueError(
                "Working directory must remain inside the repository root."
            )

        if request.timeout_seconds <= 0:
            raise ValueError(
                "Timeout must be greater than zero."
            )

        try:
            completed = subprocess.run(
                list(request.command),
                cwd=working_directory,
                capture_output=True,
                text=True,
                timeout=request.timeout_seconds,
                shell=False,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return ExecutionResult(
                command=request.command,
                working_directory=working_directory.as_posix(),
                status=ExecutionStatus.TIMED_OUT,
                exit_code=None,
                stdout=self._decode_output(exc.stdout),
                stderr=self._decode_output(exc.stderr),
                timeout_seconds=request.timeout_seconds,
            )

        status = (
            ExecutionStatus.COMPLETED
            if completed.returncode == 0
            else ExecutionStatus.FAILED
        )

        return ExecutionResult(
            command=request.command,
            working_directory=working_directory.as_posix(),
            status=status,
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            timeout_seconds=request.timeout_seconds,
        )

    @staticmethod
    def _is_within_root(path: Path, root: Path) -> bool:
        try:
            path.relative_to(root)
            return True
        except ValueError:
            return False

    @staticmethod
    def _decode_output(output: object) -> str:
        if output is None:
            return ""

        if isinstance(output, bytes):
            return output.decode("utf-8", errors="replace")

        return str(output)