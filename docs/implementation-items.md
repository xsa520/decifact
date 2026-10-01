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
introduce reference translation or any broader shared-reference
mechanism in the same patch. Such work would require a separate
specification, evidence threshold, and implementation decision. This
item is scoped strictly to *response completeness for information
already computed*, not to *expanding what gets computed*.

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

---

## Item 2 — Define explicit canonical-field inclusion semantics

**Status:** OBSERVED, NOT PATCHED. Recorded for future implementation.

**Observed** (`canonical/canonicalize.py`, `compute_canonical_hash`):

```python
cleaned = {
    k: ("" if "hash" in k.lower()
            or "reference" in k.lower()
        else v)
    for k, v in canonical_object.items()
}
```

This blanks every top-level field whose key *contains* `"hash"` or
`"reference"` as a substring — not an exact-match exclusion list.
For example, `policy_reference`, `evidence_hash`, `model_reference`,
`authority_reference`, and `input_hash` would all be excluded,
including any of these that turn out to be substantive decision
fields rather than provenance/transport metadata. The exclusion also
only applies to top-level keys; nested fields with the same
substrings are not treated consistently with their top-level
counterparts.

**Required review:**

- define which fields are constitutionally excluded, by exact name,
  not substring match;
- define nested-field behavior explicitly;
- add positive and negative test vectors covering the exclusion
  boundary;
- make any backward-compatibility decision explicit rather than
  implicit.

**Non-goal for this item:** Do not assume the current substring-based
exclusion was unintentional. It may have been a deliberate early
choice to exclude provenance/transport fields. This item is about
formalizing the contract, not assuming the current behavior is wrong.

**Relation to README:** Until this review is complete, the README
should describe canonicalization as operating "under its present
field-exclusion rules" (implementation-defined), not as extracting
an unqualified "minimal semantic set."

---

## Item 3 — `replayable` field is a static marker, not a verified outcome

**Status:** OBSERVED, NOT PATCHED. Recorded for future implementation.

**Observed** (`app/routes/compare.py`): every `/compare` response
returns `"replayable": true` unconditionally. The code does not
check whether decision-time inputs were preserved, whether a
versioned policy snapshot exists, whether a replay engine is
available, whether the authority context can be reconstructed, or
whether a replay was actually attempted and produced a consistent
result.

**Required review — candidate future field model:**

```
replay_status:
  NOT_EVALUATED
  MATERIALS_AVAILABLE
  REPLAYED_CONSISTENT
  REPLAYED_INCONSISTENT
  INSUFFICIENT_MATERIAL
```

**Non-goal for this item:** Do not change the API field in the same
pass as documentation clarifications. This is a breaking response-
schema change and should be scoped and versioned separately.

**Relation to README:** The README now states that `replayable` is a
static implementation marker, not a report that replay occurred or
that reconstruction materials are available. This item tracks the
corresponding code-level fix.

---

## Item 4 — Phase 1 shared-reference proxy: versioning and evolution path

**Status:** OPEN — not yet scheduled.

The `policy_reference`-equality proxy used for shared canonical
reference detection is explicitly Phase 1.

If a later, separately specified mechanism broadens shared-reference
detection, this item tracks:

- how a `FORMALLY_INCOMPARABLE` result produced under Phase 1 should
  be distinguished from one produced under a later, broader
  detection mechanism (e.g. a `detection_method` or `proxy_version`
  field in the response);
- whether historical `/compare` results computed under Phase 1 would
  need to be re-evaluated if a later phase changes what counts as a
  shared reference;
- that this evolution is independent of, and must not be bundled
  with, Items 1–3 above.

**Non-goal for this item:** This item does not commit to building
reference translation. It only tracks how the response model should
represent *which* detection mechanism produced a given result, if
and when that mechanism changes.

---

## Item 5 — Judgment Constitution / Readiness

**Status:** DEFERRED — not yet implemented. Not scheduled, and not a
committed roadmap item.

**Specification:**

`README.md` records a pre-comparability architecture boundary under
"Architecture Boundary — Judgment Constitution / Readiness". The
current executable path does not enforce it.

**Current behavior:**

- `/compare` returns only `EQUIVALENT`, `NON_EQUIVALENT`, or
  `FORMALLY_INCOMPARABLE`.
- Shared-reference detection remains the Phase 1 exact
  `policy_reference` equality proxy. This item does not change that
  proxy.
- `replayable: true` remains a static marker. The implementation does
  not perform independent reconstruction or verification.
- Request validation establishes structural presence only. Empty
  strings and an unconstrained `decision` object remain able to pass
  schema acceptance, and accepted requests still proceed into Phase 1
  comparison.
- There is no executable `INCOMPLETE`, `STRUCTURALLY_COMPLETE`,
  `VERIFIED_CONSTITUTED`, or `HOLD` state machine.
- Existing examples are not `VERIFIED_CONSTITUTED` records.

**Future fail-closed semantics, if a later implementation is
separately authorized:**

- missing constitution basis -> not comparison-admissible
- `STRUCTURALLY_COMPLETE` but unverified -> `HOLD` / not
  comparison-admissible
- only `VERIFIED_CONSTITUTED` -> eligible for comparison

`HOLD` would remain an admission/readiness disposition. It must not
be mapped to failure or to `FORMALLY_INCOMPARABLE`.
`VERIFIED_CONSTITUTED` would remain an admission prerequisite, not a
comparison outcome.

**Non-goal for this item:** Do not add readiness code, tests, or
runtime enforcement in the same pass as this record. Do not change
Phase 1 proxy behavior, the three comparison classifications, or
`replayable`. Do not treat field presence as verified constitution.
