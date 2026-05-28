Decifact does not determine authority.
It exposes comparability boundaries.

# Decifact

**Cross-system decision equivalence based on invariant boundaries.**

Built on Guardian v0.2 — Decision Equivalence Specification.

---

## The Seam This Addresses

Most AI governance work focuses on a single system:
- Does this agent behave correctly?
- Is this decision auditable?
- Does this output comply with policy?

These are necessary questions. But they leave a deeper problem unaddressed.

**When independently governed systems begin coordinating — sharing decisions, delegating authority, producing joint consequences — a prior question must be answered first:**

> Were the governance conditions across these systems ever established as comparable before their outputs began creating shared institutional dependencies?

This is not a runtime enforcement problem. It is a precondition problem.

Without comparability verification at this layer, coordination proceeds on assumptions that may never have been valid. Operational success can be mistaken for structural resilience. The gap widens unnoticed until the cost of closure is prohibitive.

Decifact is the minimal inspectable surface for this layer.

---

## The Problem

When two independently governed AI systems process the same input and produce different decisions, most systems cannot answer:

- Are these decisions actually different?
- If so, where exactly do they diverge?
- Is the divergence structurally significant, or just representational noise?
- Were the governance conditions under which each decision was made ever canonically comparable?

Without a standard for decision equivalence, cross-system coordination is undefined.

> "Without decision equivalence, economic correctness is undefined."
> — Guardian v0.2 Specification

> "The canonical boundary must exist before layer instantiation."
> — Guardian Constitutional Invariant

---

## Where Decifact Sits

```
┌─────────────────────────────────────────────────────────┐
│  Independently Governed System A                        │
│  (its own policy, authority, execution environment)     │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  DECIFACT — Comparability Boundary Layer                │
│                                                         │
│  "Were these decisions produced under governance        │
│   conditions that were ever canonically comparable?"    │
│                                                         │
│  /verify-equivalence  /canonicalize  /compare           │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Independently Governed System B                        │
│  (its own policy, authority, execution environment)     │
└─────────────────────────────────────────────────────────┘
```

Decifact does not govern either system.
It does not transfer authority between them.
It exposes whether their decisions share the invariant boundary required for meaningful coordination.

**This question must be answered before coordination begins — not after consequences have already formed.**

---

## What This Does

Determines whether two decisions share the same **invariant boundary** — the minimal semantic set that defines a decision, independent of execution artifacts, transport encoding, or system-specific representation.

- **Deterministic**: same input always produces same output
- **Transparent**: differences are explicit, not opaque
- **Minimal**: no LLM calls, no external dependencies
- **Composable**: works alongside any agent framework
- **Independent**: sits outside the systems it evaluates — no shared write domain, no equity in either system

---

## Endpoints

| Endpoint | Function |
|----------|----------|
| `POST /verify-equivalence` | Decision equivalence verification |
| `POST /canonicalize` | Canonical boundary engine |
| `POST /compare` | Cross-runtime fracture inspection |

---

## Quick Start

### Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Call the API

```bash
curl -X POST https://<your-endpoint>/verify-equivalence \
  -H "Content-Type: application/json" \
  -d '{
    "decision_a": {
      "intent": "execute_trade",
      "target": "AAPL",
      "parameters": {
        "direction": "buy",
        "size": 100,
        "threshold": 0.8
      },
      "policy_context": "risk_conservative"
    },
    "decision_b": {
      "intent": "execute_trade",
      "target": "AAPL",
      "parameters": {
        "direction": "buy",
        "size": 100,
        "threshold": 0.7
      },
      "policy_context": "risk_conservative"
    }
  }'
```

### Response — Non-Equivalent

```json
{
  "equivalent": false,
  "invariant_identity_match": false,
  "canonical_hash_a": "a3f9c2...",
  "canonical_hash_b": "b7d1e4...",
  "invariant_boundary": {
    "a": {
      "intent": "execute_trade",
      "target": "AAPL",
      "parameters": { "direction": "buy", "size": 100, "threshold": 0.8 },
      "policy_context": "risk_conservative"
    },
    "b": {
      "intent": "execute_trade",
      "target": "AAPL",
      "parameters": { "direction": "buy", "size": 100, "threshold": 0.7 },
      "policy_context": "risk_conservative"
    }
  },
  "invariant_boundary_diff": [
    {
      "path": "parameters.threshold",
      "a": 0.8,
      "b": 0.7
    }
  ],
  "call_count": 1
}
```

### Response — Equivalent

```json
{
  "equivalent": true,
  "invariant_identity_match": true,
  "invariant_boundary_diff": [],
  "call_count": 2
}
```

---

## What Is NOT Equivalence

The following MUST NOT be used to determine equivalence:

| Method | Why It Fails |
|--------|-------------|
| `outcome_a == outcome_b` | Same outcome can come from different decisions |
| `hash(serialized_a) == hash(serialized_b)` | Structural equality ≠ semantic equivalence |
| `identity_a == identity_b` | Same actor can produce non-equivalent decisions |
| `both_passed_audit == true` | Independent audit results ≠ cross-system comparability |

---

## Integration Example

```python
import requests

def check_equivalence(decision_a, decision_b):
    response = requests.post(
        "https://<your-endpoint>/verify-equivalence",
        json={"decision_a": decision_a, "decision_b": decision_b}
    )
    result = response.json()

    if not result["equivalent"]:
        print(f"Decisions diverge at: {result['invariant_boundary_diff']}")

    return result["equivalent"]
```

---

## Scope

This engine evaluates **decision equivalence only** (Guardian v0.2).

| Concern | Scope |
|---------|-------|
| Decision equivalence | ✅ This engine |
| Decision acceptance | ❌ Guardian v0.3 (upcoming) |
| Execution correctness | ❌ Out of scope |
| Identity validation | ❌ Out of scope |
| Runtime policy enforcement | ❌ Out of scope — that is a different layer |
| Governance of either system | ❌ Out of scope — Decifact sits between systems, not inside them |

Equivalence determines whether two decisions are the same decision.

Acceptance determines whether a decision is valid within a context.

These concerns MUST remain strictly separated.

**Decifact does not tell systems what to do. It exposes whether they were ever comparable enough for coordination to be meaningful.**

---

## Relation to Guardian

Decifact is the reference implementation of Guardian v0.2 Decision Equivalence Specification.

Guardian defines the constitutional conditions under which independently governed systems can determine whether their decisions remain canonically comparable without inheriting each other's jurisdiction.

Guardian v0.3 (acceptance layer) will build on this equivalence primitive.

Specification: [xsa520/guardian](https://github.com/xsa520/guardian)

---

## Status

Stable for equivalence verification in controlled environments.
Deployed instances processing live decisions since 2026-01.

Operational substrate: Alpha System — running since 2026-02-11, RFC3161 evidence chain, 77+ replay cycles. Internal only.

---

## Explainer

See: [docs/decifact-explainer.pdf](docs/decifact-explainer.pdf)

---

## Examples

Run the minimal comparability demo:

    python3 examples/verify_demo.py examples/example-decisions.json

See: [examples/verify_demo.py](examples/verify_demo.py)
