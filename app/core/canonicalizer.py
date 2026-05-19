import json
from typing import Any


def canonicalize_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))
