# ABAN × Decifact v0.3 — Test Summary

**Repository:** `C:\Users\xsa52\decifact`  
**Branch:** `feature/aban-admission-wrapper-v03`  
**Base implementation commit:** `2ff4b2e`  
**Isolation evidence/tests:** included in this commit

## Prior validated status (v0.3 admission wrapper)

- 21/21 tests pass at `2ff4b2e`
- 3a–3g behavior validated
- Confirmed fractures: `no_shared_canonical_reference`, `no_governing_condition_translation_defined`
- main not merged

## Fracture Label Semantics Review

See full write-up:

- `evidence/aban-v0.3-api-test/fracture-label-isolation-summary.md`
- `evidence/aban-v0.3-api-test/fracture-label-isolation-results.json`
- `tests/test_fracture_label_isolation.py`

### Trigger definitions (exact)

- `decision_object_divergence` ← `canonical_hash_a != canonical_hash_b`
- `authority_assumption_divergence` ← `boundary_context_hash` differs **and** `canonical_hash` equal

### Relationship classification (evidence-backed)

**Review conclusion:** `OVER-BROAD / UNSTABLE DIAGNOSTICS`

**Basis:** hash-layer triggers; mutually exclusive emission; authority
divergence masking; field-level over-breadth.

### Classification safety

Exploratory labels do **not** independently drive `FORMALLY_INCOMPARABLE`.
Confirmed fractures alone do.

### Isolation suite

- Cases A–M + baseline + safety assertion
- All isolation cases use `POST /compare` directly
- J/K reproduce 3b/3e comparison payload shapes only (no admission retest)
- 16 new tests, all passing
- Full suite: **37 passed**
- Production compare/admission code: **unchanged** (at isolation creation)

### Status flags

*(Human-maintained — synchronize before distribution; not stored in
generated `fracture-label-isolation-results.json`.)*

- main merged: **no**
- push performed (this work): **no**
- production claim: **no**
