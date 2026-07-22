# Fracture Label Isolation Summary

**Repository:** `C:\Users\xsa52\decifact`  
**Branch:** `feature/aban-admission-wrapper-v03`  
**Base commit:** `2ff4b2e`  
**Date:** 2026-07-22  

## Remediation (Phase 2 — public-output narrowing)

Approved Phase 1 decision executed with the narrowest change:

- Removed public append of `decision_object_divergence`
- Removed public append of `authority_assumption_divergence`
- No replacement public labels added
- No new debug-output surface introduced
- No rename / unmask / classification change / hashing change
- No admission-behavior change
- Confirmed public fracture set unchanged
- `acceptance_context_mismatch` unmodified
- Independent unmasking deferred
- Production code changed only to narrow public output

Wording discipline: no separate internal/debug retention path was
implemented in this remediation. These two labels were removed from the
public `fracture_boundary`; this package does **not** claim they were
retained internally.

### Interface rule

An empty public `fracture_boundary` does **not** imply equivalence.
Callers must read:

- `comparability_classification`
- `canonical_equivalent`
- `governance_equivalent`

## Fracture Label Semantics Review (pre-remediation findings)

### Exact trigger definitions (historical — no longer public)

**`decision_object_divergence`** (formerly emitted by
`_build_fracture_boundary`):

```text
canonical_hash_a != canonical_hash_b
```

**`authority_assumption_divergence`** (formerly):

```text
boundary_context_hash_a != boundary_context_hash_b
AND canonical_hash_a == canonical_hash_b
```

### Confirmed public fractures (unchanged)

| Set | Labels |
|-----|--------|
| Confirmed (classification-bearing) | `no_shared_canonical_reference`, `no_governing_condition_translation_defined` |
| Removed from public fracture_boundary | `decision_object_divergence`, `authority_assumption_divergence` |

`FORMALLY_INCOMPARABLE` continues to be driven only by the confirmed set.

### Field-isolation matrix results (post-remediation)

| Case | Changed field(s) | Classification | Public fractures | Equivalence notes |
|------|------------------|----------------|------------------|-------------------|
| baseline | none | EQUIVALENT | [] | both true |
| A | `decision.intent` | NON_EQUIVALENT | [] | canon=false |
| B | `decision.target` | NON_EQUIVALENT | [] | canon=false |
| C | `authority_domain` | NON_EQUIVALENT | [] | gov=false |
| D | `policy_reference` | FORMALLY_INCOMPARABLE | `no_shared_canonical_reference` | gov=false |
| E | `governing_condition` (no translation) | FORMALLY_INCOMPARABLE | translation | gov=false |
| F | `governing_condition` + shared valid translation_ref | NON_EQUIVALENT | [] | gov=false |
| G | `execution_context` | NON_EQUIVALENT | [] | gov=false |
| H | `admissibility_scope` | NON_EQUIVALENT | `acceptance_context_mismatch` | gov=false |
| I | `governing_condition_translation_ref` only | NON_EQUIVALENT | [] | gov=false |
| J | 3b multi-field | FORMALLY_INCOMPARABLE | both confirmed | both false |
| K | 3e multi-field | FORMALLY_INCOMPARABLE | translation only | gov=false |
| L | intent + authority_domain | NON_EQUIVALENT | [] | both false |
| M | `decision.content_hash` | EQUIVALENT | [] | both true |

DOD/AAD are absent from every public `fracture_boundary`.

### Final relationship classification

**Review conclusion:** `OVER-BROAD / UNSTABLE DIAGNOSTICS`

**Remediation applied:** removed from public `fracture_boundary`; no
replacement public labels; no new debug-output surface; independent
unmasking deferred.

### Pytest

```text
python -m pytest tests/test_fracture_label_isolation.py -v
→ 17 passed

python -m pytest tests/test_admission_wrapper.py -v
→ 7 passed (3a–3g green)

python -m pytest -v
→ 38 passed
```

Classification behavior and equivalence booleans unchanged relative to
pre-remediation expectations.

### Owner-repository status

*(Synchronize this block immediately before distribution.)*

- Branch: `feature/aban-admission-wrapper-v03`
- Isolation evidence/test commit: `e756158`
- Publication-status sync commit: `4a4fc42`
- Phase 2 public-output narrowing: **uncommitted — pending review**
- Remote branch: `origin/feature/aban-admission-wrapper-v03`
- main has NOT been merged
- no push of Phase 2 remediation
- no production claim made

### Explicit statement

Undefined engine hash-diagnostics must not silently become ABAN domain
ontology. `decision_object_divergence` and `authority_assumption_divergence`
have been removed from the public `fracture_boundary`. Confirmed public
fractures are unchanged. Independent unmasking remains deferred. No
replacement public labels were added. No new debug-output surface was
introduced. Production code changed only to narrow public output.

### Real local HTTP validation

Endpoint: `http://127.0.0.1:8766/compare` (uvicorn `app.main:app`; port
8766 used because 8765 was already bound)

Captured in `fracture-label-isolation-http.json`:

| Case | HTTP | Classification | Public fractures |
|------|------|----------------|------------------|
| identical baseline | 200 | EQUIVALENT | [] |
| decision.intent only (A) | 200 | NON_EQUIVALENT | [] |
| authority_domain only (C) | 200 | NON_EQUIVALENT | [] |
| governing_condition, no translation (E) | 200 | FORMALLY_INCOMPARABLE | [translation] |
| governing_condition, shared translation (F) | 200 | NON_EQUIVALENT | [] |
| current 3b (J) | 200 | FORMALLY_INCOMPARABLE | [both confirmed] |
| current 3e (K) | 200 | FORMALLY_INCOMPARABLE | [translation] |
| masking decision+authority (L) | 200 | NON_EQUIVALENT | [] |

Expected and observed: DOD/AAD absent everywhere publicly; classifications
unchanged; equivalence booleans unchanged; confirmed fractures preserved.
Actual local HTTP calls were run; results match the pytest matrix.
