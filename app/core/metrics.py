from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "logs" / "verify.log"


def increment_call_count() -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as file:
        timestamp = datetime.now(timezone.utc).isoformat()
        file.write(f"{timestamp}\n")


def get_call_count() -> int:
    if not LOG_FILE.exists():
        return 0
    with LOG_FILE.open("r", encoding="utf-8") as file:
        return sum(1 for _ in file)