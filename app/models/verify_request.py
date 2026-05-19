from typing import Any

from pydantic import BaseModel


class VerifyRequest(BaseModel):
    decision_a: dict[str, Any]
    decision_b: dict[str, Any]
