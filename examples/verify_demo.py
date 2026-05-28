#!/usr/bin/env python3
"""
Decifact Minimal Verifier Demo
-------------------------------
Existence proof for the /compare endpoint.

This script demonstrates cross-system governance comparability inspection:
two independently governed systems, same outcome, non-equivalent governance conditions.

Usage:
    python3 verify_demo.py example-decisions.json

Output:
    Governance equivalence verdict + invariant mismatch report
"""

import json
import sys
import hashlib
from datetime import datetime, timezone


# ─── Invariant thresholds (shared reference conditions) ─────────────────────
# These are the pre-agreed invariant assumptions that BOTH systems must satisfy
# for their decisions to be considered governance-comparable.
# Without pre-agreed invariants, comparison itself is not meaningful.

INVARIANTS = {
    "authority_freshness_max_seconds": 3600,   # authority must be < 1hr old
    "evidence_chain_required": "RFC3161-anchored",  # tamper-evident chain required
    "rollback_viable_required": True,           # rollback must be possible
    "undeclared_dependency_prohibited": True,       # no hidden downstream commitments
}


# ─── Comparator ─────────────────────────────────────────────────────────────

def check_invariant_compliance(decision: dict, label: str) -> list[str]:
    """Check whether a single decision satisfies the shared invariants."""
    violations = []

    if decision["authority_freshness_seconds"] > INVARIANTS["authority_freshness_max_seconds"]:
        violations.append(
            f"{label}: authority_freshness {decision['authority_freshness_seconds']}s "
            f"exceeds threshold {INVARIANTS['authority_freshness_max_seconds']}s"
        )

    if decision["evidence_chain"] != INVARIANTS["evidence_chain_required"]:
        violations.append(
            f"{label}: evidence_chain is '{decision['evidence_chain']}', "
            f"required '{INVARIANTS['evidence_chain_required']}'"
        )

    if decision["rollback_viable"] != INVARIANTS["rollback_viable_required"]:
        violations.append(
            f"{label}: rollback_viable is {decision['rollback_viable']}, "
            f"required {INVARIANTS['rollback_viable_required']}"
        )

    if decision["undeclared_dependency"] and INVARIANTS["undeclared_dependency_prohibited"]:
        violations.append(
            f"{label}: undeclared_dependency is True — prohibited under shared invariants"
        )

    return violations


def compare_governance_fields(a: dict, b: dict) -> list[str]:
    """Identify structural divergences between the two governance states."""
    divergences = []

    fields_to_compare = [
        "governance_regime",
        "authority_source",
        "policy_hash",
        "evidence_chain",
        "rollback_viable",
        "undeclared_dependency",
    ]

    for field in fields_to_compare:
        if a.get(field) != b.get(field):
            divergences.append(
                f"  {field}:\n"
                f"    system_a = {a.get(field)}\n"
                f"    system_b = {b.get(field)}"
            )

    return divergences


def run_compare(filepath: str):
    with open(filepath) as f:
        data = json.load(f)

    a = data["decision_a"]
    b = data["decision_b"]

    print("=" * 60)
    print("DECIFACT /compare — Governance Comparability Inspection")
    print("=" * 60)
    print(f"System A: {a['system_id']} ({a['governance_regime']})")
    print(f"System B: {b['system_id']} ({b['governance_regime']})")
    print(f"Decision object: {a['decision_object']}")
    print(f"Outcome A: {a['outcome']}  |  Outcome B: {b['outcome']}")
    print()

    # Step 1: Check invariant compliance per system
    violations_a = check_invariant_compliance(a, "system_a")
    violations_b = check_invariant_compliance(b, "system_b")
    all_violations = violations_a + violations_b

    # Step 2: Compare governance fields
    divergences = compare_governance_fields(a, b)

    # Step 3: Verdict
    equivalent = (len(all_violations) == 0 and len(divergences) == 0)

    print("─" * 60)
    print("INVARIANT COMPLIANCE")
    print("─" * 60)
    if all_violations:
        for v in all_violations:
            print(f"  ✗  {v}")
    else:
        print("  ✓  Both systems satisfy shared invariants")

    print()
    print("─" * 60)
    print("GOVERNANCE FIELD DIVERGENCES")
    print("─" * 60)
    if divergences:
        for d in divergences:
            print(d)
    else:
        print("  ✓  No field divergences detected")

    print()
    print("─" * 60)
    print("VERDICT")
    print("─" * 60)
    if equivalent:
        print("  ✅  GOVERNANCE EQUIVALENT")
        print("      Both decisions were produced under comparable governance conditions.")
    else:
        print("  ❌  NOT GOVERNANCE EQUIVALENT")
        print()
        print("      Identical outcome. Non-equivalent governance states.")
        print()
        print("      The decisions match at the output layer.")
        print("      They do not match at the governance condition layer.")
        print()
        print("      This is the seam Decifact exposes:")
        print("      receipts can match while decision equivalence does not.")

    print()
    print("=" * 60)
    print("Decifact does not tell systems what to do.")
    print("It exposes whether they were ever comparable enough")
    print("for coordination to be meaningful.")
    print("=" * 60)
    print()
    print("Guardian v0.2 — github.com/xsa520/guardian")
    print("Decifact     — github.com/xsa520/decifact")


if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "example-decisions.json"
    run_compare(filepath)
