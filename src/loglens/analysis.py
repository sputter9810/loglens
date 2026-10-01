"""Reusable analysis operations over parsed access-log records."""

from collections import Counter
from collections.abc import Iterable, Iterator
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