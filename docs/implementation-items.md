# Implementation Items

Bounded, deferred engineering items. These are recorded for future
work — none are patched in the same pass as the README architecture
update (2026-07-29), and none are bundled with unrelated work
(e.g. reference-translation implementation).

---

## Item 1 — Preserve staged fracture semantics in `/compare`

**Status:** OBSERVED, NOT PATCHED. Recorded for future implementation.

**Current behavior** (`app/routes/compare.py`,
`_classify_comparability`):

When `_has_shared_canonical_reference()` returns `False`, the
function short-circuits and returns:

```python
return "FORMALLY_INCOMPARABLE", ["no_shared_canonical_reference"]
```

This discards whatever `_build_fracture_boundary()` had already
computed in `internal_fracture_boundary` for the same call — e.g.
`decision_object_divergence`, `authority_assumption_divergence`,
`acceptance_context_mismatch` may all have been evaluated and found
true, but none of that is represented in the response once the
`FORMALLY_INCOMPARABLE` branch fires.

**Observed consequence and required future distinctions:**

The current implementation directly exhibits the first two
categories below. The third is not currently represented by the
response model and would become necessary if later phases introduce
staged evaluation with prerequisite-dependent short-circuiting.

```
1. Evaluated, true, and classification-driving
   → currently preserved
   (e.g. "no_shared_canonical_reference")

2. Evaluated, true, but not classification-driving
   → currently and observably discarded
   (e.g. decision_object_divergence, computed but dropped
   when the FORMALLY_INCOMPARABLE branch returns)

3. Not evaluated because an upstream prerequisite failed
   → not a behavior currently produced by this evaluation
   sequence, but a distinct state the future staged result
   model must be capable of representing
```

Note on the current control flow: `_build_fracture_boundary()`
already runs all four checks unconditionally before
`_classify_comparability()` decides which branch to take. So today,
nothing is actually skipped due to a failed prerequisite — category
3 does not yet occur in this code. It becomes relevant only if a
future staged-evaluation design introduces genuine short-circuiting
(skipping later checks once an earlier one fails), which this
implementation does not currently do.

**Required distinction for a future fix:**

A staged result model would need at least four states per
prerequisite/check, not two:

```
PASS
FAIL                  (classification-driving)
OBSERVED / DIAGNOSTIC (evaluated, true, non-driving)
NOT_EVALUATED         (skipped because an upstream
                        prerequisite failed)
```

Collapsing this to a simple `FAIL` vs `NOT_EVALUATED` binary would
still lose category 2 (diagnostics computed but not surfaced).

**Non-goal for this item:**

Do not change the Phase 1 `policy_reference` proxy logic. Do not
introduce reference translation (`REQUIRES_REFERENCE_TRANSLATION`,
Guardian v0.3 territory) in the same patch. This item is scoped
strictly to *response completeness for information already
computed*, not to *expanding what gets computed*.

```
Failure-semantic preservation  ≠  Reference-translation implementation
```

These are two separate pieces of future work and should not be
merged into a single change.

**Relation to README:** The README's "Failure-Semantic Preservation
(Design Direction)" section already documents this gap honestly at
the specification level. This file tracks the corresponding code
change as a separate, bounded, not-yet-scheduled item.

The current implementation has already, and observably, proven
category 2 above (evaluated-but-discarded diagnostics).
`NOT_EVALUATED` (category 3) is a distinct state that a future
staged prerequisite-evaluation model must be able to represent — it
is not something this implementation currently produces.
