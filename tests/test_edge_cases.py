from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def verify(decision_a: dict, decision_b: dict, monkeypatch) -> dict:
    monkeypatch.setattr("app.routes.verify.increment_call_count", lambda: None)
    monkeypatch.setattr("app.routes.verify.get_call_count", lambda: 0)
    response = client.post(
        "/verify-equivalence",
        json={"decision_a": decision_a, "decision_b": decision_b},
    )
    assert response.status_code == 200
    return response.json()


def test_extra_field_produces_stable_diff(monkeypatch) -> None:
    decision_a = {
        "intent": {"action": "approve"},
        "target": {"resource": "invoice-123"},
        "parameters": {"x": 1},
        "policy_fields": {"version": "v1"},
    }
    decision_b = {
        "intent": {"action": "approve"},
        "target": {"resource": "invoice-123"},
        "parameters": {"x": 1, "extra": "value"},
        "policy_fields": {"version": "v1"},
    }

    first = verify(decision_a, decision_b, monkeypatch)
    second = verify(decision_a, decision_b, monkeypatch)

    assert first["invariant_identity_match"] is False
    assert first["invariant_boundary_diff"] == second["invariant_boundary_diff"]
    assert {
        "field": "parameters.extra",
        "classification": "invariant_boundary_mismatch",
        "semantic_impact": "decision_identity_divergence",
        "a": None,
        "b": "value",
    } in first["invariant_boundary_diff"]


def test_type_mismatch_is_not_equal(monkeypatch) -> None:
    decision_a = {
        "intent": {"action": "approve"},
        "target": {"resource": "invoice-123"},
        "parameters": {"threshold": 0.8},
        "policy_fields": {"version": "v1"},
    }
    decision_b = {
        "intent": {"action": "approve"},
        "target": {"resource": "invoice-123"},
        "parameters": {"threshold": "0.8"},
        "policy_fields": {"version": "v1"},
    }

    result = verify(decision_a, decision_b, monkeypatch)

    assert result["invariant_identity_match"] is False
    assert {
        "field": "parameters.threshold",
        "classification": "invariant_boundary_mismatch",
        "semantic_impact": "decision_identity_divergence",
        "a": 0.8,
        "b": "0.8",
    } in result["invariant_boundary_diff"]


def test_missing_field_is_detected(monkeypatch) -> None:
    decision_a = {
        "intent": {"action": "approve"},
        "target": {"resource": "invoice-123"},
        "parameters": {"threshold": 0.8, "region": "apac"},
        "policy_fields": {"version": "v1"},
    }
    decision_b = {
        "intent": {"action": "approve"},
        "target": {"resource": "invoice-123"},
        "parameters": {"threshold": 0.8},
        "policy_fields": {"version": "v1"},
    }

    result = verify(decision_a, decision_b, monkeypatch)

    assert result["invariant_identity_match"] is False
    assert {
        "field": "parameters.region",
        "classification": "invariant_boundary_mismatch",
        "semantic_impact": "decision_identity_divergence",
        "a": "apac",
        "b": None,
    } in result["invariant_boundary_diff"]


def test_nested_structure_difference_is_detected(monkeypatch) -> None:
    decision_a = {
        "intent": {"action": "approve"},
        "target": {"resource": "invoice-123"},
        "parameters": {"policy": {"limits": {"daily": 10}}},
        "policy_fields": {"version": "v1"},
    }
    decision_b = {
        "intent": {"action": "approve"},
        "target": {"resource": "invoice-123"},
        "parameters": {"policy": {"limits": {"daily": 12}}},
        "policy_fields": {"version": "v1"},
    }

    result = verify(decision_a, decision_b, monkeypatch)

    assert result["invariant_identity_match"] is False
    assert {
        "field": "parameters.policy.limits.daily",
        "classification": "invariant_boundary_mismatch",
        "semantic_impact": "decision_identity_divergence",
        "a": 10,
        "b": 12,
    } in result["invariant_boundary_diff"]
