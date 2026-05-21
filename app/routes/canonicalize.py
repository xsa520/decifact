from fastapi import APIRouter
from datetime import datetime
from pydantic import BaseModel
from canonical.schema import (
    AuthorityContext, CanonicalBoundaryObject)
from canonical.canonicalize import (
    compute_canonical_hash)
from canonical.boundary_reference import (
    compute_boundary_context_hash,
    build_boundary_reference)
from canonical.invariants import (
    SOVEREIGNTY_PRINCIPLE, INVARIANT_VERSION)

router = APIRouter()


class CanonicalizeRequest(BaseModel):
    canonical_object: dict
    authority_context: AuthorityContext


@router.post("/canonicalize")
def canonicalize(payload: CanonicalizeRequest):
    canonical_hash = compute_canonical_hash(
        payload.canonical_object)
    boundary_context_hash = (
        compute_boundary_context_hash(
            payload.authority_context.dict()))
    boundary_reference = build_boundary_reference(
        canonical_hash, boundary_context_hash)
    return CanonicalBoundaryObject(
        canonical_hash=canonical_hash,
        boundary_context_hash=boundary_context_hash,
        boundary_reference=boundary_reference,
        canonical_timestamp=(
            datetime.utcnow().isoformat() + "Z"),
        sovereignty_principle=SOVEREIGNTY_PRINCIPLE,
        invariant_version=INVARIANT_VERSION
    )
