"""
Cross-domain admission transfer experiment v0.1 — Vendor Assurance vs Buyer Acceptance.

Synthetic domain only. Domain assumptions are test assumptions, not real procurement rules.

Invariants under test:
  A. Admission independence
  B. Authority independence
  C. Basis independence
  D. Judgment independence
  E. Domain independence (no ABAN vocabulary required)
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

EVIDENCE_DIR = (
    Path(__file__).resolve().parents[1] / "evidence" / "cross-domain-transfer-v01"
)

# --- Synthetic domain assumptions (not real procurement rules) ---
# declared_reference: formal SOW/MSA/procurement clause ties vendor assurance
#   to buyer acceptance review.
# flagged_authority: authorized buyer-side procurement function initiated review.
# Invocation requires >=2 independent authorization domains excluding invoked_by.
# Synthetic roles: Procurement Manager, Security / Risk Acceptance Lead.

PRODUCT_ID = "vendor-product-001"
SHARED_CONDITION = "Critical vulnerability remediation SLA <= 72 hours"
SHARED_POLICY = "SHARED-PROCUREMENT-ASSURANCE-REF-2026-v1"


def _valid_vendor_buyer_invocation() -> dict:
    return {
        "invoked_by": "vendor-buyer-coordination-node-01",
        "authority_reference": "formal-agreement://sow-msa-critical-supplier-2026-v1",
        "invocation_reason": (
            "Signed SOW establishes vendor assurance participation in "
            "buyer acceptance review."
        ),
        "timestamp": "2026-08-11T09:00:00Z",
        "sign_off": [
            {
                "authorized_by": "procurement-manager-014",
                "role": "Procurement Manager",
                "authorized_at": "2026-08-11T09:05:00Z",
            },
            {
                "authorized_by": "security-risk-acceptance-lead-022",
                "role": "Security / Risk Acceptance Lead",
                "authorized_at": "2026-08-11T09:10:00Z",
            },
        ],
    }


def _vendor_runtime(*, assurance: str, policy_reference: str, governing_condition: str,
                    execution_context: str = "vendor_release_security_review") -> dict:
    return {
        "decision": {"assurance": assurance, "product_id": PRODUCT_ID},
        "authority_context": {
            "authority_domain": "vendor_assurance",
            "policy_reference": policy_reference,
            "execution_context": execution_context,
            "admissibility_scope": "critical_supplier_onboarding",
            "governing_condition": governing_condition,
            "governing_condition_translation_ref": None,
        },
    }


def _buyer_runtime(*, acceptance: str, policy_reference: str, governing_condition: str,
                   execution_context: str = "buyer_resilience_acceptance_review") -> dict:
    return {
        "decision": {"acceptance": acceptance, "product_id": PRODUCT_ID},
        "authority_context": {
            "authority_domain": "buyer_acceptance",
            "policy_reference": policy_reference,
            "execution_context": execution_context,
            "admissibility_scope": "critical_supplier_onboarding",
            "governing_condition": governing_condition,
            "governing_condition_translation_ref": None,
        },
    }


def _vb2_comparison() -> dict:
    return {
        "runtime_a": _vendor_runtime(
            assurance="PASS",
            policy_reference="VENDOR-SEC-ASSURANCE-POLICY-2026-v1",
            governing_condition="release-security remediation gate satisfied",
        ),
        "runtime_b": _buyer_runtime(
            acceptance="REJECT",
            policy_reference="BUYER-CRITICAL-SUPPLIER-ACCEPTANCE-2026-v1",
            governing_condition="resilience acceptance threshold not met",
        ),
    }


def _vb3_comparison() -> dict:
    ctx = "vendor_release_security_review"
    return {
        "runtime_a": _vendor_runtime(
            assurance="PASS",
            policy_reference=SHARED_POLICY,
            governing_condition=SHARED_CONDITION,
            execution_context=ctx,
        ),
        "runtime_b": _buyer_runtime(
            acceptance="FAIL",
            policy_reference=SHARED_POLICY,
            governing_condition=SHARED_CONDITION,
            execution_context=ctx,
        ),
    }


# VB-2 engine probe (fixed before test execution):
# classification=FORMALLY_INCOMPARABLE
# fracture_boundary=['no_shared_canonical_reference',
#                    'no_governing_condition_translation_defined']


def test_vb1_no_relationship_constituted():
    """VB-1: no relationship — compare must not be invoked."""
    payload = {
        "case_admission": {"declared_relationship": "none"},
        "comparison": _vb2_comparison(),
    }
    r = client.post("/admit-and-compare", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["finding"] == "COORDINATION_NOT_CONSTITUTED"
    assert body["sub_reason"] == "no_relationship_declared"
    assert body["compare_invoked"] is False


def test_vb2_admission_pass_formally_incomparable():
    """VB-2: valid invocation, no comparison basis."""
    payload = {
        "case_admission": {
            "declared_relationship": "declared_reference",
            "invocation_record": _valid_vendor_buyer_invocation(),
        },
        "comparison": _vb2_comparison(),
    }
    r = client.post("/admit-and-compare", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["compare_invoked"] is True
    assert body["comparability_classification"] == "FORMALLY_INCOMPARABLE"
    assert body["fracture_boundary"] == [
        "no_shared_canonical_reference",
        "no_governing_condition_translation_defined",
    ]


def test_vb3_admission_pass_non_equivalent():
    """VB-3: shared basis, different judgments — NON_EQUIVALENT not incomparable."""
    payload = {
        "case_admission": {
            "declared_relationship": "declared_reference",
            "invocation_record": _valid_vendor_buyer_invocation(),
        },
        "comparison": _vb3_comparison(),
    }
    r = client.post("/admit-and-compare", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["compare_invoked"] is True
    assert body["comparability_classification"] == "NON_EQUIVALENT"
    assert body["fracture_boundary"] == []
    assert body["canonical_equivalent"] is False
    assert body["governance_equivalent"] is False


def test_vb4_invocation_unauthorized():
    """VB-4: relationship exists but invocation unauthorized."""
    record = _valid_vendor_buyer_invocation()
    record["sign_off"] = [
        {
            "authorized_by": "vendor-buyer-coordination-node-01",
            "role": "Procurement Manager",
            "authorized_at": "2026-08-11T09:05:00Z",
        },
        {
            "authorized_by": "security-risk-acceptance-lead-022",
            "role": "Security / Risk Acceptance Lead",
            "authorized_at": "2026-08-11T09:10:00Z",
        },
    ]
    payload = {
        "case_admission": {
            "declared_relationship": "declared_reference",
            "invocation_record": record,
        },
        "comparison": _vb2_comparison(),
    }
    r = client.post("/admit-and-compare", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["finding"] == "COORDINATION_NOT_CONSTITUTED"
    assert body["sub_reason"] == "invocation_unauthorized"
    assert body["compare_invoked"] is False


def test_invariant_a_admission_independence():
    """A: complete comparison payload cannot bypass absent relationship."""
    payload = {
        "case_admission": {"declared_relationship": "none"},
        "comparison": _vb3_comparison(),
    }
    r = client.post("/admit-and-compare", json=payload)
    body = r.json()
    assert body["compare_invoked"] is False


def test_invariant_b_authority_independence():
    """B: declared relationship does not alone authorize invocation."""
    payload = {
        "case_admission": {
            "declared_relationship": "declared_reference",
            "invocation_record": None,
        },
        "comparison": _vb2_comparison(),
    }
    r = client.post("/admit-and-compare", json=payload)
    body = r.json()
    assert body["finding"] == "COORDINATION_NOT_CONSTITUTED"
    assert body["sub_reason"] == "invocation_unauthorized"
    assert body["compare_invoked"] is False


def test_invariant_c_basis_independence():
    """C: admission pass does not imply comparison basis exists."""
    payload = {
        "case_admission": {
            "declared_relationship": "declared_reference",
            "invocation_record": _valid_vendor_buyer_invocation(),
        },
        "comparison": _vb2_comparison(),
    }
    r = client.post("/admit-and-compare", json=payload)
    body = r.json()
    assert body.get("compare_invoked") is True
    assert body["comparability_classification"] == "FORMALLY_INCOMPARABLE"


def test_invariant_d_judgment_independence():
    """D: different judgments with valid basis != formal incomparability."""
    payload = {
        "case_admission": {
            "declared_relationship": "declared_reference",
            "invocation_record": _valid_vendor_buyer_invocation(),
        },
        "comparison": _vb3_comparison(),
    }
    r = client.post("/admit-and-compare", json=payload)
    body = r.json()
    assert body["comparability_classification"] == "NON_EQUIVALENT"
    assert body["comparability_classification"] != "FORMALLY_INCOMPARABLE"


def test_invariant_e_domain_independence_no_aban_vocabulary():
    """E: Vendor/Buyer path must not require ABAN-specific strings."""
    forbidden = ("RAO", "ministry_of_agriculture", "ministry_of_finance", "protected_rule_ref")
    payload = {
        "case_admission": {
            "declared_relationship": "declared_reference",
            "invocation_record": _valid_vendor_buyer_invocation(),
        },
        "comparison": _vb3_comparison(),
    }
    serialized = json.dumps(payload)
    for token in forbidden:
        assert token not in serialized
    r = client.post("/admit-and-compare", json=payload)
    assert r.status_code == 200
    assert r.json()["compare_invoked"] is True


def test_flagged_authority_value_also_admits():
    """Experimental value flagged_authority uses same admission gate semantics."""
    payload = {
        "case_admission": {
            "declared_relationship": "flagged_authority",
            "invocation_record": _valid_vendor_buyer_invocation(),
        },
        "comparison": _vb3_comparison(),
    }
    r = client.post("/admit-and-compare", json=payload)
    assert r.status_code == 200
    assert r.json()["compare_invoked"] is True
