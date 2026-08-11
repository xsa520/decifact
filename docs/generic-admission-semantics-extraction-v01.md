# Generic Admission Semantics Extraction / Main Integration Review v0.1

**Task nature:** READ-ONLY ARCHITECTURE REVIEW (evidence-bound).  
**Review branch:** `review/generic-admission-semantics-v01`  
**Main commit (review base):** `32956e0635d68037a79f60eff42bd6c835abf9c5`  
**Frozen ABAN reference commit:** `f4e0e69dfa97dfb3caee56893fee5e173f05f9b0` (`feature/aban-admission-wrapper-v03`)  
**Cross-domain reference:** `experiment/cross-domain-admission-transfer-v01` (uncommitted WIP + stash; evidence read from stash untracked tree `stash@{0}^3`)

**Governing sentence:** Extract only what the completed experiments actually validated. Do not convert experimental vocabulary into production ontology.

**Recommendation (Section H):** **`NEEDS_MORE_EVIDENCE`**

---

## Evidence inputs consulted

| Source | Status |
|---|---|
| `feature/aban-admission-wrapper-v03` @ `f4e0e69` — `admission_request.py`, `admission_gate.py`, `admit_and_compare.py`, `tests/test_admission_wrapper.py`, `evidence/aban-v0.3-api-test/` | Read (frozen branch) |
| Cross-domain transfer — `evidence/cross-domain-transfer-v01/` (README, expected-outputs, test-results, vb-1..4, supplementary-manual-verification) | Read (stash `stash@{0}^3`; not on any committed branch tip) |
| `main` @ `32956e0` — `app/routes/compare.py`, `canonical/schema.py`, `app/main.py`, `README.md` | Read (current checkout) |
| `docs/implementation-items.md` | **Not present** in repository at requested paths/commits |
| README sections: seven-layer, `Failure-Semantic Preservation`, `NOT_EVALUATED` | **Not found** in `main` README at `32956e0` (grep returned no matches) |

Cross-domain experiment evidence is treated as **completed experiment output** from the prior session even though it was not committed to the experiment branch tip; citations reference the preserved stash tree and automated test file in that WIP.

---

## Six in-scope questions (with evidence citations)

### Q1 — Generic relationship constitution

**Minimal domain-invariant definition (evidence-supported):**

A comparison relationship is **constituted for routing purposes** when the admission payload declares a relationship state **other than explicit absence** (`declared_relationship != "none"`).

**What must be true regardless of domain (validated):**

1. Explicit `"none"` means **no relationship constituted** → upstream failure, `/compare` not invoked.  
   - Evidence: `app/core/admission_gate.py` L12–18; ABAN `test_3a_no_relationship_declared`; VB-1 `expected-outputs.json`; `evidence/aban-v0.3-api-test/3a-request.json`.
2. **Constitution of relationship ≠ authorization to invoke comparison.** A non-`none` declaration alone is insufficient.  
   - Evidence: `admission_gate.py` L20–27 (null `invocation_record` → unauthorized); VB-4; ABAN `test_3c_*`.
3. Complete comparison payloads **cannot bypass** absent relationship.  
   - Evidence: ABAN `test_admission_fail_does_not_require_comparison_payload`; cross-domain supplementary manual verification (`admission_none_blocks_compare`: `compare_invoked=false` with full comparison present).

**Evidence gap:** The experiments validate a **binary constituted / not constituted** gate keyed off `"none"`. They do **not** validate what evidential checks must hold for a non-`none` declaration to be *true in the world*—only that the gate treats non-`none` as "relationship declared" for downstream invocation checks.

---

### Q2 — Relationship evidence vs. relationship state

**Observed shape (both experiments):**

| Layer | Field(s) | Role |
|---|---|---|
| Declared state | `declared_relationship` | Coarse enum: `none` vs domain-specific non-none literals |
| Supporting evidence | `invocation_record.authority_reference`, `invocation_reason`, `timestamp` | Formal reference + narrative justification for invocation |
| Authorization evidence | `invocation_record.sign_off[]` | Independent signers |

