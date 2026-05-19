import copy

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


def test_identical_structure_is_equivalent(monkeypatch) -> None:
    decision = {
        "intent": {"action": "approve"},
        "target": {"resource": "invoice-123"},
        "parameters": {"policy": {"threshold": 0.8}},
        "policy_fields": {"version": "v1"},
    }

    result = verify(decision, copy.deepcopy(decision), monkeypatch)

    assert result["invariant_identity_match"] is True
    assert result["invariant_boundary_diff"] == []


def test_same_data_different_key_order_is_equivalent(monkeypatch) -> None:
    decision_a = {
        "intent": {"action": "approve", "actor": "system"},
        "target": {"resource": "invoice-123", "type": "invoice"},
        "parameters": {"policy": {"threshold": 0.8}, "region": "apac"},
        "policy_fields": {"version": "v1", "jurisdiction": "US"},
    }
    decision_b = {
        "policy_fields": {"jurisdiction": "US", "version": "v1"},
        "parameters": {"region": "apac", "policy": {"threshold": 0.8}},
        "target": {"type": "invoice", "resource": "invoice-123"},
        "intent": {"actor": "system", "action": "approve"},
    }

    result = verify(decision_a, decision_b, monkeypatch)

    assert result["invariant_identity_match"] is True
    assert result["invariant_boundary_diff"] == []
