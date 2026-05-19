from fastapi import APIRouter

from app.core.boundary_diff import compute_boundary_diff
from app.core.canonicalizer import canonicalize_json
from app.core.equivalence import is_equivalent
from app.core.hasher import sha256_hex
from app.core.invariant import extract_invariant_boundary
from app.core.metrics import get_call_count, increment_call_count
from app.models.verify_request import VerifyRequest


router = APIRouter()


@router.post("/verify-equivalence")
def verify_decision_equivalence(payload: VerifyRequest) -> dict:
    try:
        increment_call_count()
    except Exception:
        pass

    canonical_a = canonicalize_json(payload.decision_a)
    canonical_b = canonicalize_json(payload.decision_b)

    canonical_hash_a = sha256_hex(canonical_a)
    canonical_hash_b = sha256_hex(canonical_b)

    invariant_a = extract_invariant_boundary(payload.decision_a)
    invariant_b = extract_invariant_boundary(payload.decision_b)
    invariant_hash_a = sha256_hex(canonicalize_json(invariant_a))
    invariant_hash_b = sha256_hex(canonicalize_json(invariant_b))

    equivalent = is_equivalent(invariant_a, invariant_b)
    invariant_identity_match = invariant_hash_a == invariant_hash_b
    boundary_diff = compute_boundary_diff(invariant_a, invariant_b)

    return {
        "equivalent": equivalent,
        "invariant_identity_match": invariant_identity_match,
        "canonical_hash_a": canonical_hash_a,
        "canonical_hash_b": canonical_hash_b,
        "invariant_boundary": {
            "a": invariant_a,
            "b": invariant_b,
        },
        "invariant_boundary_diff": boundary_diff,
        "call_count": get_call_count(),
        "replayable": True,
        "replay_reference": None,
    }
