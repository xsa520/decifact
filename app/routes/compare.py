from fastapi import APIRouter
from pydantic import BaseModel

from canonical.boundary_reference import compute_boundary_context_hash
from canonical.canonicalize import compute_canonical_hash
from canonical.invariants import SOVEREIGNTY_PRINCIPLE
from canonical.schema import AuthorityContext

router = APIRouter()


class RuntimeInput(BaseModel):
    decision: dict
    authority_context: AuthorityContext


class CompareRequest(BaseModel):
    runtime_a: RuntimeInput
    runtime_b: RuntimeInput


def _build_fracture_boundary(
    canonical_hash_a: str,
    canonical_hash_b: str,
    boundary_context_hash_a: str,
    boundary_context_hash_b: str,
    authority_a: AuthorityContext,
    authority_b: AuthorityContext,
) -> list[str]:
    fracture_boundary: list[str] = []

    if canonical_hash_a != canonical_hash_b:
        fracture_boundary.append("decision_object_divergence")

    if (
        boundary_context_hash_a != boundary_context_hash_b
        and canonical_hash_a == canonical_hash_b
    ):
        fracture_boundary.append("authority_assumption_divergence")

    if (
        authority_a.authority_domain == authority_b.authority_domain
        and authority_a.admissibility_scope != authority_b.admissibility_scope
    ):
        fracture_boundary.append("acceptance_context_mismatch")

    return fracture_boundary


@router.post("/compare")
def compare(payload: CompareRequest) -> dict:
    canonical_hash_a = compute_canonical_hash(payload.runtime_a.decision)
    canonical_hash_b = compute_canonical_hash(payload.runtime_b.decision)

    authority_a = payload.runtime_a.authority_context.dict()
    authority_b = payload.runtime_b.authority_context.dict()
    boundary_context_hash_a = compute_boundary_context_hash(authority_a)
    boundary_context_hash_b = compute_boundary_context_hash(authority_b)

    fracture_boundary = _build_fracture_boundary(
        canonical_hash_a,
        canonical_hash_b,
        boundary_context_hash_a,
        boundary_context_hash_b,
        payload.runtime_a.authority_context,
        payload.runtime_b.authority_context,
    )

    return {
        "canonical_equivalent": canonical_hash_a == canonical_hash_b,
        "governance_equivalent": (
            boundary_context_hash_a == boundary_context_hash_b
        ),
        "fracture_boundary": fracture_boundary,
        "canonical_hash_a": canonical_hash_a,
        "canonical_hash_b": canonical_hash_b,
        "boundary_context_hash_a": boundary_context_hash_a,
        "boundary_context_hash_b": boundary_context_hash_b,
        "replayable": True,
        "sovereignty_principle": SOVEREIGNTY_PRINCIPLE,
    }
