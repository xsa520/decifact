from typing import Any


def extract_invariant_boundary(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "intent": decision.get("intent"),
        "target": decision.get("target"),
        "parameters": decision.get("parameters", {}),
        "policy_fields": decision.get("policy_fields", {}),
    }
