from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.admission_gate import evaluate_admission
from app.models.admission_request import CaseAdmission
from app.routes.compare import CompareRequest, compare

router = APIRouter()


class AdmitAndCompareRequest(BaseModel):
    case_admission: CaseAdmission
    comparison: Optional[CompareRequest] = None


@router.post("/admit-and-compare")
def admit_and_compare(payload: AdmitAndCompareRequest) -> dict:
    admission_result = evaluate_admission(payload.case_admission)

    if not admission_result["passed"]:
        return admission_result

    if payload.comparison is None:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "MISSING_COMPARISON_PAYLOAD",
                "message": (
                    "Admission passed, but runtime_a/runtime_b are "
                    "required before /compare can be invoked."
                ),
            },
        )

    compare_result = compare(payload.comparison)
    compare_result["compare_invoked"] = True
    return compare_result
