from app.core.boundary_diff import compute_boundary_diff


def test_boundary_diff_detects_exact_field() -> None:
    a = {
        "intent": {"action": "allow"},
        "target": {"resource": "doc-1"},
        "parameters": {"x": 1},
        "policy_fields": {"tier": "gold"},
    }
    b = {
        "intent": {"action": "deny"},
        "target": {"resource": "doc-1"},
        "parameters": {"x": 1},
        "policy_fields": {"tier": "gold"},
    }

    diffs = compute_boundary_diff(a, b)

    assert {
        "field": "intent.action",
        "classification": "invariant_boundary_mismatch",
        "semantic_impact": "decision_identity_divergence",
        "a": "allow",
        "b": "deny",
    } in diffs


def test_boundary_diff_handles_missing_key_and_is_deterministic() -> None:
    a = {
        "intent": {"action": "allow"},
        "target": {"resource": "doc-1"},
        "parameters": {"a": 1},
        "policy_fields": {"tier": "gold"},
    }
    b = {
        "intent": {"action": "allow"},
        "target": {"resource": "doc-1", "scope": "internal"},
        "parameters": {"a": 1},
        "policy_fields": {"tier": "gold"},
    }

    diffs_first = compute_boundary_diff(a, b)
    diffs_second = compute_boundary_diff(a, b)

    assert {
        "field": "target.scope",
        "classification": "invariant_boundary_mismatch",
        "semantic_impact": "decision_identity_divergence",
        "a": None,
        "b": "internal",
    } in diffs_first
    assert diffs_first == diffs_second
