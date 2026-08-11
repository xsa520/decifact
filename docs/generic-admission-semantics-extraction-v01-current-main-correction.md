# Generic Admission Semantics Extraction — Current-Main Correction v0.1

**Task nature:** PROVENANCE CORRECTION + BOUNDED READ-ONLY RE-REVIEW  
**Supersedes (for current-main claims only):** `docs/generic-admission-semantics-extraction-v01.md` (stale-base review against `32956e0`)  
**Correction branch:** `review/generic-admission-semantics-v01-current-main-correction`  
**Corrected current main:** `4e78c4194ac47fd1ef960f7c2c80425f7e5ec77c`  
**Prior stale review base:** `32956e0635d68037a79f60eff42bd6c835abf9c5`

**Recommendation (Section I):** **`NEEDS_MORE_EVIDENCE`**

Fixing stale-base contamination does **not** automatically upgrade the prior recommendation.

---

## A. Provenance correction

### Prior failure type: **STALE-BASE CONTAMINATION**

**Definition:** The review branch had correct main *lineage*, but its base commit was not current with `origin/main` when repository state was treated as evidence.

**Distinguished from WRONG-ANCESTRY CONTAMINATION:** The review branch was branched from `main`, not from an experimental lineage — but from a **stale local `main` snapshot**.

> **"Branched from main" ≠ "branched from current main."**  
> Both branch identity/ancestry **and** branch currency must be verified independently.

### Synchronization record

| Step | Result |
|---|---|
| `git fetch origin` | Completed |
| Local `main` before sync | `32956e0635d68037a79f60eff42bd6c835abf9c5` (13 commits behind) |
| Fast-forward | `git merge --ff-only origin/main` |
| Local `main` after sync | `4e78c4194ac47fd1ef960f7c2c80425f7e5ec77c` |
| `origin/main` | `4e78c4194ac47fd1ef960f7c2c80425f7e5ec77c` |
| **local main == origin/main** | **YES** |

### MC-013 note

This task supplies source-case evidence only. **`methodology-candidates.md` was not modified.** MC-013 remains **CANDIDATE IDENTIFIED / INSERTION DEFERRED UNTIL SOURCE-CASE CLOSURE**.

---

## B. Cross-domain evidence preservation

| Item | Value |
|---|---|
| Experiment branch | `experiment/cross-domain-admission-transfer-v01` |
| Parent (ABAN frozen) | `f4e0e69dfa97dfb3caee56893fee5e173f05f9b0` |
| **Committed experiment hash** | **`7a71ebf7aba969311036bb12fa77aa2ee1753d73`** |
| Commit message | `Record completed cross-domain admission transfer evidence` |
| Evidence committed | **YES** (14 files: schema extension, tests, 12 evidence artifacts) |
| Merged to main | **NO** |

### Regression after commit (reproduced)

| Command | Result |
|---|---|
| `pytest -q tests/test_admission_wrapper.py` | **7 passed** |
| `pytest -q tests/test_fracture_label_isolation.py` | **17 passed** |
| `pytest -q tests/test_cross_domain_admission_transfer_v01.py` | **10 passed** |
| `pytest -q` | **51 passed** |

Matches previously verified experiment results. No semantic or expected-output changes were made during preservation.

---

## C. Current-main verification

Inspected at **`4e78c41`** (local == origin).

### C.1 Requested documentation — present/absent

| Artifact | Stale review (`32956e0`) | Current main (`4e78c41`) |
|---|---|---|
| `docs/implementation-items.md` | **Reported absent** | **PRESENT** (212 lines) |
| README — seven governance layers | **Reported not found** | **PRESENT** — numbered list L1–L7, lines 218–230; Decifact scoped to Layer 3 comparison determination, lines 232–240 |
| README — Failure-Semantic Preservation | **Reported not found** | **PRESENT** — section heading line 330; lines 330–367 |
| README — `NOT_EVALUATED` | **Reported not found** | **PRESENT** — lines 348–349, 358–361; also in `docs/implementation-items.md` Item 1 lines 48–52, 72–73 |
| README — prerequisite / staged semantics | Not fully checked | **PRESENT** — comparability-after-prerequisite lines 147–149; staged evaluation design direction lines 358–364; Item 1 documents staged fracture semantics gap |

