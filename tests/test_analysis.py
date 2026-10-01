from datetime import UTC, datetime

import pytest

from loglens import (
    AccessLogRecord,
    RequestSummary,
    filter_by_method,
    filter_by_status,
    summarize_requests,
)


def make_record(status: int, method: str = "GET") -> AccessLogRecord:
    return AccessLogRecord(
        client_ip="192.0.2.1",
        timestamp=datetime(2025, 10, 1, tzinfo=UTC),
        method=method,
        request_target="/resource",
        protocol="HTTP/1.1",
        status=status,
        response_size=1,
    )


class OneShotRecords:
    def __init__(self, records: list[AccessLogRecord]) -> None:
        self.records = records
        self.iterations = 0
        self.consumed = 0

    def __iter__(self):
        self.iterations += 1
        if self.iterations > 1:
            raise AssertionError("records must be traversed once")
        for record in self.records:
            self.consumed += 1
            yield record


def test_empty_records_have_zero_totals_and_categories() -> None:
    summary = summarize_requests(iter(()))

    assert summary == RequestSummary(
        total_requests=0,
        status_counts={},
        category_counts={"1xx": 0, "2xx": 0, "3xx": 0, "4xx": 0, "5xx": 0},
    )


def test_mixed_statuses_have_exact_counts_and_categories() -> None:
    records = [make_record(status) for status in (200, 200, 404, 503, 100, 302, 302)]

    summary = summarize_requests(records)

    assert summary.total_requests == 7
    assert summary.status_counts == {200: 2, 404: 1, 503: 1, 100: 1, 302: 2}
    assert summary.category_counts == {
        "1xx": 1,
        "2xx": 2,
        "3xx": 2,
        "4xx": 1,
        "5xx": 1,
    }


def test_one_shot_iterable_is_traversed_once() -> None:
    records = OneShotRecords([make_record(201), make_record(500)])

    summary = summarize_requests(records)

    assert summary.total_requests == 2
    assert summary.status_counts == {201: 1, 500: 1}
    assert records.iterations == 1


def test_filter_by_status_returns_exact_matches_in_input_order() -> None:
    records = [make_record(status) for status in (200, 404, 200, 302, 404)]

    assert list(filter_by_status(records, 404)) == [records[1], records[4]]


@pytest.mark.parametrize("status", [100, 599])
def test_filter_by_status_accepts_valid_boundary_codes(status: int) -> None:
    records = [make_record(code) for code in (100, 101, 598, 599)]

    assert list(filter_by_status(records, status)) == [
        record for record in records if record.status == status
    ]


def test_filter_by_status_returns_empty_for_no_matches_or_empty_input() -> None:
    assert list(filter_by_status([make_record(200)], 404)) == []
    assert list(filter_by_status(iter(()), 200)) == []


def test_filter_by_status_consumes_one_shot_iterable_incrementally() -> None:
    source_records = [
        make_record(404),
        make_record(200),
        make_record(302),
        make_record(200),
    ]
    records = OneShotRecords(source_records)
    matches = filter_by_status(records, 200)

    assert records.iterations == 0
    assert records.consumed == 0
    assert next(matches) == source_records[1]
    assert records.iterations == 1
    assert records.consumed == 2
    assert list(matches) == [source_records[3]]
    assert records.iterations == 1
    assert records.consumed == 4


def test_filter_by_method_matches_common_methods_in_input_order() -> None:
    records = [
        make_record(200, method)
        for method in ("GET", "POST", "HEAD", "GET", "DELETE")
    ]

    assert list(filter_by_method(records, "GET")) == [records[0], records[3]]
    assert list(filter_by_method(records, "POST")) == [records[1]]
    assert list(filter_by_method(records, "HEAD")) == [records[2]]


def test_filter_by_method_supports_extensions_without_a_whitelist() -> None:
    records = [make_record(200, "BREW"), make_record(200, "M-SEARCH")]

    assert list(filter_by_method(records, "BREW")) == [records[0]]
    assert list(filter_by_method(records, "M-SEARCH")) == [records[1]]
    assert list(filter_by_method(records, "PROPFIND")) == []


def test_filter_by_method_returns_empty_for_empty_input() -> None:
    assert list(filter_by_method(iter(()), "GET")) == []


def test_filter_by_method_consumes_one_shot_iterable_incrementally() -> None:
    source_records = [
        make_record(200, "POST"),
        make_record(200, "GET"),
        make_record(200, "HEAD"),
        make_record(200, "GET"),
    ]
    records = OneShotRecords(source_records)
    matches = filter_by_method(records, "GET")

    assert records.iterations == 0
    assert records.consumed == 0
    assert next(matches) == source_records[1]
    assert records.iterations == 1
    assert records.consumed == 2
    assert list(matches) == [source_records[3]]
    assert records.iterations == 1
    assert records.consumed == 4