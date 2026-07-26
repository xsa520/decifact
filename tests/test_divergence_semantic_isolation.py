"""
Decision/Authority divergence semantic isolation — Layer 3 remainder
(ABAN × Decifact v0.3, spec revision v0.3.1:
docs/experiments/decision-authority-divergence-isolation-v03.md).

Coverage-mapping note (read before adding cases here):

Layer 1 (mechanical baseline, M1-M4) and part of Layer 3 (S3, S4, S7)
from the frozen spec are ALREADY COVERED by
tests/test_fracture_label_isolation.py and are NOT re-implemented in
this file:

    M1 (baseline, no divergence)         -> test_baseline_identical_no_removed_public_labels
    M2 (decision only diverges)          -> test_case_a_decision_intent_only
    M3 (authority_domain only diverges)  -> test_case_c_authority_domain_only
    M4 (both diverge simultaneously)     -> test_case_l_masking_decision_and_authority_together
                                             (directly confirms canonical_equivalent and
                                             governance_equivalent fire independently and
                                             simultaneously -- no masking at the boolean
                                             level; this was the spec's falsification
                                             condition, and it already passes today)
    S3 (admissibility_scope only)        -> test_case_h_admissibility_scope_only
    S4 (authority_domain only)           -> same case as M3 / test_case_c
    S7 (both diverge, superset of M4)    -> same case as M4 / test_case_l
    R1 (JSON key-order invariance)       -> guaranteed structurally by
                                             sort_keys=True in
                                             canonical/canonicalize.py and
                                             canonical/boundary_reference.py;
                                             no dedicated test needed
    R2 (cosmetic field, e.g. refusal_reason) -> covered in spirit by
                                             test_case_m (canonicalizer
                                             ignores a hash-adjacent field)
    R4 (omitted vs. explicit default)    -> partially covered by
                                             test_case_i (translation_ref
                                             asymmetry); not identical to
                                             R4 but same family

What was NOT already covered, and is added in this file: S5a and S6.
Both are genuine, unresolved ABAN semantic questions -- not mechanical
field-isolation cases -- so both are characterization tests per the
spec's Test-type classification: they record the current mechanical
result as evidence, they do NOT assert a domain-correctness verdict,
and their semantic disposition remains UNRESOLVED_SEMANTICS pending
Rindai input.

D1-D3 (deferred schema questions) remain doc-only; there is no
executable input surface for them under the current schema, so no
test is added for them here or anywhere.

No production code is changed in this commit.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

EVIDENCE_DIR = Path(__file__).resolve().parents[1] / "evidence" / "aban-v0.3-api-test"


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


def _characterization_record(
    case_id: str,
    open_question: str,
    changed_fields: list[str],
    body: dict,
) -> dict:
    """
    Record the actual mechanical result as evidence. Do NOT assert a
    domain-correctness verdict here -- semantic disposition for both
    S5a and S6 is UNRESOLVED_SEMANTICS pending Rindai input, per the
    frozen spec's Test-type classification.
    """
    return {
        "case_id": case_id,
        "open_question": open_question,
        "changed_fields": changed_fields,
        "canonical_equivalent": body.get("canonical_equivalent"),
        "governance_equivalent": body.get("governance_equivalent"),
        "comparability_classification": body.get("comparability_classification"),
        "fracture_boundary": body.get("fracture_boundary"),
        "mechanical_disposition": (
            "canonical_decision_hash_mismatch="
            f"{not body.get('canonical_equivalent')}, "
            "authority_context_hash_mismatch="
            f"{not body.get('governance_equivalent')}"
        ),
        "semantic_disposition": "UNRESOLVED_SEMANTICS",
    }


def _characterize_s5a() -> dict:
    """
    S5a: same decision_intent, same policy_reference, same
    governing_condition; only citizen_reference (case-instance
    target) differs.

    Open question (unresolved, not answered by this test): is
    canonical_decision_hash intended to represent decision-instance
    identity (which case this is) or decision semantic form (what
    kind of decision this is)? If the former, this case's mechanical
    result should be a mismatch by design. If the latter, a mismatch
    here would indicate the hash is over-scoped. This does not
    decide between the two -- it records which one the current
    implementation actually does.
    """
    a = _baseline_runtime()
    b = copy.deepcopy(a)
    b["decision"]["target"] = "national_id://synthetic-9999"

    body = _compare(a, b)

    return _characterization_record(
        "S5a",
        open_question=(
            "Does canonical_decision_hash scope over case-instance "
            "identity (citizen_reference / decision.target), or only "
            "over decision semantic form (intent, governing policy)?"
        ),
        changed_fields=["decision.target"],
        body=body,
    )


def test_s5a_case_instance_identity_characterization():
    record = _characterize_s5a()
    # No assertion on domain correctness. Only confirm the case ran
    # and produced a well-formed record -- the mechanical fact itself
    # is evidence for Rindai's review, not a verdict this test renders.
    assert record["semantic_disposition"] == "UNRESOLVED_SEMANTICS"
    assert record["comparability_classification"] is not None


def _characterize_s6() -> dict:
    """
    S6: different textual intent labels, constructed to represent
    what a domain expert *might* consider "the same underlying
    decision, differently labeled" -- e.g. a jurisdiction-specific
    synonym for the same governed action.

    Open question (unresolved, not answered by this test): does
    ABAN's model recognize "the same decision, differently labeled"
    as a real category, or is every distinct label definitionally a
    distinct decision? There is no way to construct a case ABAN
    itself would recognize as a true relabeling without domain input
    -- the fixture below is a plausible candidate (a synonym-style
    label change with everything else held constant), not a
    confirmed ABAN-equivalent pair.
    """
    a = _baseline_runtime()
    b = copy.deepcopy(a)
    # Candidate relabeling: "deny_subsidy" vs. a synonym-style label
    # for the same governed action. This is a constructed candidate,
    # not something confirmed by Rindai to be ABAN-equivalent.
    b["decision"]["intent"] = "subsidy_denied"

    body = _compare(a, b)

    return _characterization_record(
        "S6",
        open_question=(
            "Is there such a thing as 'the same decision, differently "
            "labeled' in ABAN's model, or is every distinct label a "
            "distinct decision by definition? The fixture used here "
            "(deny_subsidy vs. subsidy_denied) is a constructed "
            "candidate synonym, not a domain-confirmed equivalent "
            "pair."
        ),
        changed_fields=["decision.intent (candidate synonym)"],
        body=body,
    )


def test_s6_relabeling_same_meaning_characterization():
    record = _characterize_s6()
    assert record["semantic_disposition"] == "UNRESOLVED_SEMANTICS"
    assert record["comparability_classification"] is not None


def test_write_divergence_semantic_isolation_results_json():
    rows = [
        _characterize_s5a(),
        _characterize_s6(),
    ]

    payload = {
        "experiment": "decision-authority-divergence-semantic-isolation",
        "spec_version": "v0.3.1",
        "spec_path": (
            "docs/experiments/decision-authority-divergence-isolation-v03.md"
        ),
        "already_covered_elsewhere": {
            "M1": "test_baseline_identical_no_removed_public_labels",
            "M2": "test_case_a_decision_intent_only",
            "M3": "test_case_c_authority_domain_only",
            "M4": "test_case_l_masking_decision_and_authority_together",
            "S3": "test_case_h_admissibility_scope_only",
            "S4": "same case as M3",
            "S7": "same case as M4",
            "R1": "guaranteed by sort_keys=True; no dedicated test",
            "R2": "covered in spirit by test_case_m",
            "R4": "partially covered by test_case_i",
        },
        "deferred_schema_questions_not_tested": ["D1", "D2", "D3"],
        "characterization_results": rows,
        "note": (
            "S5a and S6 are characterization tests. Their mechanical "
            "results are recorded as evidence. Semantic disposition "
            "remains UNRESOLVED_SEMANTICS for both pending Rindai "
            "input -- this file does not resolve either open question."
        ),
    }

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out = EVIDENCE_DIR / "divergence-semantic-isolation-results.json"
    out.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    assert out.exists()
