from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _base_comparison():
    return {
        "runtime_a": {
            "decision": {"intent": "deny_subsidy", "target": "national_id://synthetic-0001"},
            "authority_context": {
                "authority_domain": "ministry_of_agriculture",
                "policy_reference": "AGRI-SEED-INPUT-ELIGIBILITY-2025-v2",
                "execution_context": "subsidy_eligibility_review",
                "admissibility_scope": "national_farmer_registry",
                "governing_condition": "land-size eligibility cutoff breached",
            },
        },
        "runtime_b": {
            "decision": {"intent": "deny_credit", "target": "national_id://synthetic-0001"},
            "authority_context": {
                "authority_domain": "ministry_of_finance",
                "policy_reference": "FIN-SME-CREDIT-ELIGIBILITY-2025-v1",
                "execution_context": "credit_eligibility_review",
                "admissibility_scope": "national_credit_registry",
                "governing_condition": "debt-service coverage ratio below required minimum",
            },
        },
    }


def test_3a_no_relationship_declared():
    payload = {
        "case_admission": {"declared_relationship": "none"},
        "comparison": _base_comparison(),
    }
    r = client.post("/admit-and-compare", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["finding"] == "COORDINATION_NOT_CONSTITUTED"
    assert body["sub_reason"] == "no_relationship_declared"
    assert body["compare_invoked"] is False


def test_3b_valid_dual_signoff_calls_compare():
    payload = {
        "case_admission": {
            "declared_relationship": "protected_rule_ref",
            "invocation_record": {
                "invoked_by": "RAO-node-agri-fin-liaison-07",
                "authority_reference": "protected_rule://cross-ministry-fraud-screen-2025-v1",
                "invocation_reason": "Protected rule requires a cross-ministry coordination review.",
                "timestamp": "2026-07-15T09:12:00Z",
                "sign_off": [
                    {"authorized_by": "RAO-officer-0231", "role": "RAO_Officer", "authorized_at": "2026-07-15T09:14:00Z"},
                    {"authorized_by": "ministry_of_finance-liaison-014", "role": "second_ministry_representative", "authorized_at": "2026-07-15T09:20:00Z"},
                ],
            },
        },
        "comparison": _base_comparison(),
    }
    r = client.post("/admit-and-compare", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["compare_invoked"] is True
    assert body["comparability_classification"] == "FORMALLY_INCOMPARABLE"
    assert "no_shared_canonical_reference" in body["fracture_boundary"]
    assert "no_governing_condition_translation_defined" in body["fracture_boundary"]


def test_3c_single_signoff_rejected():
    payload = {
        "case_admission": {
            "declared_relationship": "protected_rule_ref",
            "invocation_record": {
                "invoked_by": "RAO-node-agri-fin-liaison-07",
                "authority_reference": "protected_rule://cross-ministry-fraud-screen-2025-v1",
                "invocation_reason": "Protected rule requires a cross-ministry coordination review.",
                "timestamp": "2026-07-15T09:12:00Z",
                "sign_off": [
                    {"authorized_by": "RAO-node-agri-fin-liaison-07", "role": "RAO_Officer", "authorized_at": "2026-07-15T09:12:00Z"},
                ],
            },
        },
        "comparison": _base_comparison(),
    }
    r = client.post("/admit-and-compare", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["finding"] == "COORDINATION_NOT_CONSTITUTED"
    assert body["sub_reason"] == "invocation_unauthorized"
    assert body["compare_invoked"] is False


def test_3d_invoker_self_sign_plus_second_rejected():
    """Rindai's 2026-07-22 hardening case: invoking node self-signs
    alongside one genuine second party. Must still be rejected —
    two sign_off entries is not the same as two distinct entities."""
    payload = {
        "case_admission": {
            "declared_relationship": "protected_rule_ref",
            "invocation_record": {
                "invoked_by": "RAO-node-agri-fin-liaison-07",
                "authority_reference": "protected_rule://cross-ministry-fraud-screen-2025-v1",
                "invocation_reason": "Protected rule requires a cross-ministry coordination review.",
                "timestamp": "2026-07-15T09:12:00Z",
                "sign_off": [
                    {"authorized_by": "RAO-node-agri-fin-liaison-07", "role": "RAO_Officer", "authorized_at": "2026-07-15T09:12:00Z"},
                    {"authorized_by": "ministry_of_finance-liaison-014", "role": "second_ministry_representative", "authorized_at": "2026-07-15T09:20:00Z"},
                ],
            },
        },
        "comparison": _base_comparison(),
    }
    r = client.post("/admit-and-compare", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["finding"] == "COORDINATION_NOT_CONSTITUTED"
    assert body["sub_reason"] == "invocation_unauthorized"
    assert body["compare_invoked"] is False


def _valid_dual_signoff_admission():
    return {
        "declared_relationship": "protected_rule_ref",
        "invocation_record": {
            "invoked_by": "RAO-node-agri-fin-liaison-07",
            "authority_reference": "protected_rule://cross-ministry-fraud-screen-2025-v1",
            "invocation_reason": "Protected rule requires a cross-ministry coordination review.",
            "timestamp": "2026-07-15T09:12:00Z",
            "sign_off": [
                {"authorized_by": "RAO-officer-0231", "role": "RAO_Officer", "authorized_at": "2026-07-15T09:14:00Z"},
                {"authorized_by": "ministry_of_finance-liaison-014", "role": "second_ministry_representative", "authorized_at": "2026-07-15T09:20:00Z"},
            ],
        },
    }


def test_translation_fracture_alone_drives_formally_incomparable():
    """Gap identified 2026-07-22: same policy_reference (so
    no_shared_canonical_reference does NOT fire), but different
    governing_condition with no translation ref declared. This must
    independently produce FORMALLY_INCOMPARABLE — the translation
    fracture must drive classification, not just appear in
    fracture_boundary while classification falls through to
    EQUIVALENT/NON_EQUIVALENT."""
    comparison = _base_comparison()
    # Force identical policy_reference on both sides so the
    # canonical-reference check alone would NOT trigger
    # FORMALLY_INCOMPARABLE.
    comparison["runtime_a"]["authority_context"]["policy_reference"] = "SHARED-CROSS-MINISTRY-REF-v1"
    comparison["runtime_b"]["authority_context"]["policy_reference"] = "SHARED-CROSS-MINISTRY-REF-v1"
    # governing_condition still differs, no translation_ref set on either side.
    payload = {
        "case_admission": _valid_dual_signoff_admission(),
        "comparison": comparison,
    }
    r = client.post("/admit-and-compare", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["compare_invoked"] is True
    assert body["comparability_classification"] == "FORMALLY_INCOMPARABLE"
    assert "no_governing_condition_translation_defined" in body["fracture_boundary"]
    assert "no_shared_canonical_reference" not in body["fracture_boundary"]


def test_admission_fail_does_not_require_comparison_payload():
    """Gap identified 2026-07-22: when declared_relationship = none,
    the case should be resolvable without ever supplying a
    comparison payload — the relationship was never constituted, so
    there is nothing to compare in the first place."""
    payload = {
        "case_admission": {"declared_relationship": "none"},
    }
    r = client.post("/admit-and-compare", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["finding"] == "COORDINATION_NOT_CONSTITUTED"
    assert body["sub_reason"] == "no_relationship_declared"
    assert body["compare_invoked"] is False


def test_admission_pass_without_comparison_returns_422():
    """If admission passes but no comparison payload was given, this
    must be a distinct HTTP failure (422) — not a 200 with a mixed
    'passed: true' / 'operation actually incomplete' response that a
    machine caller could misread as success."""
    payload = {
        "case_admission": _valid_dual_signoff_admission(),
    }
    r = client.post("/admit-and-compare", json=payload)
    assert r.status_code == 422
    body = r.json()
    assert body["detail"]["error"] == "MISSING_COMPARISON_PAYLOAD"
