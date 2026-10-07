import pytest

from pathlib import Path
from ai_verify.cli.main import build_parser, main
from ai_verify.core.models import VerificationStatus


def test_parser_has_expected_program_name() -> None:
    parser = build_parser()

    assert parser.prog == "ai-verify"


def test_parser_accepts_all_required_arguments() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "--repository",
            ".",
            "--requirement",
            "Requirement",
            "--invariant",
            "Invariant",
            "--run-id",
            "RUN-001",
            "--command",
            "python",
            "-m",
            "pytest",
        ]
    )

    assert str(args.repository) == "."
    assert args.requirement == "Requirement"
    assert args.invariant == "Invariant"
    assert args.run_id == "RUN-001"
    assert args.command == ["python", "-m", "pytest"]


@pytest.mark.parametrize(
    "missing_argument",
    [
        "--repository",
        "--requirement",
        "--invariant",
        "--run-id",
        "--command",
    ],
)
def test_parser_rejects_missing_required_argument(
    missing_argument: str,
) -> None:
    arguments = {
        "--repository": ".",
        "--requirement": "Requirement",
        "--invariant": "Invariant",
        "--run-id": "RUN-001",
        "--command": "python",
    }

    arguments.pop(missing_argument)

    parser = build_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(
            [
                item
                for key, value in arguments.items()
                for item in (key, value)
            ]
        )

    assert exc_info.value.code == 2


def test_repository_argument_is_path() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "--repository",
            "C:/repository",
            "--requirement",
            "Requirement",
            "--invariant",
            "Invariant",
            "--run-id",
            "RUN-002",
            "--command",
            "python",
            "-m",
            "pytest",
        ]
    )

    assert args.repository.name == "repository"


def test_parser_preserves_requirement_text() -> None:
    parser = build_parser()

    requirement = (
        "An authenticated user must only retrieve "
        "their own invoice."
    )

    args = parser.parse_args(
        [
            "--repository",
            ".",
            "--requirement",
            requirement,
            "--invariant",
            "invoice.user_id == authenticated_user.id",
            "--run-id",
            "RUN-003",
            "--command",
            "python",
            "-m",
            "pytest",
        ]
    )

    assert args.requirement == requirement


class FakeReport:
    run_id = "RUN-FAKE"
    requirement = "Requirement"
    invariant = "Invariant"
    status = VerificationStatus.VERIFIED.value
    decision_rule = "SUFFICIENT_SUPPORTING_EVIDENCE"
    rationale = "Required supporting evidence is present."
    scope = {}
    verification_plan = {}
    evidence = ()
    provenance = {}


class FakeVerificationService:
    captured = None

    def verify(self, **kwargs):
        self.captured = kwargs
        return object(), FakeReport(), {}


def test_main_calls_verification_service(monkeypatch, capsys) -> None:
    fake_service = FakeVerificationService()

    monkeypatch.setattr(
        "ai_verify.cli.main.VerificationService",
        lambda: fake_service,
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "ai-verify",
            "--repository",
            ".",
            "--requirement",
            "Requirement",
            "--invariant",
            "Invariant",
            "--run-id",
            "RUN-004",
            "--command",
            "python",
            "-m",
            "pytest",
        ],
    )

    result = main()

    assert result == 0
    assert fake_service.captured is not None
    assert fake_service.captured["requirement"] == "Requirement"
    assert fake_service.captured["invariant"] == "Invariant"
    assert fake_service.captured["run_id"] == "RUN-004"
    assert str(fake_service.captured["repository_root"]) == "."
    assert len(fake_service.captured["activities"]) == 1

    activity = fake_service.captured["activities"][0]

    assert activity.activity_id == "cli-activity"
    assert activity.evidence_id == "cli-evidence"
    assert activity.execution.command == (
        "python",
        "-m",
        "pytest",
    )

    output = capsys.readouterr().out

    assert "Status: VERIFIED" in output
    assert "Rule: SUFFICIENT_SUPPORTING_EVIDENCE" in output


def test_main_preserves_explicit_command(monkeypatch) -> None:
    fake_service = FakeVerificationService()

    monkeypatch.setattr(
        "ai_verify.cli.main.VerificationService",
        lambda: fake_service,
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "ai-verify",
            "--repository",
            ".",
            "--requirement",
            "Requirement",
            "--invariant",
            "Invariant",
            "--run-id",
            "RUN-005",
            "--command",
            "python",
            "-m",
            "pytest",
            "tests",
            "-v",
        ],
    )

    result = main()

    assert result == 0

    activity = fake_service.captured["activities"][0]

    assert activity.execution.command == (
        "python",
        "-m",
        "pytest",
        "tests",
        "-v",
    )

def test_parser_defaults_output_directory() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "--repository",
            ".",
            "--requirement",
            "Requirement",
            "--invariant",
            "Invariant",
            "--run-id",
            "RUN-006",
            "--command",
            "python",
            "-m",
            "pytest",
        ]
    )

    assert args.output_directory == Path("reports")


def test_parser_accepts_custom_output_directory() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "--repository",
            ".",
            "--requirement",
            "Requirement",
            "--invariant",
            "Invariant",
            "--run-id",
            "RUN-007",
            "--output-directory",
            "custom-reports",
            "--command",
            "python",
            "-m",
            "pytest",
        ]
    )

    assert args.output_directory == Path("custom-reports")


def test_main_writes_json_and_markdown_reports(
    monkeypatch,
    tmp_path,
    capsys,
) -> None:
    fake_service = FakeVerificationService()

    monkeypatch.setattr(
        "ai_verify.cli.main.VerificationService",
        lambda: fake_service,
    )

    output_directory = tmp_path / "reports"

    monkeypatch.setattr(
        "sys.argv",
        [
            "ai-verify",
            "--repository",
            ".",
            "--requirement",
            "Requirement",
            "--invariant",
            "Invariant",
            "--run-id",
            "RUN-008",
            "--output-directory",
            str(output_directory),
            "--command",
            "python",
            "-m",
            "pytest",
        ],
    )

    result = main()

    assert result == 0

    json_path = output_directory / "RUN-FAKE.json"
    markdown_path = output_directory / "RUN-FAKE.md"

    assert json_path.exists()
    assert markdown_path.exists()

    output = capsys.readouterr().out

    assert "JSON report:" in output
    assert "Markdown report:" in output