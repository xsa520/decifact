from typing import Optional, Literal
from pydantic import BaseModel, Field


class SignOffEntry(BaseModel):
    authorized_by: str
    role: str
    authorized_at: str


class InvocationRecord(BaseModel):
    invoked_by: str
    authority_reference: str
    invocation_reason: str
    timestamp: str
    sign_off: list[SignOffEntry] = Field(default_factory=list)


class CaseAdmission(BaseModel):
    declared_relationship: Literal[
        "none",
        # Existing ABAN historical values
        "protected_rule_ref",
        "RAO_officer_flagged",
        # Cross-domain experiment values
        "declared_reference",
        "flagged_authority",
    ]
    invocation_record: Optional[InvocationRecord] = None
