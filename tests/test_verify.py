from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_verify_same_invariant_returns_true() -> None:
    payload = {
        "decision_a": {
            "target": {"resource": "invoice-123"},
            "intent": {"action": "approve"},
            "parameters": {"threshold": 0.9, "region": "apac"},
            "policy_fields": {"policy_version": "v1"},
            "metadata": {"ignored": True},
        },
        "decision_b": {
            "metadata": {"ignored": False},
            "policy_fields": {"policy_version": "v1"},
            "parameters": {"region": "apac", "threshold": 0.9},
            "intent": {"action": "approve"},
            "target": {"resource": "invoice-123"},
        },
    }

    response = client.post("/verify-equivalence", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert data["equivalent"] is True
    assert data["invariant_identity_match"] is True
    assert data["canonical_hash_a"] != data["canonical_hash_b"]
