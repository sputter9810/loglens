from pathlib import Path

import pytest

from loglens.input import (
    AllRecordsInvalidError,
    InputStats,
    LogInputError,
    iter_log_records,
)

SAMPLES = Path(__file__).parents[1] / "samples"


def test_mixed_sample_yields_valid_records_and_counts_skipped_lines() -> None:
    stats = InputStats()

    records = list(iter_log_records(SAMPLES / "mixed-input.log", stats))

    assert len(records) == 4
    assert [record.status for record in records] == [200, 404, 503, 201]
    assert stats.valid_records == 4
    assert stats.malformed_records == 4
    assert stats.blank_lines == 2
    assert stats.nonblank_lines == 8


def test_empty_sample_yields_no_records_without_error() -> None:
    stats = InputStats()

    assert list(iter_log_records(SAMPLES / "empty.log", stats)) == []
    assert stats.valid_records == 0
    assert stats.malformed_records == 0
    assert stats.blank_lines == 0


def test_blank_only_file_is_successful_and_counted(tmp_path: Path) -> None:
    path = tmp_path / "blank-only.log"
    path.write_text("\n  \n\t\n", encoding="utf-8")
    stats = InputStats()

    assert list(iter_log_records(path, stats)) == []
    assert stats.valid_records == 0
    assert stats.malformed_records == 0
    assert stats.blank_lines == 3


def test_all_invalid_sample_raises_after_counting_every_line() -> None:
    stats = InputStats()

    with pytest.raises(AllRecordsInvalidError):
        list(iter_log_records(SAMPLES / "all-invalid.log", stats))

    assert stats.valid_records == 0
    assert stats.malformed_records == 5
    assert stats.nonblank_lines == 5


def test_missing_file_is_a_concise_input_error(tmp_path: Path) -> None:
    with pytest.raises(LogInputError, match="cannot open") as exception:
        list(iter_log_records(tmp_path / "missing.log", InputStats()))

    assert exception.value.incomplete is False


def test_invalid_utf8_is_reported_as_incomplete_read(tmp_path: Path) -> None:
    path = tmp_path / "invalid-utf8.log"
    path.write_bytes(b"\xff")

    with pytest.raises(LogInputError, match="failed before completion") as exception:
        list(iter_log_records(path, InputStats()))

    assert exception.value.incomplete is True


def test_file_records_are_yielded_incrementally(monkeypatch) -> None:
    sample_lines = (SAMPLES / "valid-clf.log").read_text(encoding="utf-8").splitlines()

    class TrackingStream:
        def __init__(self) -> None:
            self.read_count = 0

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback) -> None:
            return None

        def __iter__(self):
            for line in sample_lines:
                self.read_count += 1
                yield line + "\n"

    stream = TrackingStream()
    monkeypatch.setattr(Path, "open", lambda self, *args, **kwargs: stream)
    records = iter_log_records("ignored.log", InputStats())

    assert stream.read_count == 0
    next(records)
    assert stream.read_count == 1


def test_mid_read_failure_is_reported_as_incomplete(monkeypatch) -> None:
    sample_line = (SAMPLES / "valid-clf.log").read_text(encoding="utf-8").splitlines()[0]

    class FailingStream:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback) -> None:
            return None

        def __iter__(self):
            yield sample_line + "\n"
            raise OSError("simulated device failure")

    monkeypatch.setattr(Path, "open", lambda self, *args, **kwargs: FailingStream())
    stats = InputStats()
    records = iter_log_records("failing.log", stats)

    assert next(records).request_target == "/alpha?x=1"
    with pytest.raises(LogInputError, match="failed before completion") as exception:
        next(records)
    assert exception.value.incomplete is True