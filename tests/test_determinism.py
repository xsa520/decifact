import copy

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def verify(decision_a: dict, decision_b: dict, monkeypatch) -> dict:
    # Ensure deterministic response snapshots by neutralizing runtime call counter.
    monkeypatch.setattr("app.routes.verify.increment_call_count", lambda: None)
    monkeypatch.setattr("app.routes.verify.get_call_count", lambda: 0)
    response = client.post(
        "/verify-equivalence",
        json={"decision_a": decision_a, "decision_b": decision_b},
    )
    assert response.status_code == 200
    return response.json()


def test_repeated_calls_are_exactly_identical(monkeypatch) -> None:
    decision_a = {
        "intent": {"action": "approve"},
        "target": {"resource": "invoice-123"},
        "parameters": {"policy": {"threshold": 0.8}, "region": "apac"},
        "policy_fields": {"version": "v1"},
    }
    decision_b = copy.deepcopy(decision_a)

    outputs = [verify(decision_a, decision_b, monkeypatch) for _ in range(10)]

    first = outputs[0]
    for output in outputs[1:]:
        assert output == first


def test_stress_consistency_1000_runs(monkeypatch) -> None:
    decision_a = {
        "intent": {"action": "approve"},
        "target": {"resource": "invoice-123"},
        "parameters": {"policy": {"threshold": 0.8}},
        "policy_fields": {"version": "v1"},
    }
    decision_b = copy.deepcopy(decision_a)

    baseline = verify(decision_a, decision_b, monkeypatch)
    for _ in range(1000):
        current = verify(decision_a, decision_b, monkeypatch)
        assert current == baseline
