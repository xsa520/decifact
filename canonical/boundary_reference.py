import hashlib, json


def compute_boundary_context_hash(
        authority_context: dict) -> str:
    normalized = json.dumps(
        authority_context, sort_keys=True,
        ensure_ascii=False, indent=2)
    return hashlib.sha256(
        normalized.encode("utf-8")).hexdigest()


def build_boundary_reference(
        canonical_hash: str,
        boundary_context_hash: str,
        version: str = "1.0.0") -> str:
    combined = (
        f"{canonical_hash}:"
        f"{boundary_context_hash}:{version}"
    )
    return hashlib.sha256(
        combined.encode("utf-8")).hexdigest()