**Exact path:** `docs/implementation-items.md`  
**Key section headings:** Item 1 (staged fracture / `NOT_EVALUATED`), Item 2 (canonical-field exclusion), Item 3 (`replayable` marker), Item 4 (Phase 1 proxy evolution).

### C.2 Current L3 implementation — re-verified answers

| # | Question | Current main @ `4e78c41` | Evidence |
|---|---|---|---|
| 1 | Admission/precondition route? | **NO** | `app/main.py` L18–20 registers `/verify-equivalence`, `/canonicalize`, `/compare` only; no `admit_and_compare` module on main |
| 2 | Direct `/compare` without admission gate? | **YES** | `app/routes/compare.py` `@router.post("/compare")` L84; no upstream gate in main |
| 3 | Governing-condition translation in compare? | **NO** | No `_has_governing_condition_translation()` in `app/routes/compare.py`; classification L75–76 triggers only on missing shared `policy_reference` |
| 4 | `AuthorityContext.governing_condition`? | **NO** | `canonical/schema.py` L5–9: only `authority_domain`, `policy_reference`, `execution_context`, `admissibility_scope` |
| 5 | Public fracture labels | **`no_shared_canonical_reference`**, **`decision_object_divergence`**, **`authority_assumption_divergence`**, **`acceptance_context_mismatch`** | `compare.py` `_build_fracture_boundary` L29–58 |
| 6 | `FORMALLY_INCOMPARABLE` when no shared reference? | **YES** | `_classify_comparability` L75–76 returns `FORMALLY_INCOMPARABLE`, `["no_shared_canonical_reference"]` |
| 7 | Docs describe staged prerequisite / `NOT_EVALUATED`? | **YES (design direction)** | README L330–367; `implementation-items.md` Item 1 |
| 8 | Design vs implementation relationship | **Documented gap** | README acknowledges flat `fracture_boundary` and discarded diagnostics; Item 1 status **OBSERVED, NOT PATCHED**; admission/precondition layer **not implemented on main** |

### C.3 README seven-layer context (not L1/L2 implementation)

README lines 218–230 enumerate seven governance layers (referent/object through evidence reconciliation). Decifact is scoped to **Layer 3 — comparison determination** (lines 232–240). This is **architectural context**, not evidence that L1/L2 evaluators exist in code.

---

## D. Corrected Main Integration Boundary

**Unchanged core finding:** Current `main` has **no implemented admission/precondition layer**. Integration would require adding an orchestrator route **before** L3, without embedding checks inside `_classify_comparability()`.

**Corrected context:**

1. Current main documentation **already anticipates** staged prerequisite evaluation and `NOT_EVALUATED` semantics as **design direction** (`README.md` L330–367, `docs/implementation-items.md` Item 1). A future admission layer would align with documented direction but is **not yet implemented**.

2. Current main `/compare` **still** exposes hash-divergence labels on public `fracture_boundary` and **still lacks** governing-condition translation — same as stale-base observation for **code behavior**.

3. ABAN wrapper branch (`f4e0e69`) and cross-domain experiment (`7a71ebf`) implement admission + a **different L3 engine** (translation check, narrowed public fractures). **Main integration is not a drop-in of experiment branch code** without an explicit L3 reconciliation decision.

**Attach point (conceptual, unchanged):** New route registered in `app/main.py`, calling precondition evaluator then existing `compare()` — mirroring ABAN `admit_and_compare.py` pattern on the **wrapper branch only**.

---

## E. Corrected Three-Way Semantic Comparison

