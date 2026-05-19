# Decifact

Decision equivalence based on invariant boundaries.

Built on Guardian v0.2 — Decision Equivalence Specification.

---

## The Problem

When two AI agents process the same input and produce different decisions, most systems cannot answer:

- Are these decisions actually different?
- If so, where exactly do they diverge?
- Is the divergence structurally significant, or just representational noise?

Without a standard for decision equivalence, cross-system coordination is undefined.

> "Without decision equivalence, economic correctness is undefined."
> — Guardian v0.2 Specification

---

## What This Does

Determines whether two decisions share the same **invariant boundary** — the minimal semantic set that defines a decision, independent of execution artifacts, transport encoding, or system-specific representation.

- **Deterministic**: same input always produces same output
- **Transparent**: differences are explicit, not opaque
- **Minimal**: no LLM calls, no external dependencies
- **Composable**: works alongside any agent framework

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

Equivalence determines whether two decisions are the same decision.

Acceptance determines whether a decision is valid within a context.

These concerns MUST remain strictly separated.

---

## Relation to Guardian

Decifact is the reference implementation of Guardian v0.2 Decision Equivalence Specification.

Guardian v0.3 (acceptance layer) will build on this equivalence primitive.

Specification: [xsa520/guardian](https://github.com/xsa520/guardian)

---

## Status

Stable for equivalence verification in controlled environments.
Deployed instances processing live decisions since 2026-01.