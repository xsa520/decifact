# Decifact Editorial Principles

These are maintenance-facing principles for editing `README.md`,
`decifact.com`, `QUICKSTART.md`, and `playground.html` — not public
content. They exist so future edits preserve the discovery effect
validated on 2026-06-14, without requiring that effect to be
re-discovered (or accidentally undone) each time.

---

## Principle 1 — Discovery is a prerequisite for artifact, not an
alternative to it.

Decifact's terminology (`FORMALLY_INCOMPARABLE`, canonical reference,
fracture boundary, invariant boundary, etc.) only becomes meaningful
*after* a reader recognizes their own situation in what's being
described. Before that recognition, these terms are noise — abstract
words competing with every other framework's abstract words.

This is not "Discovery Language vs. Artifact Language" as two
competing registers to balance. It is two *stages*:

> Discovery Language = the language Artifact Language needs, before it
> can mean anything.

Artifact language is not simplified, hidden, or apologized for. It is
*sequenced* — it arrives once the reader is already oriented.

---

## Principle 2 — The fix is sequencing, not more symptom language.

When auditing for discoverability, the question is not "do we have
enough plain-language description of the problem?" It's "does the
plain-language description arrive *before* the terminology that
depends on it?"

The 2026-06-14 README revision changed ~30-40 lines (hero, one new
"Recognize This?" section, two sentence-level rewordings, one
transition sentence) — no content was removed, no new sections were
written from scratch, no technical material changed. The improvement
came entirely from reordering and locally rewording existing material.

If a future audit finds the same "builds recognition, then drops into
terminology before landing the point" pattern, the fix is almost
certainly: keep the sentence, move it later or reword its ending —
not write new material.

---

## Preferred sequencing

> Recognition → Symptom → Example → Problem → Framework → Mechanism

Not:

> Framework → Mechanism → Example → Recognition

Concretely, for any page/section:

1. **Recognition** — a situation the reader has plausibly experienced,
   described without Decifact-specific terms.
2. **Symptom** — what that situation *feels like* from the inside
   ("both sides look valid, but...").
3. **Example** — a concrete worked instance (e.g. the cross-ministry
   example).
4. **Problem** — the general form of the situation, explicitly
   connected back to the Recognition/Example ("that's the situation in
   miniature; more generally...").
5. **Framework** — Guardian/Decifact's conceptual vocabulary
   (comparability, acceptance, equivalence).
6. **Mechanism** — the artifact itself: endpoints, classifications,
   JSON, `FORMALLY_INCOMPARABLE`.

---

## What this is not

- Not a rewrite mandate. Most existing content already contains good
  Recognition/Symptom material — it was often just placed *after* the
  Framework/Mechanism material that depended on it, or its own ending
  reverted to Framework language before landing.
- Not a request to remove or soften Decifact's actual terminology.
  Artifact language stays exactly as precise as it needs to be — it
  just shouldn't be the *first* thing a stranger encounters.
- Not specific to README.md. Applies to decifact.com, QUICKSTART.md,
  and playground.html — anywhere a stranger's first encounter with
  Decifact happens.
