from pydantic import BaseModel
from typing import Optional


class AuthorityContext(BaseModel):
    authority_domain: str
    policy_reference: str
    execution_context: str
    admissibility_scope: Optional[str] = None


class CanonicalBoundaryObject(BaseModel):
    canonical_hash: str
    boundary_context_hash: str
    boundary_reference: str
    canonical_timestamp: str
    sovereignty_principle: str
    invariant_version: str = "1.0.0"
    replayable: bool = True
