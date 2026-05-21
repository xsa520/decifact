import hashlib, json


def compute_canonical_hash(canonical_object: dict) -> str:
    cleaned = {
        k: ("" if "hash" in k.lower()
                or "reference" in k.lower()
            else v)
        for k, v in canonical_object.items()
    }
    normalized = json.dumps(
        cleaned, sort_keys=True,
        ensure_ascii=False, indent=2)
    return hashlib.sha256(
        normalized.encode("utf-8")).hexdigest()
