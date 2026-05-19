from typing import Any


def compute_boundary_diff(a: Any, b: Any, path: str = "") -> list[dict[str, Any]]:
    diffs: list[dict[str, Any]] = []

    if isinstance(a, dict) and isinstance(b, dict):
        keys = sorted(set(a.keys()) | set(b.keys()))
        for key in keys:
            next_path = f"{path}.{key}" if path else str(key)
            diffs.extend(compute_boundary_diff(a.get(key), b.get(key), next_path))
        return diffs

    if isinstance(a, list) and isinstance(b, list):
        max_len = max(len(a), len(b))
        for idx in range(max_len):
            value_a = a[idx] if idx < len(a) else None
            value_b = b[idx] if idx < len(b) else None
            next_path = f"{path}[{idx}]"
            diffs.extend(compute_boundary_diff(value_a, value_b, next_path))
        return diffs

    if a != b:
        diffs.append({
            "field": path,
            "classification": "invariant_boundary_mismatch",
            "semantic_impact": "decision_identity_divergence",
            "a": a,
            "b": b,
        })

    return diffs
