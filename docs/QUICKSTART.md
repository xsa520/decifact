## 1. The Problem

Two AI systems can each have valid governance records, pass every audit, and still be operating on incommensurable decision logic.

When they coordinate — sharing decisions, delegating authority, producing joint consequences — most systems assume their governance conditions are comparable.

They are often not.

Decifact exposes that boundary before coordination begins.

## 2. Three Scenarios

**Scenario A — Hospital Triage**
Hospital A (UK framework) approves AI-assisted triage.
Hospital B (UAE framework) approves AI-assisted triage.
Same intent. Different governance foundations.
Are they operating under comparable conditions?

**Scenario B — Cross-Ministry AI Deployment**
Agriculture Ministry approves an AI crop-monitoring system.
Finance Ministry approves the same system for subsidy allocation.
Each approval is internally valid.
Can these approvals be placed on the same comparison basis?

**Scenario C — Multi-Agent Financial System**
Agent A produces: BUY NVDA
Agent B produces: SELL NVDA
Both are operating under valid policies.
Is this a disagreement — or an incomparability?

## 3. The Three Classifications

| Classification | Meaning |
|---|---|
| EQUIVALENT | Shared comparison basis exists. Governance conditions are identical. |
| NON_EQUIVALENT | Shared comparison basis exists. Conditions differ. Valid disagreement. |
| FORMALLY_INCOMPARABLE | No shared comparison basis detected. Not a disagreement. A structural finding. |

> FORMALLY_INCOMPARABLE is not an error. It is a first-class governance result.

## 4. Quickstart (5 minutes)

The example below runs Scenario A (Hospital Triage) — two independently approved systems being checked against each other before coordination begins.

### Install and run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Call /compare — Hospital Example

```bash
curl -X POST http://127.0.0.1:8000/compare -H "Content-Type: application/json" -d '{"runtime_a":{"decision":{"intent":"deploy_ai_triage","target":"patient_triage_module"},"authority_context":{"authority_domain":"UK-Health-Ministry","policy_reference":"UK-AI-Framework-v1","execution_context":"deploy","admissibility_scope":"clinical-decision-support"}},"runtime_b":{"decision":{"intent":"deploy_ai_triage","target":"patient_triage_module"},"authority_context":{"authority_domain":"UAE-Health-Ministry","policy_reference":"UAE-AI-Framework-v2026","execution_context":"deploy","admissibility_scope":"clinical-oversight"}}}'
```

runtime_a:
decision.intent = "deploy_ai_triage"
decision.target = "patient_triage_module"
authority_context.authority_domain = "UK-Health-Ministry"
authority_context.policy_reference = "UK-AI-Framework-v1"
authority_context.admissibility_scope = "clinical-decision-support"

runtime_b:
decision.intent = "deploy_ai_triage"
decision.target = "patient_triage_module"
authority_context.authority_domain = "UAE-Health-Ministry"
authority_context.policy_reference = "UAE-AI-Framework-v2026"
authority_context.admissibility_scope = "clinical-oversight"

### Expected response

```json
{"comparability_classification":"FORMALLY_INCOMPARABLE","fracture_boundary":["no_shared_canonical_reference"],"replayable":true}
```

### What this means

The hospitals are not disagreeing.
They are operating under different governance references.
Coordination between them would require establishing a shared canonical reference first — not just exchanging data.

## 5. Three Endpoints

`POST /canonicalize` — Extract canonical invariants from a governance object
`POST /compare` — Classify two governance decisions: EQUIVALENT, NON_EQUIVALENT, or FORMALLY_INCOMPARABLE
`POST /verify-equivalence` — Verify whether two governance decisions share the same invariant boundary

## 6. What Decifact Does NOT Do

- Does not govern either system
- Does not transfer authority between systems
- Does not determine which system is correct
- Does not replace runtime enforcement
- Does not require systems to share infrastructure

## 7. One line at the bottom

> Comparability before coordination. Decifact exposes the boundary.