**ABAN suggests:** `protected_rule_ref` + `authority_reference: protected_rule://...` + RAO/ministry sign-off roles (`tests/test_admission_wrapper.py`, `3b-request.json`).

**Vendor/Buyer suggests:** `declared_reference` + `authority_reference: formal-agreement://sow-msa-...` + Procurement/Security roles (`evidence/cross-domain-transfer-v01/vb-2-request.json`, README domain table).

**Critical observation:** `evaluate_admission()` **does not read** `declared_relationship` values other than `"none"` (`admission_gate.py` L12–45). Non-none literals are **domain-specific labels** carried in schema but **not interpreted** by the gate. Invocation authority is evaluated only from `invocation_record` structure.

**Answer:** In current evidence, **state and evidence are partially separated** (`declared_relationship` vs `invocation_record`), but **not cleanly**. The enum mixes absence (`none`) with domain-specific "relationship type" labels that the gate ignores. A generic contract likely needs:

- a domain-neutral **relationship-present** boolean or equivalent, **plus**
- an **evidence bundle** (reference, reason, sign-offs) supplied by the domain adapter.

Whether that separation should be explicit in schema is **UNRESOLVED** (see Section G).

---

### Q3 — Generic invocation-authority invariant

**Minimal structure validated (both domains):**

When relationship is non-`none`, routing to `/compare` requires an `invocation_record` where:

1. `invoked_by` is present.
2. `sign_off` contains **at least two entries**.
3. At least **two distinct `authorized_by` values** remain after **excluding** `invoked_by`.  
   - Evidence: `admission_gate.py` L29–37; ABAN `test_3c`, `test_3d`; VB-4 `expected-outputs.json`.

**Domain-invariant phrasing (conceptual, evidence-supported):**  
*"Invocation requires multiple independent authorizing actors, excluding the invoking actor, evidenced by distinct signer identities."*

**Is N=2 domain-invariant?** **`UNRESOLVED`.** Both experiments hardcode `N=2` in gate logic and fixtures. No experiment varied N (e.g., N=3 required, N=1 rejected with different policy). The **exclusion of `invoked_by`** is evidence-supported (ABAN 3d, VB-4); the **numeric threshold 2** is an observed implementation choice, not independently validated as domain-invariant.

**Role titles** (`RAO_Officer`, `Procurement Manager`) are **`DOMAIN_SPECIFIC_REPRESENTATION`** — not read by gate logic except as opaque strings on `SignOffEntry.role`.

---

### Q4 — Domain mapping boundary

**Concrete boundary line:**

```
┌─────────────────────────────────────────────────────────────┐
│ GENERIC ADMISSION CONTRACT (evidence-supported shape)        │
│  • relationship_absent: yes/no  (currently: == "none")       │
│  • invocation_record?: {                                     │
│       invoked_by, authority_reference, invocation_reason,    │
│       timestamp, sign_off[{authorized_by, role, authorized_at}]│
│    }                                                         │
│  • evaluate: if absent → fail; else if invocation invalid →  │
│       fail; else → route to /compare                         │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ maps into
┌─────────────────────────────────────────────────────────────┐
│ DOMAIN-SPECIFIC REPRESENTATION (must NOT enter generic core) │
│  • declared_relationship literals (4 known + future domain)  │
│  • authority_reference URI/scheme conventions              │
│  • role titles, ministry names, RAO identifiers            │
│  • comparison.decision field vocabulary (intent vs assurance)│
│  • AuthorityContext field values (domains, policy refs)      │
└─────────────────────────────────────────────────────────────┘
```

**Evidence:** Gate branches only on `"none"` and invocation structure; VB `test_invariant_e_domain_independence_no_aban_vocabulary`; cross-domain README classification **A — STRUCTURALLY_TRANSFERABLE** (lexical/schema extension only).

