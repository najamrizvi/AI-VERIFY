from pathlib import Path

from ai_verify.repository.analyzer import RepositoryAnalysis, RepositoryFile
from ai_verify.verification.planner import VerificationPlanner
from ai_verify.verification.scope import (
    VerificationScope,
    VerificationScopeBuilder,
)


def make_scope() -> VerificationScope:
    root = Path("/repo")

    analysis = RepositoryAnalysis(
        root=root,
        python_files=(
            RepositoryFile(
                relative_path="src/invoice_service.py",
                absolute_path=root / "src" / "invoice_service.py",
            ),
            RepositoryFile(
                relative_path="tests/test_invoice_service.py",
                absolute_path=root / "tests" / "test_invoice_service.py",
            ),
        ),
    )

    return VerificationScopeBuilder().build(
        requirement="Invoice amount must not be negative.",
        invariant="amount >= 0",
        analysis=analysis,
    )


def test_plan_preserves_requirement_and_invariant() -> None:
    scope = make_scope()

    plan = VerificationPlanner().build(
        "Invoice amount must not be negative.",
        "amount >= 0",
        scope,
    )

    assert plan.requirement == "Invoice amount must not be negative."
    assert plan.invariant == "amount >= 0"


def test_plan_preserves_scope() -> None:
    scope = make_scope()

    plan = VerificationPlanner().build(
        "Requirement",
        "Invariant",
        scope,
    )

    assert plan.scope == scope


def test_plan_contains_positive_negative_and_edge_activities() -> None:
    scope = make_scope()

    plan = VerificationPlanner().build(
        "Requirement",
        "Invariant",
        scope,
    )

    assert [activity.category for activity in plan.activities] == [
        "positive",
        "negative",
        "edge",
    ]


def test_all_core_activities_are_required() -> None:
    plan = VerificationPlanner().build(
        "Requirement",
        "Invariant",
        make_scope(),
    )

    assert all(activity.required for activity in plan.activities)


def test_activity_ids_are_deterministic() -> None:
    planner = VerificationPlanner()
    scope = make_scope()

    first = planner.build("Requirement", "Invariant", scope)
    second = planner.build("Requirement", "Invariant", scope)

    assert first.activities == second.activities


def test_plan_requires_three_evidence_items() -> None:
    plan = VerificationPlanner().build(
        "Requirement",
        "Invariant",
        make_scope(),
    )

    assert plan.required_evidence_count == 3