| Semantic aspect | Current main (`4e78c41`) | ABAN v0.3 wrapper (`f4e0e69`) | Cross-domain (`7a71ebf`) | Classification |
|---|---|---|---|---|
| Admission / relationship gate | **None** | `evaluate_admission()` + `/admit-and-compare` | Same gate as ABAN | `ALREADY_EVIDENCE_SUPPORTED_GENERIC` (pattern on branches); **absent on main** |
| Direct `/compare` always reachable | **Yes** | Yes via `/compare`; gated via wrapper route | Same | Main: no gate |
| Invocation authority (≥2 signers excl. invoker) | N/A on main | Implemented | Same | `ALREADY_EVIDENCE_SUPPORTED_GENERIC` |
| Upstream failure outcome | N/A on main | `COORDINATION_NOT_CONSTITUTED` + sub_reasons | Same | `DOMAIN_SPECIFIC_REPRESENTATION` (finding label) |
| `compare_invoked` flag | N/A on main | Present on wrapper | Same | `ALREADY_EVIDENCE_SUPPORTED_GENERIC` |
| L3: `policy_reference` shared-ref check | Yes | Yes | Yes | `ALREADY_EVIDENCE_SUPPORTED_GENERIC` |
| L3: governing-condition translation | **No** | **Yes** (`_has_governing_condition_translation`) | Uses ABAN-branch L3 | **`UNRESOLVED` for main integration** |
| L3: public fracture set | Hash-divergence labels **included** | Hash-divergence labels **removed** from public set | ABAN-branch L3 | Main ≠ ABAN branch |
| `AuthorityContext.governing_condition` | **Absent** | **Present** | Present in VB fixtures | Main ≠ ABAN branch |
| Domain relationship literals | N/A | ABAN literals | + `declared_reference`, `flagged_authority` | `DOMAIN_SPECIFIC_REPRESENTATION` |
| Docs: staged prerequisite / `NOT_EVALUATED` | **Present (design)** | N/A on branch tip | N/A | Corrected: **was wrongly reported absent on stale main** |
| L1/L2 evaluators in code | **Not implemented** | **Not implemented** | **Not implemented** | `FUTURE_EXTENSION_ONLY` |

**Main vs ABAN L3 divergence:** **Still exists** on current main. Stale-base correction did **not** eliminate this divergence.

---

## F. Retained semantic conclusions (still valid)

These were derived primarily from frozen ABAN wrapper + completed cross-domain experiment and **remain provisionally valid**:

| ID | Conclusion | Why retained |
|---|---|---|
| R-1 | Relationship `"none"` blocks comparison routing; complete comparison payload cannot bypass | ABAN 3a, VB-1, `admission_gate.py`; experiment evidence `7a71ebf` |
| R-2 | Relationship declaration ≠ invocation authority | ABAN 3c/3d, VB-4, invariant B |
| R-3 | Invocation requires multiple distinct signers excluding `invoked_by` | `admission_gate.py` L29–37; ABAN 3d; VB-4 |
| R-4 | Admission pass ≠ L3 comparison basis exists | VB-2 → `FORMALLY_INCOMPARABLE` after pass |
| R-5 | Upstream precondition failure ≠ `FORMALLY_INCOMPARABLE` | VB-1/VB-4 vs VB-2 routing distinction |
| R-6 | Domain-specific literals must not become generic ontology | Four known literals + gate ignores non-`none` values |
| R-7 | Precondition routing must occur **before** L3 `/compare` | `admit_and_compare.py` L19–37; not inside `_classify_comparability()` |

Sections A/B/C (generic invariants, domain-specific list, conceptual contract shape) from the prior report are **retained** unless contradicted above.

---

## G. Retracted / corrected stale-base findings

| Prior claim (stale base `32956e0`) | Corrected finding (`4e78c41`) |
|---|---|
| `docs/implementation-items.md` absent | **RETRACTED — file exists** with Item 1 staged fracture / `NOT_EVALUATED` tracking |
| README lacks Failure-Semantic Preservation | **RETRACTED — section present** (L330+) |
| README lacks `NOT_EVALUATED` discussion | **RETRACTED — present** in README and Item 1 |
| README lacks seven-layer / prerequisite context | **RETRACTED — seven layers enumerated** L218–230; Layer 3 scope L232–240 |
| Open question #6/#7 citing missing docs | **CORRECTED — docs now locatable**; open questions reframed below |
| Cross-domain evidence only in stash | **CORRECTED — committed** at `7a71ebf` on experiment branch |

**Claims that remain correct after re-verification:**

| Claim | Status |
|---|---|
| Main has no admission route | **Still true** |
| Main `/compare` lacks governing-condition translation | **Still true** |
| Main `AuthorityContext` lacks `governing_condition` | **Still true** |
| Main public fractures include hash-divergence labels | **Still true** |
| Main ≠ ABAN-branch L3 engine | **Still true** |

