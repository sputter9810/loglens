"""Reusable analysis operations over parsed access-log records."""

from collections import Counter
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass

from loglens.models import AccessLogRecord

_STATUS_CATEGORIES = ("1xx", "2xx", "3xx", "4xx", "5xx")


@dataclass(frozen=True)
class RequestSummary:
    """Request totals, exact status counts, and all five status categories."""

    total_requests: int
    status_counts: dict[int, int]
    category_counts: dict[str, int]


def summarize_requests(records: Iterable[AccessLogRecord]) -> RequestSummary:
    """Summarize parsed records in one pass without reading files or printing."""
    status_counts: Counter[int] = Counter()
    category_counts = dict.fromkeys(_STATUS_CATEGORIES, 0)
    total_requests = 0

    for record in records:
        total_requests += 1
        status_counts[record.status] += 1
        category = f"{record.status // 100}xx"
        if category in category_counts:
            category_counts[category] += 1

    return RequestSummary(
        total_requests=total_requests,
        status_counts=dict(status_counts),
        category_counts=category_counts,
    )


def filter_by_status(
    records: Iterable[AccessLogRecord], status: int
) -> Iterator[AccessLogRecord]:
    """Yield records with an exact status, preserving source order.

    Preconditions: ``status`` is an integer from 100 through 599, and records
    contains valid parsed access-log records. Validation belongs to the caller.
    """
    for record in records:
        if record.status == status:
            yield record


def filter_by_method(
    records: Iterable[AccessLogRecord], method: str
) -> Iterator[AccessLogRecord]:
    """Yield records with an exact uppercase method, preserving source order.

    Preconditions: ``method`` is an uppercase HTTP token, and records contains
    valid parsed access-log records with normalized methods. Validation and
    normalization belong to the caller.
    """
    for record in records:
        if record.method == method:
            yield record


def _rank_values(
    records: Iterable[AccessLogRecord],
    value_for: Callable[[AccessLogRecord], str],
    limit: int,
) -> list[tuple[str, int]]:
    if limit <= 0:
        raise ValueError("limit must be a positive integer")

    counts: Counter[str] = Counter()
    for record in records:
        counts[value_for(record)] += 1

    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]


def rank_request_targets(
    records: Iterable[AccessLogRecord], limit: int = 10
) -> list[tuple[str, int]]:
    """Rank complete request targets by count, then target ascending.

    ``limit`` must be a positive integer. Storage grows with distinct targets,
    not with the number of input records.
    """
    return _rank_values(records, lambda record: record.request_target, limit)


def rank_client_ips(
    records: Iterable[AccessLogRecord], limit: int = 10
) -> list[tuple[str, int]]:
    """Rank canonical client IP strings by count, then address ascending.

    Records must contain canonical IP strings and ``limit`` must be a positive
    integer. Storage grows with distinct addresses, not input record count.
    """
    return _rank_values(records, lambda record: record.client_ip, limit)
