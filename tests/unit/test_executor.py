import sys
import time
from pathlib import Path

import pytest

from ai_verify.core.execution import (
    ExecutionRequest,
    ExecutionStatus,
)
from ai_verify.verification.executor import ControlledExecutor


def make_request(*args: str, timeout: float = 5.0) -> ExecutionRequest:
    return ExecutionRequest(
        command=(sys.executable, "-c", *args),
        working_directory=".",
        timeout_seconds=timeout,
    )


def test_successful_command_is_completed(tmp_path: Path) -> None:
    result = ControlledExecutor().execute(
        make_request("print('success')"),
        tmp_path,
    )

    assert result.status == ExecutionStatus.COMPLETED
    assert result.exit_code == 0
    assert result.stdout.strip() == "success"
    assert result.stderr == ""


def test_failed_command_is_distinguished_from_timeout(
    tmp_path: Path,
) -> None:
    result = ControlledExecutor().execute(
        make_request(
            "import sys; print('failure'); sys.exit(2)"
        ),
        tmp_path,
    )

    assert result.status == ExecutionStatus.FAILED
    assert result.exit_code == 2
    assert "failure" in result.stdout


def test_timeout_is_reported_separately(tmp_path: Path) -> None:
    result = ControlledExecutor().execute(
        make_request(
            "import time; time.sleep(2)",
            timeout=0.1,
        ),
        tmp_path,
    )

    assert result.status == ExecutionStatus.TIMED_OUT
    assert result.exit_code is None


def test_command_and_working_directory_are_preserved(
    tmp_path: Path,
) -> None:
    result = ControlledExecutor().execute(
        make_request("print('hello')"),
        tmp_path,
    )

    assert result.command[0] == sys.executable
    assert result.command[1] == "-c"
    assert result.working_directory == tmp_path.resolve().as_posix()


def test_empty_command_is_rejected(tmp_path: Path) -> None:
    request = ExecutionRequest(
        command=(),
        working_directory=".",
        timeout_seconds=5,
    )

    with pytest.raises(ValueError, match="command"):
        ControlledExecutor().execute(request, tmp_path)


def test_invalid_timeout_is_rejected(tmp_path: Path) -> None:
    request = ExecutionRequest(
        command=(sys.executable, "-c", "print('x')"),
        working_directory=".",
        timeout_seconds=0,
    )

    with pytest.raises(ValueError, match="Timeout"):
        ControlledExecutor().execute(request, tmp_path)


def test_working_directory_must_exist(tmp_path: Path) -> None:
    request = make_request("print('x')")

    request = ExecutionRequest(
        command=request.command,
        working_directory="missing",
        timeout_seconds=request.timeout_seconds,
    )

    with pytest.raises(NotADirectoryError):
        ControlledExecutor().execute(request, tmp_path)


def test_working_directory_cannot_escape_repository(
    tmp_path: Path,
) -> None:
    outside = tmp_path.parent

    request = ExecutionRequest(
        command=(sys.executable, "-c", "print('x')"),
        working_directory="..",
        timeout_seconds=5,
    )

    with pytest.raises(ValueError, match="repository root"):
        ControlledExecutor().execute(request, tmp_path)


def test_non_directory_repository_is_rejected(tmp_path: Path) -> None:
    file_path = tmp_path / "repository.txt"
    file_path.write_text("not a repository", encoding="utf-8")

    request = make_request("print('x')")

    with pytest.raises(NotADirectoryError):
        ControlledExecutor().execute(request, file_path)


def test_missing_repository_is_rejected(tmp_path: Path) -> None:
    missing = tmp_path / "missing"

    request = make_request("print('x')")

    with pytest.raises(FileNotFoundError):
        ControlledExecutor().execute(request, missing)