---

## H. Remaining genuinely unresolved questions

Fixing stale-base contamination **does not** answer these:

1. **Is N=2 authorization threshold domain-invariant?** — Still only observed in two domains; gate hardcodes 2.
2. **Should relationship state and evidence be separate in production?** — Gate ignores non-`none` literal semantics; unresolved.
3. **Generic production name for upstream admission failure?** — `COORDINATION_NOT_CONSTITUTED` remains ABAN-flavored.
4. **Is a domain adapter required?** — Experiments suggest lexical adapter at schema edge; not validated as production pattern.
5. **Are two tested domains sufficient for implementation confidence?** — N=2; not promoted to ontology.
6. **Which L3 engine is canonical for main integration?** — Current main Phase 1 compare vs ABAN-branch compare with translation and narrowed fractures; VB-2 evidence depends on ABAN-branch L3.
7. **How to align documented staged `NOT_EVALUATED` design with admission wrapper?** — Docs on main describe future staged L3 behavior; admission wrapper on branch is separate upstream layer — integration architecture unsettled.

### Reasons that disappear (stale-base artifacts)

- ~~`implementation-items.md` absent~~
- ~~README Failure-Semantic / NOT_EVALUATED / seven-layer not locatable~~
- ~~Cross-domain evidence provenance weak (stash-only)~~

### Reasons that remain after correction

- N=2 domains; N=2 threshold unresolved
- Generic naming unsettled
- Main lacks admission implementation despite docs describing prerequisite concepts
- Main vs ABAN-branch L3 material divergence
- Relationship state vs evidence separation unsettled

---

## I. Recommendation

### **`NEEDS_MORE_EVIDENCE`**

**Rationale:**

1. **Provenance correction is not new positive evidence.** Docs now locatable on current main clarify design direction but do **not** implement admission or resolve open semantic questions.

2. **Core transferable structure** (R-1 through R-7) remains evidenced on ABAN + cross-domain branches — but **current main still lacks the admission layer entirely**.

3. **Main vs ABAN-branch L3 divergence persists.** Cross-domain VB-2 fracture behavior was validated against ABAN-branch `/compare`, not current main `/compare` (no translation check, different public fracture set).

4. **Unresolved questions in Section H remain** — stale-base fixes removed documentation-absence noise only.

5. **Not `DO_NOT_GENERALIZE_YET`:** Experiments did validate structural transferability of precondition routing (prior experiment classification A). Extraction is not invalidated — it is **incomplete for main integration**.

6. **Not `READY_FOR_IMPLEMENTATION_TASK`:** Implementation would require L3 reconciliation decision, generic contract naming, and evidence beyond N=2 domains.

---

## J. Git / provenance status

| Item | Value |
|---|---|
| Current main hash | `4e78c4194ac47fd1ef960f7c2c80425f7e5ec77c` |
| origin/main hash | `4e78c4194ac47fd1ef960f7c2c80425f7e5ec77c` |
| Equality confirmed | **YES** |
| Prior stale review base | `32956e0635d68037a79f60eff42bd6c835abf9c5` |
| Review correction branch | `review/generic-admission-semantics-v01-current-main-correction` |
| Experiment evidence commit | `7a71ebf7aba969311036bb12fa77aa2ee1753d73` |
| Original stale review doc | `docs/generic-admission-semantics-extraction-v01.md` (untracked on correction branch; preserved, not overwritten) |
| Files modified by **this review task** | `docs/generic-admission-semantics-extraction-v01-current-main-correction.md` only |
| `app/` modified by review | **NO** |
| main modified | **NO** |
| Merged to main | **NO** |
| decifact.com touched | **NO** |
| methodology-candidates.md touched | **NO** |

---

## Reference commits (read-only)

| Branch | Commit | Role |
|---|---|---|
| `main` / `origin/main` | `4e78c41` | Current-main verification base |
| `feature/aban-admission-wrapper-v03` | `f4e0e69` | Frozen ABAN wrapper reference |
| `experiment/cross-domain-admission-transfer-v01` | `7a71ebf` | Committed cross-domain evidence |
| Stale review base | `32956e0` | Historical only — do not use for current-main claims |
