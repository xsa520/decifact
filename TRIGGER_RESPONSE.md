# Clarification: Comparison Determination Is Not Generic Comparison

Decifact first determines whether a valid comparison basis is
represented under the implemented evaluation model.

Possible outcomes:

- `EQUIVALENT`
- `NON_EQUIVALENT`
- `FORMALLY_INCOMPARABLE`

`FORMALLY_INCOMPARABLE` means the implementation did not establish
the prerequisite comparison basis. It is distinct from a completed
comparison that found non-equivalence.

A Decifact result describes a relationship between judgments. It does
not establish correctness, reliance authority, execution
admissibility, or runtime permission.

`HOLD` is an admission/readiness disposition, not a comparison
classification.

An input held before comparison has not been classified as equivalent,
non-equivalent, or formally incomparable.

That disposition is specification-only. The current comparison path
does not return `HOLD`.
