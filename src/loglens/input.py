"""Incremental local-file input for supported access-log records."""

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from loglens.models import AccessLogRecord
from loglens.parser import AccessLogParseError, parse_access_log_line


@dataclass
class InputStats:
    """Counts accumulated while an input iterator is consumed."""

    valid_records: int = 0
    malformed_records: int = 0
    blank_lines: int = 0
    nonblank_lines: int = 0


class LogInputError(Exception):
    """Raised for expected file input failures."""

    def __init__(self, message: str, *, incomplete: bool = False) -> None:
        super().__init__(message)
        self.incomplete = incomplete


class AllRecordsInvalidError(LogInputError):
    """Raised when nonblank input contains no valid access-log records."""


def iter_log_records(path: str | Path, stats: InputStats) -> Iterator[AccessLogRecord]:
    """Read UTF-8 lines incrementally, counting blanks and skipping malformed records.

    Empty and blank-only files yield no records successfully. Nonblank files
    containing no valid records raise ``AllRecordsInvalidError`` after scanning.
    """
    log_path = Path(path)
    try:
        source = log_path.open("r", encoding="utf-8")
    except OSError as error:
        raise LogInputError(f"cannot open '{log_path}': {error}") from error

    try:
        with source:
            for line in source:
                if not line.strip():
                    stats.blank_lines += 1
                    continue

                stats.nonblank_lines += 1
                try:
                    record = parse_access_log_line(line)
                except AccessLogParseError:
                    stats.malformed_records += 1
                    continue

                stats.valid_records += 1
                yield record
    except (OSError, UnicodeError) as error:
        raise LogInputError(
            f"reading '{log_path}' failed before completion: {error}",
            incomplete=True,
        ) from error

    if stats.nonblank_lines > 0 and stats.valid_records == 0:
        raise AllRecordsInvalidError(
            f"'{log_path}' contains nonblank lines but no valid access-log records"
        )