**Stop line:** Anything below `evaluate_admission()` return `{"passed": True}` is **`/compare` / L3 territory** and was intentionally not modified in either experiment.

---

### Q5 — Generic upstream-failure outcome naming

**Observed outcome (both experiments):**

```json
{
  "passed": false,
  "finding": "COORDINATION_NOT_CONSTITUTED",
  "sub_reason": "no_relationship_declared" | "invocation_unauthorized",
  "compare_invoked": false
}
```

**Is `COORDINATION_NOT_CONSTITUTED` domain-neutral?** **No — ABAN-flavored wrapper vocabulary.** "Coordination" reflects cross-ministry ABAN framing. Vendor/Buyer tests reuse the same string without semantic harm only because the gate is domain-agnostic at logic level.

**Evidence-supported sub-reasons (more portable):**

| `sub_reason` | Meaning | Evidence |
|---|---|---|
| `no_relationship_declared` | Relationship absent | 3a, VB-1 |
| `invocation_unauthorized` | Relationship present but invocation fails authority structure | 3c, 3d, VB-4, invariant B |

**Naming candidate (NOT a final decision):**  
`COMPARISON_PRECONDITION_NOT_MET` with machine sub-reasons above. Alternative candidate: `ROUTE_TO_COMPARE_DENIED`.

**Distinction from L3 failure:** Upstream admission failure **never sets** `comparability_classification`. VB-1/VB-4 outputs lack `FORMALLY_INCOMPARABLE`. VB-2 reaches `FORMALLY_INCOMPARABLE` **only after** admission pass and `/compare` invocation (`compare_invoked: true`).

---

### Q6 — Routing boundary (prevent upstream failure → `FORMALLY_INCOMPARABLE`)

**Validated pattern (ABAN v0.3 + cross-domain):**

```
POST /admit-and-compare
  → evaluate_admission(case_admission)     # PRECONDITION LAYER
  → if not passed: return upstream failure (compare_invoked=false)  # STOP
  → if comparison missing: HTTP 422
  → compare(comparison)                    # L3 — only reachable if admission passed
  → attach compare_invoked=true
```

Evidence: `app/routes/admit_and_compare.py` L19–38 (frozen ABAN branch); VB-1/VB-4 actual outputs (`compare_invoked=false`, no classification fields).

**Where this attaches on `main` today:**

Current `main` (`app/main.py` L18–20) registers only `/verify-equivalence`, `/canonicalize`, `/compare`. **No admission route exists on main.**

**Behavioral integration point (conceptual, no diff written):**

1. Add a **new HTTP surface** (e.g. `/admit-and-compare` or `/precondition-and-compare`) registered in `app/main.py` **alongside** existing `/compare`.
2. Implement a **thin orchestrator** mirroring `admit_and_compare.py`: call generic precondition evaluator first; call existing `compare()` only on pass.
3. **Do not** embed precondition checks inside `_classify_comparability()` or `_has_shared_canonical_reference()` (`app/routes/compare.py` on main L64–82).

