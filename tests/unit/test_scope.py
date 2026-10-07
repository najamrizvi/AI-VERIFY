from pathlib import Path

from ai_verify.repository.analyzer import RepositoryAnalysis, RepositoryFile
from ai_verify.verification.scope import VerificationScopeBuilder


def make_analysis() -> RepositoryAnalysis:
    root = Path("/repo")

    return RepositoryAnalysis(
        root=root,
        python_files=(
            RepositoryFile(
                relative_path="tests/test_invoice_service.py",
                absolute_path=root / "tests" / "test_invoice_service.py",
            ),
            RepositoryFile(
                relative_path="src/invoice_service.py",
                absolute_path=root / "src" / "invoice_service.py",
            ),
            RepositoryFile(
                relative_path="src/helpers.py",
                absolute_path=root / "src" / "helpers.py",
            ),
        ),
    )


def test_build_preserves_requirement_and_invariant() -> None:
    scope = VerificationScopeBuilder().build(
        requirement="Invoice amount must not be negative.",
        invariant="amount >= 0",
        analysis=make_analysis(),
    )

    assert scope.requirement == "Invoice amount must not be negative."
    assert scope.invariant == "amount >= 0"


def test_build_includes_discovered_files() -> None:
    scope = VerificationScopeBuilder().build(
        requirement="Requirement",
        invariant="Invariant",
        analysis=make_analysis(),
    )

    assert [item.relative_path for item in scope.files] == [
        "src/helpers.py",
        "src/invoice_service.py",
        "tests/test_invoice_service.py",
    ]


def test_scope_order_is_deterministic() -> None:
    analysis = make_analysis()
    builder = VerificationScopeBuilder()

    first = builder.build("Requirement", "Invariant", analysis)
    second = builder.build("Requirement", "Invariant", analysis)

    assert first == second


def test_source_files_are_classified_as_source() -> None:
    scope = VerificationScopeBuilder().build(
        "Requirement",
        "Invariant",
        make_analysis(),
    )

    roles = {
        item.relative_path: item.role
        for item in scope.files
    }

    assert roles["src/invoice_service.py"] == "source"
    assert roles["src/helpers.py"] == "source"


def test_test_files_are_classified_as_test() -> None:
    scope = VerificationScopeBuilder().build(
        "Requirement",
        "Invariant",
        make_analysis(),
    )

    roles = {
        item.relative_path: item.role
        for item in scope.files
    }

    assert roles["tests/test_invoice_service.py"] == "test"


def test_scope_paths_remain_inside_repository_root() -> None:
    analysis = make_analysis()

    scope = VerificationScopeBuilder().build(
        "Requirement",
        "Invariant",
        analysis,
    )

    for item in scope.files:
        assert item.absolute_path.is_relative_to(analysis.root)


def test_empty_repository_analysis_produces_empty_scope() -> None:
    analysis = RepositoryAnalysis(
        root=Path("/repo"),
        python_files=(),
    )

    scope = VerificationScopeBuilder().build(
        "Requirement",
        "Invariant",
        analysis,
    )

    assert scope.files == ()