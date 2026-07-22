# ABAN × Decifact v0.3 — Test Summary

**Repository:** `C:\Users\xsa52\decifact`  
**Branch:** `feature/aban-admission-wrapper-v03`  
**Base implementation commit:** `2ff4b2e`  
**Isolation evidence/tests commit:** `e756158`  
**Publication-status sync commit:** `4a4fc42`

## Prior validated status (v0.3 admission wrapper)

- 21/21 tests pass at `2ff4b2e`
- 3a–3g behavior validated
- Confirmed fractures: `no_shared_canonical_reference`, `no_governing_condition_translation_defined`
- main not merged

## Phase 2 — public-output narrowing (pending review)

Production change (narrowest): stop appending
`decision_object_divergence` and `authority_assumption_divergence` to
the public `fracture_boundary`.

- Confirmed public fracture set: **unchanged**
- Independent unmasking: **deferred**
- No replacement public labels added
- No new debug-output surface introduced
- No separate internal/debug retention path implemented — do not claim
  internal retention; state only public removal
- Classification logic / hashing / admission: **unchanged**
- `acceptance_context_mismatch`: **unmodified**
- Production code changed only to narrow public output
- No merge / no push / no production claim

### Interface rule

An empty public `fracture_boundary` does **not** imply equivalence.
Callers must read:

- `comparability_classification`
- `canonical_equivalent`
- `governance_equivalent`

## Fracture Label Semantics Review

See full write-up:

- `evidence/aban-v0.3-api-test/fracture-label-isolation-summary.md`
- `evidence/aban-v0.3-api-test/fracture-label-isolation-results.json`
- `evidence/aban-v0.3-api-test/fracture-label-isolation-http.json`
- `tests/test_fracture_label_isolation.py`

### Relationship classification (evidence-backed)

**Review conclusion:** `OVER-BROAD / UNSTABLE DIAGNOSTICS`

**Remediation:** removed from public `fracture_boundary`.

### Classification safety

Removed labels do not appear on any public `fracture_boundary`.
Confirmed fractures alone drive `FORMALLY_INCOMPARABLE`.

### Isolation suite

- Cases A–M + baseline + representative public-boundary safety assertion
- All isolation cases use `POST /compare` directly
- J/K reproduce 3b/3e comparison payload shapes only (no admission retest)
- Isolation tests: **17 passed**
- Admission wrapper: **7 passed**
- Full suite: **38 passed**

### Status flags

*(Human-maintained — synchronize before distribution; not stored in
generated `fracture-label-isolation-results.json`.)*

- Isolation evidence/tests commit: `e756158`
- Publication-status sync: `4a4fc42`
- Phase 2 public-output narrowing: **uncommitted — pending review**
- Remote branch: `origin/feature/aban-admission-wrapper-v03`
- Push status (Phase 2): **not pushed**
- main merged: **no**
- production claim: **no**
