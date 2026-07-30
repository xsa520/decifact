> [!WARNING]
> This document reflects the terminology used by the historical
> ABAN admission-wrapper test branch.
>
> It is not the current Decifact comparison model. The current model
> distinguishes `EQUIVALENT`, `NON_EQUIVALENT`, and
> `FORMALLY_INCOMPARABLE`, and does not treat comparison
> determination as proof that two judgments are generically
> “the same decision.”
>
> See the [`main`](https://github.com/xsa520/decifact/tree/main) branch for current documentation.

---

## Clarification: This is not comparison

This is not a generic comparison tool.

What is being evaluated here is **decision equivalence**.

---

## Definition

Equivalence is defined strictly as **invariant boundary equality**.

Two decisions are equivalent if and only if their invariant representations match.

---

## Important distinctions

- Hash equality is neither necessary nor sufficient for equivalence
- Structural similarity does not imply equivalence
- Execution results are not a valid proxy for equivalence

---

## What this engine does

1. Extracts the invariant boundary of each decision
2. Canonicalizes the invariant representation
3. Compares the resulting canonical forms
4. Produces a deterministic equivalence result

---

## Implication

If two systems produce different outputs under this model,
the difference is not interpretational - it is structural.

---

## Summary

This is not about comparing outputs.

This is about determining whether two decisions are **the same decision**.
