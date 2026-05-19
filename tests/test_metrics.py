from pathlib import Path

from app.core import metrics


def test_metrics_file_persists_and_count_increases(tmp_path: Path) -> None:
    test_log_file = tmp_path / "verify.log"
    original_log_file = metrics.LOG_FILE
    metrics.LOG_FILE = test_log_file

    try:
        count_before = metrics.get_call_count()
        metrics.increment_call_count()
        count_after_first = metrics.get_call_count()
        metrics.increment_call_count()
        count_after_second = metrics.get_call_count()

        assert count_before == 0
        assert count_after_first == 1
        assert count_after_second == 2
        assert test_log_file.exists()
    finally:
        metrics.LOG_FILE = original_log_file


def test_metrics_count_persists_across_repeated_reads(tmp_path: Path) -> None:
    test_log_file = tmp_path / "verify.log"
    original_log_file = metrics.LOG_FILE
    metrics.LOG_FILE = test_log_file

    try:
        metrics.increment_call_count()
        metrics.increment_call_count()

        count_first_read = metrics.get_call_count()
        count_second_read = metrics.get_call_count()

        assert test_log_file.exists()
        assert count_first_read == 2
        assert count_second_read == 2
    finally:
        metrics.LOG_FILE = original_log_file
