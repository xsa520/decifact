from app.models.admission_request import CaseAdmission


def evaluate_admission(admission: CaseAdmission) -> dict:
    """
    Returns either:
      {"passed": False, "finding": "COORDINATION_NOT_CONSTITUTED",
       "sub_reason": ..., "compare_invoked": False}
    or:
      {"passed": True}
    """
    if admission.declared_relationship == "none":
        return {
            "passed": False,
            "finding": "COORDINATION_NOT_CONSTITUTED",
            "sub_reason": "no_relationship_declared",
            "compare_invoked": False,
        }

    record = admission.invocation_record
    if record is None:
        return {
            "passed": False,
            "finding": "COORDINATION_NOT_CONSTITUTED",
            "sub_reason": "invocation_unauthorized",
            "compare_invoked": False,
        }

    # Rindai's 2026-07-22 hardening requirement:
    # sign_off must exclude invoked_by, and must represent at least
    # two DISTINCT entities (not just two distinct role labels).
    distinct_signers = {
        s.authorized_by for s in record.sign_off
        if s.authorized_by != record.invoked_by
    }

    if len(record.sign_off) < 2 or len(distinct_signers) < 2:
        return {
            "passed": False,
            "finding": "COORDINATION_NOT_CONSTITUTED",
            "sub_reason": "invocation_unauthorized",
            "compare_invoked": False,
        }

    return {"passed": True}
