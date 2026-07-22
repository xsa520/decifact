# Fracture Label Isolation Summary

**Repository:** `C:\Users\xsa52\decifact`  
**Branch:** `feature/aban-admission-wrapper-v03`  
**Base commit:** `2ff4b2e`  
**Date:** 2026-07-22  

## Fracture Label Semantics Review

### Exact trigger definitions

**`decision_object_divergence`** (`app/routes/compare.py` `_build_fracture_boundary`):

```text
canonical_hash_a != canonical_hash_b
```

Emitted for any difference in the decision-object hash produced by
`compute_canonical_hash(decision)`. No named decision field is inspected.

**`authority_assumption_divergence`** (same function):

```text
boundary_context_hash_a != boundary_context_hash_b
AND canonical_hash_a == canonical_hash_b
```

Emitted for any difference in the full authority-context boundary hash,
but only when decision hashes are equal. Mechanically mutually exclusive
with `decision_object_divergence`.

### Confirmed vs exploratory

| Set | Labels |
|-----|--------|
| Confirmed (classification-bearing) | `no_shared_canonical_reference`, `no_governing_condition_translation_defined` |
| Exploratory / diagnostic-only | `decision_object_divergence`, `authority_assumption_divergence` |

`FORMALLY_INCOMPARABLE` is driven only by the confirmed set (verified in
code and by isolation Cases A/C/G/L). Exploratory labels do **not**
independently determine classification.

### Field-isolation matrix results

| Case | Changed field(s) | Classification | DOD | AAD | Confirmed | Notes |
|------|------------------|----------------|-----|-----|-----------|-------|
| baseline | none | EQUIVALENT | no | no | — | clean |
| A | `decision.intent` | NON_EQUIVALENT | **yes** | no | — | |
| B | `decision.target` | NON_EQUIVALENT | **yes** | no | — | |
| C | `authority_domain` | NON_EQUIVALENT | no | **yes** | — | |
| D | `policy_reference` | FORMALLY_INCOMPARABLE | no | **yes** | `no_shared_canonical_reference` | |
| E | `governing_condition` (no translation) | FORMALLY_INCOMPARABLE | no | **yes** | translation | |
| F | `governing_condition` + shared valid translation_ref | NON_EQUIVALENT | no | **yes** | **none** | raw boundary hash still emits AAD |
| G | `execution_context` | NON_EQUIVALENT | no | **yes** | — | |
| H | `admissibility_scope` | NON_EQUIVALENT | no | **yes** | — | also `acceptance_context_mismatch` |
| I | `governing_condition_translation_ref` only | NON_EQUIVALENT | no | **yes** | — | conditions identical |
| J | 3b multi-field | FORMALLY_INCOMPARABLE | **yes** | **no** | both confirmed | AAD masked |
| K | 3e multi-field | FORMALLY_INCOMPARABLE | no | **yes** | translation | |
| L | intent + authority_domain | NON_EQUIVALENT | **yes** | **no** | — | masking proven; `governance_equivalent=false` |
| M | `decision.content_hash` | EQUIVALENT | no | no | — | EXECUTABLE; hash-keyed field cleared |

DOD = `decision_object_divergence`; AAD = `authority_assumption_divergence`.

### Final relationship classification

**Review conclusion:** `OVER-BROAD / UNSTABLE DIAGNOSTICS`

**Basis:**

- hash-layer triggers
- mutually exclusive emission
- authority divergence masking
- field-level over-breadth

Evidence:

1. Both labels are hash-layer partitions, not named ABAN domain conditions.
2. They are mechanically distinct (mutually exclusive emission) but not
   semantically fine-grained: any decision hash change → DOD; any authority
   hash change with equal decision hash → AAD.
3. Case L / J prove masking: simultaneous decision + authority change
   suppresses AAD even when `governance_equivalent` is false.
4. Case F proves AAD fires from raw boundary-hash difference even when
   the confirmed translation fracture is correctly absent.
5. They are not redundant aliases (different boolean conditions), but they
   are over-broad as domain ontology signals.

Provisional hypothesis **confirmed** by the matrix.

### Code / classification changes

Repository lifecycle status (code changes, merge/push) is maintained only
in the human-edited summary documents and must be synchronized immediately
before distribution. It is intentionally **not** embedded in the generated
JSON matrix artifact.

At isolation-test creation time: production compare/admission code was not
modified; classification logic was not changed; confirmed fracture set was
not expanded; labels were not renamed/merged/removed.

### Remaining open questions

1. Should AAD be redefined to fire whenever boundary hashes differ,
   regardless of decision-hash equality (unmask), or remain mutually
   exclusive by design?
2. Should exploratory labels be renamed to reflect hash-layer semantics
   (e.g. `canonical_decision_hash_divergence`) to avoid ABAN-domain reading?
3. Should exploratory labels be omitted from `fracture_boundary` in API
   responses until confirmed, or retained as explicit diagnostics?
4. `acceptance_context_mismatch` (Case H) was not in scope of this review.

### Pytest

```text
python -m pytest tests/test_fracture_label_isolation.py -v
→ 16 passed

python -m pytest -v
→ 37 passed (prior 21 + 16 isolation)
```

3a–3g behavior preserved (admission wrapper suite green).

### Owner-repository status

*(Synchronize this block immediately before distribution.)*

- Branch: `feature/aban-admission-wrapper-v03`
- Base commit: `2ff4b2e`
- Isolation work: included in this evidence package
- **main has NOT been merged**
- **no push performed** as part of this isolation work
- **no production claim made**

### Explicit statement

Undefined engine hash-diagnostics must not silently become ABAN domain
ontology. `decision_object_divergence` and `authority_assumption_divergence`
remain **exploratory / diagnostic-only** until a future, separately
authorized semantic remediation.

### Real local HTTP validation

Endpoint: `http://127.0.0.1:8765/compare` (uvicorn `app.main:app`)

Captured in `fracture-label-isolation-http.json`:

| Case | HTTP | Classification | Fractures |
|------|------|----------------|-----------|
| identical baseline | 200 | EQUIVALENT | [] |
| decision.intent only | 200 | NON_EQUIVALENT | [decision_object_divergence] |
| authority_domain only | 200 | NON_EQUIVALENT | [authority_assumption_divergence] |
| governing_condition, no translation | 200 | FORMALLY_INCOMPARABLE | [translation, AAD] |
| governing_condition, shared translation | 200 | NON_EQUIVALENT | [AAD] |
| current 3b | 200 | FORMALLY_INCOMPARABLE | [both confirmed, DOD] |
| current 3e | 200 | FORMALLY_INCOMPARABLE | [translation, AAD] |

Actual local HTTP calls were run; results match the pytest matrix.
