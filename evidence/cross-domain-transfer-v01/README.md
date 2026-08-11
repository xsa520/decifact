# Cross-Domain Admission Transfer Experiment v0.1

**Evidence directory:** `evidence/cross-domain-transfer-v01/`  
**Provenance:** Separate from historical ABAN evidence at `evidence/aban-v0.3-api-test/`.  
**Branch:** `experiment/cross-domain-admission-transfer-v01`  
**Frozen ABAN parent commit:** `f4e0e69dfa97dfb3caee56893fee5e173f05f9b0`  
**Not merged to main. Not a production refactor. Not buyer-facing.**

---

## Synthetic domain assumptions (test only)

**Domain:** Vendor Assurance vs Buyer Acceptance (synthetic procurement scenario).

These are **explicit test assumptions**, not real procurement rules.

| Experimental value | Meaning in this experiment |
|---|---|
| `declared_reference` | A signed SOW, MSA, procurement clause, or other formal agreement explicitly establishes that the vendor assurance artifact participates in the buyer acceptance process. |
| `flagged_authority` | A formally authorized buyer-side procurement / vendor-assurance function has explicitly initiated the relationship for review. |

**Invocation authority assumption (synthetic):**

- A valid invocation requires at least **two independent authorization domains**, excluding the actor represented by `invoked_by`.
- Synthetic sign-off roles used in fixtures: **Procurement Manager**, **Security / Risk Acceptance Lead**.
- The exact titles are synthetic; the invariant is **independent authorization domains**, not the titles themselves.
- Preserves v0.3 hardening: `invoked_by` cannot satisfy its own independent sign-off requirement.

**Vendor/Buyer record shape:**

- `case_admission` and `comparison` remain separate sections, matching the existing wrapper architecture.
- Vendor decision field: `assurance` (e.g. PASS).
- Buyer decision field: `acceptance` (e.g. REJECT / FAIL).

---

## Pre-edit baseline (preserved discrepancy)

| Field | Value |
|---|---|
| Branch | `feature/aban-admission-wrapper-v03` |
| Commit | `f4e0e69dfa97dfb3caee56893fee5e173f05f9b0` |
| **Observed tests passing (pre-edit)** | **41** |
| Prior documented expectation (external review) | **38** |
| Discrepancy | **+3** |

The prior documented expectation of **38** tests is **not rewritten**. This experiment independently observed **41** passing tests on the frozen parent commit **before** any experimental edits. The +3 discrepancy is preserved as part of the evidence record.

Command used for pre-edit observation:

```bash
pytest -q
# Result: 41 passed
```

---

## Experiment scope (what changed)

**Changed:**

- `app/models/admission_request.py` — extended `declared_relationship` Literal with `declared_reference`, `flagged_authority` (ABAN values retained).
- `tests/test_cross_domain_admission_transfer_v01.py` — new Vendor/Buyer transfer tests only.

**Not changed:**

- `/compare` classification logic
- `_has_shared_canonical_reference()`
- `_has_governing_condition_translation()`
- Fracture-boundary generation
- `AuthorityContext`
- `evaluate_admission()` semantics
- Existing ABAN fixtures, expected outputs, or historical ABAN evidence

---

## Fixture cases (VB-1 … VB-4)

| Case | Input fixture | Expected output fixture | Actual output |
|---|---|---|---|
| VB-1 | `vb-1-request.json` | `expected-outputs.json` → VB-1 | `vb-1-actual-output.json` |
| VB-2 | `vb-2-request.json` | `expected-outputs.json` → VB-2 | `vb-2-actual-output.json` |
| VB-3 | `vb-3-request.json` | `expected-outputs.json` → VB-3 | `vb-3-actual-output.json` |
| VB-4 | `vb-4-request.json` | `expected-outputs.json` → VB-4 | `vb-4-actual-output.json` |

### VB-2 engine probe (pre-test, fixed expected fracture list)

Before VB-2 automated assertions were written, `/compare` was probed directly with the VB-2 comparison payload (outside the admission wrapper fixture):

- `comparability_classification`: `FORMALLY_INCOMPARABLE`
- `fracture_boundary`: `["no_shared_canonical_reference", "no_governing_condition_translation_defined"]`

This probe fixed the expected fracture list; it was **not** altered to match a failing run.

---

## Automated test commands and results

See `test-results.json` for machine-readable counts.

```bash
# Historical ABAN admission-wrapper tests
pytest -q tests/test_admission_wrapper.py
# 7 passed

# Historical fracture-label isolation tests
pytest -q tests/test_fracture_label_isolation.py
# 17 passed

# New Vendor/Buyer transfer tests
pytest -q tests/test_cross_domain_admission_transfer_v01.py
# 10 passed

# Combined ABAN + fracture + VB subset
pytest -q tests/test_admission_wrapper.py tests/test_fracture_label_isolation.py tests/test_cross_domain_admission_transfer_v01.py
# 34 passed

# Full repository suite (post-experiment)
pytest -q
# 51 passed
```

No failures. No existing ABAN expected outputs were changed.

---

## Supplementary / manual verification only

**Label:** These entries are **supplementary manual verification**, not automated test results. They do **not** replace regression evidence above.

Recorded in `supplementary-manual-verification.json`:

1. **VB-2 `/compare` probe outside automated fixture**  
   Direct `POST /compare` with VB-2 comparison payload only (no `case_admission` wrapper):  
   - `comparability_classification`: `FORMALLY_INCOMPARABLE`  
   - `fracture_boundary`: `["no_shared_canonical_reference", "no_governing_condition_translation_defined"]`

2. **Admission blocks compare when relationship is none**  
   Direct `POST /admit-and-compare` with complete comparison payload and `declared_relationship="none"`:  
   - `compare_invoked`: `false`  
   - `finding`: `COORDINATION_NOT_CONSTITUTED`

These manual confirmations were performed during experiment setup before VB expected outputs were fixed. Automated regression remains authoritative for pass/fail.

---

## Five invariants (automated)

| Invariant | Test coverage |
|---|---|
| A. Admission independence | `test_vb1_*`, `test_invariant_a_*` |
| B. Authority independence | `test_vb4_*`, `test_invariant_b_*` |
| C. Basis independence | `test_vb2_*`, `test_invariant_c_*` |
| D. Judgment independence | `test_vb3_*`, `test_invariant_d_*` |
| E. Domain independence | `test_invariant_e_*`, `test_flagged_authority_*` |

---

## Transferability classification (Section 10)

**Classification: A — STRUCTURALLY_TRANSFERABLE**

**Evidence:**

1. Only lexical representation changed: two new `declared_relationship` Literal values in `admission_request.py`; no change to `evaluate_admission()` branching on ABAN-specific vocabulary.
2. `/compare`, fracture logic, and `AuthorityContext` unchanged; VB-2/VB-3 exercised existing classifications without engine modification.
3. Vendor/Buyer fixtures consumed the same generic admission states (`none`, constituted relationship + authorized invocation, unauthorized invocation) and the same dual sign-off structure as ABAN cases.
4. All 7 historical ABAN admission tests and 17 fracture isolation tests pass unchanged.
5. No domain adapter, mapping layer, conditional branch, or new semantic interpretation was required for the synthetic domain.

**Not concluded:** market demand, production readiness, or Research Constitution promotion (N=1).

---

## Files in this directory

```
README.md
test-results.json
expected-outputs.json
supplementary-manual-verification.json
vb-1-request.json
vb-1-actual-output.json
vb-2-request.json
vb-2-actual-output.json
vb-3-request.json
vb-3-actual-output.json
vb-4-request.json
vb-4-actual-output.json
```
