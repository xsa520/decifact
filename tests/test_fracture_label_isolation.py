"""
Orthogonal fracture-label isolation matrix (ABAN × Decifact v0.3).

Proves trigger conditions and classification effects for exploratory labels:
  - decision_object_divergence
  - authority_assumption_divergence

Does not expand the confirmed ABAN fracture set.
Uses POST /compare directly for all isolation cases.
J/K reproduce the comparison payload shapes used by the current
3b/3e admission-wrapper fixtures; they do not retest admission routing.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

EVIDENCE_DIR = Path(__file__).resolve().parents[1] / "evidence" / "aban-v0.3-api-test"
CONFIRMED = {
    "no_shared_canonical_reference",
    "no_governing_condition_translation_defined",
}
EXPLORATORY = {
    "decision_object_divergence",
    "authority_assumption_divergence",
}


def _baseline_runtime() -> dict[str, Any]:
    return {
        "decision": {
            "intent": "deny_subsidy",
            "target": "national_id://synthetic-0001",
        },
        "authority_context": {
            "authority_domain": "ministry_of_agriculture",
            "policy_reference": "SHARED-CROSS-MINISTRY-REF-v1",
            "execution_context": "subsidy_eligibility_review",
            "admissibility_scope": "national_farmer_registry",
            "governing_condition": "land-size eligibility cutoff breached",
            "governing_condition_translation_ref": None,
        },
    }


def _compare(runtime_a: dict, runtime_b: dict) -> dict:
    r = client.post(
        "/compare",
        json={"runtime_a": runtime_a, "runtime_b": runtime_b},
    )
    assert r.status_code == 200, r.text
    return r.json()


def _record(
    case_id: str,
    changed_fields: list[str],
    body: dict,
    *,
    compare_invoked: bool = True,
    notes: str = "",
) -> dict:
    fb = body.get("fracture_boundary") or []
    return {
        "case_id": case_id,
        "changed_fields": changed_fields,
        "comparability_classification": body.get("comparability_classification"),
        "fracture_boundary": fb,
        "canonical_equivalent": body.get("canonical_equivalent"),
        "governance_equivalent": body.get("governance_equivalent"),
        "replayable": body.get("replayable"),
        "decision_object_divergence": "decision_object_divergence" in fb,
        "authority_assumption_divergence": "authority_assumption_divergence" in fb,
        "confirmed_fractures": [x for x in fb if x in CONFIRMED],
        "exploratory_labels": [x for x in fb if x in EXPLORATORY],
        "compare_invoked": compare_invoked,
        "notes": notes,
    }


# ---------------------------------------------------------------------------
# Baseline
# ---------------------------------------------------------------------------


def test_baseline_identical_no_exploratory_labels():
    a = _baseline_runtime()
    b = copy.deepcopy(a)
    body = _compare(a, b)
    assert body["comparability_classification"] == "EQUIVALENT"
    assert body["fracture_boundary"] == []
    assert body["canonical_equivalent"] is True
    assert body["governance_equivalent"] is True
    assert "decision_object_divergence" not in body["fracture_boundary"]
    assert "authority_assumption_divergence" not in body["fracture_boundary"]


# ---------------------------------------------------------------------------
# A–B decision-only
# ---------------------------------------------------------------------------


def test_case_a_decision_intent_only():
    a = _baseline_runtime()
    b = copy.deepcopy(a)
    b["decision"]["intent"] = "deny_credit"
    body = _compare(a, b)
    assert body["canonical_equivalent"] is False
    assert body["governance_equivalent"] is True
    assert "decision_object_divergence" in body["fracture_boundary"]
    assert "authority_assumption_divergence" not in body["fracture_boundary"]
    assert not (CONFIRMED & set(body["fracture_boundary"]))
    assert body["comparability_classification"] == "NON_EQUIVALENT"


def test_case_b_decision_target_only():
    a = _baseline_runtime()
    b = copy.deepcopy(a)
    b["decision"]["target"] = "national_id://synthetic-9999"
    body = _compare(a, b)
    assert body["canonical_equivalent"] is False
    assert body["governance_equivalent"] is True
    assert "decision_object_divergence" in body["fracture_boundary"]
    assert "authority_assumption_divergence" not in body["fracture_boundary"]
    assert body["comparability_classification"] == "NON_EQUIVALENT"


# ---------------------------------------------------------------------------
# C–I authority-only (and translation variants)
# ---------------------------------------------------------------------------


def test_case_c_authority_domain_only():
    a = _baseline_runtime()
    b = copy.deepcopy(a)
    b["authority_context"]["authority_domain"] = "ministry_of_finance"
    body = _compare(a, b)
    assert body["canonical_equivalent"] is True
    assert body["governance_equivalent"] is False
    assert "authority_assumption_divergence" in body["fracture_boundary"]
    assert "decision_object_divergence" not in body["fracture_boundary"]
    assert not (CONFIRMED & set(body["fracture_boundary"]))
    assert body["comparability_classification"] == "NON_EQUIVALENT"


def test_case_d_policy_reference_only():
    a = _baseline_runtime()
    b = copy.deepcopy(a)
    b["authority_context"]["policy_reference"] = "OTHER-POLICY-REF-v1"
    body = _compare(a, b)
    assert body["canonical_equivalent"] is True
    assert body["governance_equivalent"] is False
    assert "no_shared_canonical_reference" in body["fracture_boundary"]
    assert "authority_assumption_divergence" in body["fracture_boundary"]
    assert "decision_object_divergence" not in body["fracture_boundary"]
    assert body["comparability_classification"] == "FORMALLY_INCOMPARABLE"


def test_case_e_governing_condition_only_no_translation():
    a = _baseline_runtime()
    b = copy.deepcopy(a)
    b["authority_context"]["governing_condition"] = (
        "debt-service coverage ratio below required minimum"
    )
    # both translation_ref remain None
    body = _compare(a, b)
    assert body["canonical_equivalent"] is True
    assert body["governance_equivalent"] is False
    assert "no_governing_condition_translation_defined" in body["fracture_boundary"]
    assert "authority_assumption_divergence" in body["fracture_boundary"]
    assert "decision_object_divergence" not in body["fracture_boundary"]
    assert body["comparability_classification"] == "FORMALLY_INCOMPARABLE"


def test_case_f_governing_condition_only_shared_valid_translation_ref():
    """
    Isolate: raw boundary-hash still emits authority_assumption_divergence
    even though confirmed translation fracture is absent.
    """
    a = _baseline_runtime()
    b = copy.deepcopy(a)
    shared_ref = "translation://agri-fin-gc-bridge-v1"
    a["authority_context"]["governing_condition_translation_ref"] = shared_ref
    b["authority_context"]["governing_condition_translation_ref"] = shared_ref
    b["authority_context"]["governing_condition"] = (
        "debt-service coverage ratio below required minimum"
    )
    body = _compare(a, b)
    assert body["canonical_equivalent"] is True
    assert body["governance_equivalent"] is False
    assert "no_governing_condition_translation_defined" not in body["fracture_boundary"]
    assert "no_shared_canonical_reference" not in body["fracture_boundary"]
    assert "authority_assumption_divergence" in body["fracture_boundary"]
    assert "decision_object_divergence" not in body["fracture_boundary"]
    assert body["comparability_classification"] == "NON_EQUIVALENT"


def test_case_g_execution_context_only():
    a = _baseline_runtime()
    b = copy.deepcopy(a)
    b["authority_context"]["execution_context"] = "credit_eligibility_review"
    body = _compare(a, b)
    assert body["canonical_equivalent"] is True
    assert body["governance_equivalent"] is False
    assert "authority_assumption_divergence" in body["fracture_boundary"]
    assert "decision_object_divergence" not in body["fracture_boundary"]
    assert not (CONFIRMED & set(body["fracture_boundary"]))
    assert body["comparability_classification"] == "NON_EQUIVALENT"


def test_case_h_admissibility_scope_only():
    a = _baseline_runtime()
    b = copy.deepcopy(a)
    b["authority_context"]["admissibility_scope"] = "national_credit_registry"
    body = _compare(a, b)
    assert body["canonical_equivalent"] is True
    assert body["governance_equivalent"] is False
    assert "authority_assumption_divergence" in body["fracture_boundary"]
    assert "decision_object_divergence" not in body["fracture_boundary"]
    assert "acceptance_context_mismatch" in body["fracture_boundary"]
    assert not (CONFIRMED & set(body["fracture_boundary"]))
    assert body["comparability_classification"] == "NON_EQUIVALENT"


def test_case_i_translation_ref_only_conditions_identical():
    a = _baseline_runtime()
    b = copy.deepcopy(a)
    a["authority_context"]["governing_condition_translation_ref"] = (
        "translation://side-a-only-v1"
    )
    b["authority_context"]["governing_condition_translation_ref"] = (
        "translation://side-b-only-v1"
    )
    # governing_condition identical → translation confirmed fracture must not fire
    body = _compare(a, b)
    assert body["canonical_equivalent"] is True
    assert body["governance_equivalent"] is False
    assert "no_governing_condition_translation_defined" not in body["fracture_boundary"]
    assert "authority_assumption_divergence" in body["fracture_boundary"]
    assert "decision_object_divergence" not in body["fracture_boundary"]
    assert body["comparability_classification"] == "NON_EQUIVALENT"


# ---------------------------------------------------------------------------
# J–K multi-field fixtures (current 3b / 3e)
# ---------------------------------------------------------------------------


def test_case_j_current_3b_multi_field():
    a = {
        "decision": {
            "intent": "deny_subsidy",
            "target": "national_id://synthetic-0001",
        },
        "authority_context": {
            "authority_domain": "ministry_of_agriculture",
            "policy_reference": "AGRI-SEED-INPUT-ELIGIBILITY-2025-v2",
            "execution_context": "subsidy_eligibility_review",
            "admissibility_scope": "national_farmer_registry",
            "governing_condition": "land-size eligibility cutoff breached",
        },
    }
    b = {
        "decision": {
            "intent": "deny_credit",
            "target": "national_id://synthetic-0001",
        },
        "authority_context": {
            "authority_domain": "ministry_of_finance",
            "policy_reference": "FIN-SME-CREDIT-ELIGIBILITY-2025-v1",
            "execution_context": "credit_eligibility_review",
            "admissibility_scope": "national_credit_registry",
            "governing_condition": (
                "debt-service coverage ratio below required minimum"
            ),
        },
    }
    body = _compare(a, b)
    assert body["comparability_classification"] == "FORMALLY_INCOMPARABLE"
    assert "decision_object_divergence" in body["fracture_boundary"]
    assert "authority_assumption_divergence" not in body["fracture_boundary"]
    assert "no_shared_canonical_reference" in body["fracture_boundary"]
    assert "no_governing_condition_translation_defined" in body["fracture_boundary"]


def test_case_k_current_3e_multi_field():
    a = {
        "decision": {
            "intent": "deny_subsidy",
            "target": "national_id://synthetic-0001",
        },
        "authority_context": {
            "authority_domain": "ministry_of_agriculture",
            "policy_reference": "SHARED-CROSS-MINISTRY-REF-v1",
            "execution_context": "subsidy_eligibility_review",
            "admissibility_scope": "national_farmer_registry",
            "governing_condition": "land-size eligibility cutoff breached",
        },
    }
    b = {
        "decision": {
            "intent": "deny_subsidy",
            "target": "national_id://synthetic-0001",
        },
        "authority_context": {
            "authority_domain": "ministry_of_finance",
            "policy_reference": "SHARED-CROSS-MINISTRY-REF-v1",
            "execution_context": "subsidy_eligibility_review",
            "admissibility_scope": "national_farmer_registry",
            "governing_condition": (
                "debt-service coverage ratio below required minimum"
            ),
        },
    }
    body = _compare(a, b)
    assert body["comparability_classification"] == "FORMALLY_INCOMPARABLE"
    assert "authority_assumption_divergence" in body["fracture_boundary"]
    assert "decision_object_divergence" not in body["fracture_boundary"]
    assert "no_governing_condition_translation_defined" in body["fracture_boundary"]
    assert "no_shared_canonical_reference" not in body["fracture_boundary"]


# ---------------------------------------------------------------------------
# L — masking
# ---------------------------------------------------------------------------


def test_case_l_masking_decision_and_authority_together():
    """
    Decision + authority both differ; shared policy_reference; identical
    governing_condition → no confirmed fracture. Proves exploratory masking.
    """
    a = _baseline_runtime()
    b = copy.deepcopy(a)
    b["decision"]["intent"] = "deny_credit"
    b["authority_context"]["authority_domain"] = "ministry_of_finance"
    body = _compare(a, b)
    assert body["canonical_equivalent"] is False
    assert body["governance_equivalent"] is False
    assert "decision_object_divergence" in body["fracture_boundary"]
    assert "authority_assumption_divergence" not in body["fracture_boundary"]
    assert not (CONFIRMED & set(body["fracture_boundary"]))
    assert body["comparability_classification"] == "NON_EQUIVALENT"


# ---------------------------------------------------------------------------
# M — canonicalizer ignored-field check
# ---------------------------------------------------------------------------


def test_case_m_decision_hash_keyed_field_ignored_by_canonicalizer():
    """
    Top-level decision key containing 'hash' is cleared by
    compute_canonical_hash — must not emit decision_object_divergence.
    Executable because RuntimeInput.decision is an unconstrained dict.
    """
    a = _baseline_runtime()
    b = copy.deepcopy(a)
    a["decision"]["content_hash"] = "aaa-side-a"
    b["decision"]["content_hash"] = "bbb-side-b-different"
    body = _compare(a, b)
    assert body["canonical_equivalent"] is True
    assert body["governance_equivalent"] is True
    assert "decision_object_divergence" not in body["fracture_boundary"]
    assert body["comparability_classification"] == "EQUIVALENT"
    assert body["fracture_boundary"] == []


def test_exploratory_labels_do_not_independently_drive_formally_incomparable():
    """Safety: decision/authority hash divergence alone → NON_EQUIVALENT."""
    # decision-only
    a = _baseline_runtime()
    b = copy.deepcopy(a)
    b["decision"]["intent"] = "deny_credit"
    body = _compare(a, b)
    assert body["comparability_classification"] != "FORMALLY_INCOMPARABLE"
    # authority-only (non-confirmed field)
    a2 = _baseline_runtime()
    b2 = copy.deepcopy(a2)
    b2["authority_context"]["execution_context"] = "other_review"
    body2 = _compare(a2, b2)
    assert body2["comparability_classification"] != "FORMALLY_INCOMPARABLE"
    assert "authority_assumption_divergence" in body2["fracture_boundary"]


# ---------------------------------------------------------------------------
# Evidence dump (runs as part of suite; writes JSON for Gate package)
# ---------------------------------------------------------------------------


def test_write_isolation_results_json():
    rows: list[dict] = []

    # Baseline
    a = _baseline_runtime()
    rows.append(
        _record(
            "baseline",
            [],
            _compare(a, copy.deepcopy(a)),
            notes="identical runtimes",
        )
    )

    # A
    a, b = _baseline_runtime(), copy.deepcopy(_baseline_runtime())
    b["decision"]["intent"] = "deny_credit"
    rows.append(_record("A", ["decision.intent"], _compare(a, b)))

    # B
    a, b = _baseline_runtime(), copy.deepcopy(_baseline_runtime())
    b["decision"]["target"] = "national_id://synthetic-9999"
    rows.append(_record("B", ["decision.target"], _compare(a, b)))

    # C
    a, b = _baseline_runtime(), copy.deepcopy(_baseline_runtime())
    b["authority_context"]["authority_domain"] = "ministry_of_finance"
    rows.append(_record("C", ["authority_context.authority_domain"], _compare(a, b)))

    # D
    a, b = _baseline_runtime(), copy.deepcopy(_baseline_runtime())
    b["authority_context"]["policy_reference"] = "OTHER-POLICY-REF-v1"
    rows.append(_record("D", ["authority_context.policy_reference"], _compare(a, b)))

    # E
    a, b = _baseline_runtime(), copy.deepcopy(_baseline_runtime())
    b["authority_context"]["governing_condition"] = (
        "debt-service coverage ratio below required minimum"
    )
    rows.append(
        _record(
            "E",
            ["authority_context.governing_condition"],
            _compare(a, b),
            notes="no translation_ref",
        )
    )

    # F
    a, b = _baseline_runtime(), copy.deepcopy(_baseline_runtime())
    ref = "translation://agri-fin-gc-bridge-v1"
    a["authority_context"]["governing_condition_translation_ref"] = ref
    b["authority_context"]["governing_condition_translation_ref"] = ref
    b["authority_context"]["governing_condition"] = (
        "debt-service coverage ratio below required minimum"
    )
    rows.append(
        _record(
            "F",
            [
                "authority_context.governing_condition",
                "authority_context.governing_condition_translation_ref (same on both)",
            ],
            _compare(a, b),
            notes="shared valid translation_ref; confirmed translation fracture absent",
        )
    )

    # G
    a, b = _baseline_runtime(), copy.deepcopy(_baseline_runtime())
    b["authority_context"]["execution_context"] = "credit_eligibility_review"
    rows.append(_record("G", ["authority_context.execution_context"], _compare(a, b)))

    # H
    a, b = _baseline_runtime(), copy.deepcopy(_baseline_runtime())
    b["authority_context"]["admissibility_scope"] = "national_credit_registry"
    rows.append(
        _record(
            "H",
            ["authority_context.admissibility_scope"],
            _compare(a, b),
            notes="may also emit acceptance_context_mismatch",
        )
    )

    # I
    a, b = _baseline_runtime(), copy.deepcopy(_baseline_runtime())
    a["authority_context"]["governing_condition_translation_ref"] = (
        "translation://side-a-only-v1"
    )
    b["authority_context"]["governing_condition_translation_ref"] = (
        "translation://side-b-only-v1"
    )
    rows.append(
        _record(
            "I",
            ["authority_context.governing_condition_translation_ref"],
            _compare(a, b),
            notes="governing_condition identical",
        )
    )

    # J — 3b
    rows.append(
        _record(
            "J",
            ["multi-field 3b structure"],
            _compare(
                {
                    "decision": {
                        "intent": "deny_subsidy",
                        "target": "national_id://synthetic-0001",
                    },
                    "authority_context": {
                        "authority_domain": "ministry_of_agriculture",
                        "policy_reference": "AGRI-SEED-INPUT-ELIGIBILITY-2025-v2",
                        "execution_context": "subsidy_eligibility_review",
                        "admissibility_scope": "national_farmer_registry",
                        "governing_condition": "land-size eligibility cutoff breached",
                    },
                },
                {
                    "decision": {
                        "intent": "deny_credit",
                        "target": "national_id://synthetic-0001",
                    },
                    "authority_context": {
                        "authority_domain": "ministry_of_finance",
                        "policy_reference": "FIN-SME-CREDIT-ELIGIBILITY-2025-v1",
                        "execution_context": "credit_eligibility_review",
                        "admissibility_scope": "national_credit_registry",
                        "governing_condition": (
                            "debt-service coverage ratio below required minimum"
                        ),
                    },
                },
            ),
            notes="current 3b multi-field fixture",
        )
    )

    # K — 3e
    rows.append(
        _record(
            "K",
            ["multi-field 3e structure"],
            _compare(
                {
                    "decision": {
                        "intent": "deny_subsidy",
                        "target": "national_id://synthetic-0001",
                    },
                    "authority_context": {
                        "authority_domain": "ministry_of_agriculture",
                        "policy_reference": "SHARED-CROSS-MINISTRY-REF-v1",
                        "execution_context": "subsidy_eligibility_review",
                        "admissibility_scope": "national_farmer_registry",
                        "governing_condition": "land-size eligibility cutoff breached",
                    },
                },
                {
                    "decision": {
                        "intent": "deny_subsidy",
                        "target": "national_id://synthetic-0001",
                    },
                    "authority_context": {
                        "authority_domain": "ministry_of_finance",
                        "policy_reference": "SHARED-CROSS-MINISTRY-REF-v1",
                        "execution_context": "subsidy_eligibility_review",
                        "admissibility_scope": "national_farmer_registry",
                        "governing_condition": (
                            "debt-service coverage ratio below required minimum"
                        ),
                    },
                },
            ),
            notes="current 3e multi-field fixture",
        )
    )

    # L
    a, b = _baseline_runtime(), copy.deepcopy(_baseline_runtime())
    b["decision"]["intent"] = "deny_credit"
    b["authority_context"]["authority_domain"] = "ministry_of_finance"
    rows.append(
        _record(
            "L",
            ["decision.intent", "authority_context.authority_domain"],
            _compare(a, b),
            notes="masking case: authority exploratory suppressed",
        )
    )

    # M
    a, b = _baseline_runtime(), copy.deepcopy(_baseline_runtime())
    a["decision"]["content_hash"] = "aaa-side-a"
    b["decision"]["content_hash"] = "bbb-side-b-different"
    rows.append(
        _record(
            "M",
            ["decision.content_hash"],
            _compare(a, b),
            notes="EXECUTABLE: key contains 'hash'; cleared by canonicalizer",
        )
    )

    payload = {
        "owner_repository": "C:\\Users\\xsa52\\decifact",
        "branch": "feature/aban-admission-wrapper-v03",
        "matrix_cases": rows,
        "review_conclusion": {
            "classification": "OVER-BROAD / UNSTABLE DIAGNOSTICS",
            "basis": [
                "hash-layer triggers",
                "mutually exclusive emission",
                "authority divergence masking",
                "field-level over-breadth",
            ],
        },
        "confirmed_fracture_set": sorted(CONFIRMED),
        "exploratory_diagnostic_set": sorted(EXPLORATORY),
    }
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out = EVIDENCE_DIR / "fracture-label-isolation-results.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    assert out.exists()
