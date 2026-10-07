import hashlib
import json
from dataclasses import asdict
from typing import Any

from .run_package import VerificationRun


def serialize_run(run: VerificationRun) -> dict[str, Any]:
    """Convert a verification run into a canonical JSON-compatible mapping."""

    payload = asdict(run)

    payload["evidence"] = [
        {
            "evidence_id": item["evidence_id"],
            "status": item["status"],
            "description": item["description"],
            "source": item["source"],
            "evidence_type": item["evidence_type"],
            "observation": item["observation"],
            "execution_id": item["execution_id"],
        }
        for item in payload["evidence"]
    ]

    payload["decision"]["status"] = str(payload["decision"]["status"])

    return payload


def canonical_bytes(run: VerificationRun) -> bytes:
    """Return deterministic bytes representing the run package."""

    payload = serialize_run(run)

    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def calculate_integrity_hash(run: VerificationRun) -> str:
    """Calculate a lightweight SHA-256 integrity fingerprint."""

    return hashlib.sha256(canonical_bytes(run)).hexdigest()


def verify_integrity(
    run: VerificationRun,
    expected_hash: str,
) -> bool:
    """Return True when the run matches the expected integrity fingerprint."""

    return calculate_integrity_hash(run) == expected_hash