**Preserve:** Direct `/compare` remains available for L3-only callers (main's current behavior).

**Main divergence warning:** `main` `/compare` at `32956e0` differs materially from ABAN branch `/compare` (main lacks `_has_governing_condition_translation`, exposes hash-divergence labels publicly). Main integration must reconcile **which L3 engine** is canonical before attaching preconditions—not settled by these experiments (see Section G).

---

## Section 4 — Future L1/L2 insertion (architecture only)

**Current gate shape:** Single linear function `evaluate_admission()` with two checks (relationship absent; invocation unauthorized).

**Accommodation assessment:**

| Approach | L1/L2 fit | Restructuring risk |
|---|---|---|
| **Chain inside expanded `evaluate_admission()`** | Possible short-term | High — becomes monolithic; L1/L2 concerns mixed with relationship/invocation |
| **Pipeline of precondition evaluators** | Better structural fit | Medium — requires orchestrator refactor not evidenced yet |
| **Separate routes per precondition stage** | Possible | Not evidenced; increases caller burden |

**Plain statement:** The **routing-before-`/compare` property** validated by experiments **does accommodate** future L1/L2 evaluators **if** implemented as **additional upstream stages** in the orchestrator (same stop-before-L3 rule). The **current single-function gate shape** does **not** cleanly express multiple precondition types without later restructuring.

**Explicitly not designed here:** L1 referent continuity checks, L2 governing-basis currency checks, field names, schemas, or classification values.

---

## Section 5 — Three-way semantic comparison

| Semantic aspect | Current `main` (`32956e0`) | ABAN v0.3 wrapper (`f4e0e69`) | Cross-domain transferred behavior | Classification |
|---|---|---|---|---|
| Admission / relationship gate | None — `/compare` always runs | `evaluate_admission()` before `/compare` | Same gate logic, different `declared_relationship` literals | `ALREADY_EVIDENCE_SUPPORTED_GENERIC` (gate pattern); `DOMAIN_SPECIFIC_REPRESENTATION` (literals) |
| Invocation authority check | N/A | ≥2 distinct signers excl. `invoked_by` | Same | `ALREADY_EVIDENCE_SUPPORTED_GENERIC` (structure); `UNRESOLVED` (N=2 threshold) |
| Upstream failure outcome | N/A | `COORDINATION_NOT_CONSTITUTED` + sub_reason | Same strings reused | `DOMAIN_SPECIFIC_REPRESENTATION` (finding label); `ALREADY_EVIDENCE_SUPPORTED_GENERIC` (sub_reasons, routing) |
| `compare_invoked` flag | N/A | Present on wrapper responses | Present | `ALREADY_EVIDENCE_SUPPORTED_GENERIC` |
| Missing comparison after pass | N/A | HTTP 422 `MISSING_COMPARISON_PAYLOAD` | Same | `ALREADY_EVIDENCE_SUPPORTED_GENERIC` |
| L3: shared reference check | `policy_reference` equality | Same | Same (VB-2/3) | `ALREADY_EVIDENCE_SUPPORTED_GENERIC` |
| L3: governing condition translation | **Not implemented on main** | `_has_governing_condition_translation()` | Exercised (VB-2 fracture) | `FUTURE_EXTENSION_ONLY` relative to main; evidenced on ABAN branch only |
| L3: public fracture labels | Includes hash-divergence labels | Narrowed public set (isolation remediation) | Uses ABAN-branch L3 engine | `UNRESOLVED` for main integration |
| `AuthorityContext.governing_condition` | **Absent on main schema** | Present on ABAN branch | Used in VB fixtures | `UNRESOLVED` / branch divergence |
| Domain vocabulary in admission | N/A | `protected_rule_ref`, `RAO_officer_flagged` | `declared_reference`, `flagged_authority` | `DOMAIN_SPECIFIC_REPRESENTATION` |
| L1 referent continuity | Not implemented | Not implemented | Not implemented | `FUTURE_EXTENSION_ONLY` |
| L2 governing-basis currency | Not implemented | Not implemented | Not implemented | `FUTURE_EXTENSION_ONLY` |

---

## A. Generic semantic invariants (extracted)

| ID | Invariant | Evidence |
|---|---|---|
| G-1 | Relationship absence (`none`) blocks comparison routing regardless of comparison payload completeness | `admission_gate.py` L12–18; ABAN 3a + `test_admission_fail_does_not_require_comparison_payload`; VB-1; supplementary manual verification |
| G-2 | Non-none relationship declaration alone does not authorize invocation | `admission_gate.py` L20–27; VB-4; ABAN 3c |
| G-3 | Invocation requires structurally valid authorization record with multiple distinct signers excluding invoker | `admission_gate.py` L29–37; ABAN 3d; VB-4 |
| G-4 | Admission pass does not imply L3 comparison basis exists | VB-2 → `FORMALLY_INCOMPARABLE` after pass; invariant C tests |
| G-5 | Different L3 judgments with valid basis yield `NON_EQUIVALENT`, not `FORMALLY_INCOMPARABLE` | VB-3; ABAN 3b vs translation test distinction |
| G-6 | Precondition evaluation sits **before** `/compare`; failures must not reach `_classify_comparability()` | `admit_and_compare.py` L19–37; VB-1/VB-4 outputs lack classification |
| G-7 | Gate logic is independent of domain-specific relationship literals (except `none`) | `evaluate_admission()` has no branches on ABAN/VB literals; cross-domain README + invariant E |

---

## B. Domain-specific representations that must NOT enter core

**Known four literals (explicitly not a universal ontology):**

- `protected_rule_ref` (ABAN)
- `RAO_officer_flagged` (ABAN)
- `declared_reference` (Vendor/Buyer experiment)
- `flagged_authority` (Vendor/Buyer experiment)

**Additional domain-specific representations discovered:**

- `authority_reference` URI/scheme conventions (`protected_rule://`, `formal-agreement://`)
- Sign-off `role` strings (RAO_Officer, Procurement Manager, etc.)
- ABAN ministry / RAO actor identifiers in fixtures
- Comparison `decision` shapes (`intent` vs `assurance` / `acceptance`)
- Finding label `COORDINATION_NOT_CONSTITUTED` (coordination-flavored)
- ABAN-specific `AuthorityContext` domain strings when used as fixtures only

---

## C. Candidate generic admission contract (conceptual only)

```text
INPUT:
  relationship:
    present: boolean   # domain maps its declared type → present/absent
  invocation:
    invoked_by: ActorId
    authority_reference: string   # opaque to generic core; domain interprets
    invocation_reason: string
    timestamp: string
    sign_offs: [{ authorized_by: ActorId, role: string, authorized_at: string }]

EVALUATE (generic core — no domain literals):
  if not relationship.present:
    return UPSTREAM_FAIL(sub_reason=no_relationship_declared)

  if invocation missing or sign_offs invalid under policy:
    # policy presently evidenced as: count(sign_offs) >= 2 AND
    # distinct(authorized_by excluding invoked_by) >= 2
    return UPSTREAM_FAIL(sub_reason=invocation_unauthorized)

  return UPSTREAM_PASS

ROUTE:
  if UPSTREAM_PASS and comparison_payload present:
    invoke existing compare(comparison_payload)   # L3 unchanged
  elif UPSTREAM_PASS and comparison_payload absent:
    return HTTP 422 MISSING_COMPARISON_PAYLOAD
```

**Domain adapter responsibility (outside generic core):** map domain relationship type + evidence into `relationship.present` and populate `invocation` fields. **Not validated as a production adapter pattern** — inferred from observed gate behavior.

---

## D. Main integration boundary

**Attach point:** New orchestrator route in `app/main.py` router registration, delegating to:

1. Generic precondition evaluator (relationship + invocation only, per scope)
2. Existing `app.routes.compare.compare()` on pass

**Main behavior change (behavioral description):**

- Callers using the new surface cannot reach L3 classification without passing precondition checks.
- Failed preconditions return upstream outcome with `compare_invoked=false` (or successor generic label).
- Direct `/compare` on main **continues unchanged** unless separately deprecated.

**Not in scope:** Merging ABAN-branch L3 changes (`governing_condition`, narrowed fractures) into main — required for parity with VB-2 evidence but **not part of admission extraction**.

---

## E. Failure-state / routing model

```text
[Request]
   │
   ▼
[Precondition layer: relationship + invocation] ──fail──▶ UPSTREAM_FAIL
   │                              compare_invoked=false
   │                              (no comparability_classification)
   pass
   │
   ▼
[Comparison payload present?] ──no──▶ HTTP 422
   │
   yes
   ▼
[L3 /compare: basis checks + classification]
   │
   ├── FORMALLY_INCOMPARABLE  (basis missing — NOT upstream fail)
   ├── NON_EQUIVALENT         (basis present, judgments differ)
   └── EQUIVALENT
```

**Key invariant:** Upstream fail ≠ `FORMALLY_INCOMPARABLE`. Evidence: VB-1/VB-4 vs VB-2.

---

## F. Future L1/L2 insertion point

Insert **after** relationship + invocation checks, **before** `compare()`:

```text
evaluate_relationship()
  → evaluate_invocation_authority()
  → [future: evaluate_l1_referent_continuity()]
  → [future: evaluate_l2_governing_basis_currency()]
  → route_to_compare() or upstream_fail
```

Current monolithic `evaluate_admission()` would need **pipeline restructuring** to keep concerns separable. Experiments validate the **outer routing property**, not the **internal multi-stage shape**.

---

## G. Open questions (not settled by N=2 experiments)

1. **Is N=2 authorization threshold domain-invariant?** Only observed, not parameterized-tested.
2. **Should generic core use boolean `relationship.present` vs extensible enum?** Gate ignores non-none enum semantics today.
3. **Should `authority_reference` / `invocation_reason` be validated beyond presence?** Not evidenced.
4. **Generic name for upstream failure?** `COORDINATION_NOT_CONSTITUTED` is ABAN-flavored.
5. **Main vs ABAN-branch L3 divergence** — which engine is integration target? Main lacks governing-condition translation present in VB-2 evidence path.
6. **`docs/implementation-items.md` absent** — cannot cross-check staged fracture semantics / Item 1 OBSERVED status from repo.
7. **README `NOT_EVALUATED` / seven-layer / Failure-Semantic sections absent on main** — architecture context referenced in task not locatable in evidence inputs.
8. **Third domain** — transfer claim remains N=2 domains; cross-domain evidence not on a committed branch tip (stash only).
9. **Relationship evidence vs state** — clean separation not fully evidenced; may require adapter pattern (→ borders `TRANSFERABLE_WITH_DOMAIN_ADAPTER` if chosen later).

---

## H. Recommendation

### **`NEEDS_MORE_EVIDENCE`**

**Rationale (evidence-based):**

1. **Only two domains** exercised (ABAN + synthetic Vendor/Buyer). Task explicitly warns against promoting N=1 (here N=2) to production ontology.
2. **N=2 signer threshold** is implemented but not validated as domain-invariant across domains or configurations.
3. **Relationship state vs evidence** separation is architecturally suggested but **not cleanly evidenced** as a production contract shape.
4. **Upstream failure naming** remains ABAN-flavored; generic naming is explicitly deferred but blocks main integration clarity.
5. **Main L3 engine ≠ ABAN-branch L3 engine** — integration target for wrapper attachment on main is ambiguous; VB-2 fracture behavior depends on ABAN-branch compare features absent on main.
6. **Requested context files missing** (`implementation-items.md`, README sections) limit cross-check against documented main design direction.
7. **Cross-domain evidence provenance** is stash/WIP, not committed — weakens audit trail for implementation tasks.

**What *is* ready (do not lose):** The **routing invariant** (precondition before `/compare`), **invocation structure** (multi-signer excl. invoker), and **failure/routing separation** from `FORMALLY_INCOMPARABLE` are sufficiently evidenced to inform a **future** implementation task—after gaps above are closed.

**Not recommended now:** `DO_NOT_GENERALIZE_YET` — experiments did validate transferable *structure*; `READY_FOR_IMPLEMENTATION_TASK` — main/L3 divergence and open naming/evidence gaps remain.

---

## Review metadata

| Item | Value |
|---|---|
| Review branch | `review/generic-admission-semantics-v01` |
| Branched from | `main` @ `32956e0635d68037a79f60eff42bd6c835abf9c5` |
| Files modified in this review | `docs/generic-admission-semantics-extraction-v01.md` only |
| `app/` modified | **No** |
| Main modified | **No** |
| Code-change branch created | **No** (documentation-only review branch) |
| Merged | **No** |
