from ai_verify.core.integrity import (
    calculate_integrity_hash,
    serialize_run,
    verify_integrity,
)
from ai_verify.core.models import (
    DecisionResult,
    Evidence,
    EvidenceStatus,
    VerificationStatus,
)
from ai_verify.core.run_package import VerificationRun


def make_run() -> VerificationRun:
    return VerificationRun(
        run_id="run-001",
        requirement="An order must not be marked as paid unless payment succeeds.",
        invariant='order.status == "paid" implies payment.status == "completed"',
        scope={
            "repository": "g02_repository",
            "paths": ["services/order_service.py", "services/payment_service.py"],
        },
        verification_plan={
            "positive": ["successful payment"],
            "negative": ["failed payment"],
        },
        evidence=(
            Evidence(
                evidence_id="E1",
                status=EvidenceStatus.SUPPORTS,
                description="Successful payment allows order to become paid.",
                source="test",
            ),
        ),
        decision=DecisionResult(
            status=VerificationStatus.VERIFIED,
            rule="SUFFICIENT_SUPPORTING_EVIDENCE",
            rationale="Required supporting evidence is present.",
        ),
        provenance={
            "executor": "pytest",
            "environment": "local",
        },
    )


def test_run_serialization_preserves_core_information():
    run = make_run()

    payload = serialize_run(run)

    assert payload["run_id"] == "run-001"
    assert payload["requirement"].startswith("An order")
    assert payload["invariant"].startswith("order.status")
    assert payload["scope"]["repository"] == "g02_repository"
    assert payload["verification_plan"]["negative"] == ["failed payment"]
    assert payload["evidence"][0]["evidence_id"] == "E1"
    assert payload["decision"]["rule"] == "SUFFICIENT_SUPPORTING_EVIDENCE"
    assert payload["provenance"]["executor"] == "pytest"


def test_integrity_hash_is_deterministic():
    run = make_run()

    first = calculate_integrity_hash(run)
    second = calculate_integrity_hash(run)

    assert first == second
    assert len(first) == 64


def test_integrity_verification_succeeds_for_unchanged_run():
    run = make_run()
    expected_hash = calculate_integrity_hash(run)

    assert verify_integrity(run, expected_hash)


def test_integrity_verification_detects_changed_run():
    run = make_run()
    expected_hash = calculate_integrity_hash(run)

    changed_run = VerificationRun(
        run_id=run.run_id,
        requirement="Changed requirement",
        invariant=run.invariant,
        scope=run.scope,
        verification_plan=run.verification_plan,
        evidence=run.evidence,
        decision=run.decision,
        provenance=run.provenance,
    )

    assert not verify_integrity(changed_run, expected_hash)


def test_ai_metadata_is_not_part_of_authoritative_decision():
    run = make_run()

    ai_augmented_scope = dict(run.scope)
    ai_augmented_scope["ai"] = {
        "provider": "ollama",
        "model": "qwen3:1.7b",
        "explanation": "AI-generated explanation",
    }

    augmented_run = VerificationRun(
        run_id=run.run_id,
        requirement=run.requirement,
        invariant=run.invariant,
        scope=ai_augmented_scope,
        verification_plan=run.verification_plan,
        evidence=run.evidence,
        decision=run.decision,
        provenance=run.provenance,
    )

    assert augmented_run.decision == run.decision
    assert augmented_run.decision.status == VerificationStatus.VERIFIED


def test_schema_version_is_present():
    run = make_run()

    payload = serialize_run(run)

    assert payload["schema_version"] == "1.0"
