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
    raw = response.json()

    normalized_diff = []
    for item in raw["invariant_boundary_diff"]:
        path = item["field"]
        if path.startswith("parameters."):
            path = path.removeprefix("parameters.")
        normalized_diff.append({"path": path, "left": item["a"], "right": item["b"]})

    return {
        "invariant_identity_match": raw["invariant_identity_match"],
        "diff": normalized_diff,
    }


def test_threshold_mismatch_is_explicitly_captured(monkeypatch) -> None:
    decision_a = {
        "intent": {"action": "approve"},
        "target": {"resource": "invoice-123"},
        "parameters": {"policy": {"threshold": 0.8}},
        "policy_fields": {"version": "v1"},
    }
    decision_b = {
        "intent": {"action": "approve"},
        "target": {"resource": "invoice-123"},
        "parameters": {"policy": {"threshold": 0.7}},
        "policy_fields": {"version": "v1"},
    }

    result = verify(decision_a, decision_b, monkeypatch)

    assert result["invariant_identity_match"] is False
    assert {"path": "policy.threshold", "left": 0.8, "right": 0.7} in result["diff"]
