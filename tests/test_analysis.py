from datetime import UTC, datetime
from pathlib import Path

import pytest

from loglens import (
    AccessLogRecord,
    RequestSummary,
    filter_by_method,
    filter_by_status,
    parse_access_log_line,
    rank_client_ips,
    rank_request_targets,
    summarize_requests,
)

SAMPLE_PATH = Path(__file__).parents[1] / "samples" / "valid-clf.log"


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


def sample_records():
    return (
        parse_access_log_line(line)
        for line in SAMPLE_PATH.read_text(encoding="utf-8").splitlines()
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


def test_two_xx_only_summary_keeps_other_categories_zero() -> None:
    records = [make_record(200), make_record(201), make_record(204)]

    summary = summarize_requests(records)

    assert summary.total_requests == 3
    assert summary.status_counts == {200: 1, 201: 1, 204: 1}
    assert summary.category_counts == {
        "1xx": 0,
        "2xx": 3,
        "3xx": 0,
        "4xx": 0,
        "5xx": 0,
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


@pytest.mark.parametrize(("status", "expected_index"), [(100, 0), (599, 3)])
def test_filter_by_status_accepts_valid_boundary_codes(
    status: int, expected_index: int
) -> None:
    records = [make_record(code) for code in (100, 101, 598, 599)]

    assert list(filter_by_status(records, status)) == [records[expected_index]]


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


def test_request_target_ranking_matches_sample_counts_and_ties() -> None:
    assert rank_request_targets(sample_records(), limit=20) == [
        ("/alpha?x=1", 2),
        ("/beta", 2),
        ("/delta", 1),
        ("/epsilon", 1),
        ("/gamma", 1),
        ("/zeta", 1),
    ]


def test_client_ip_ranking_matches_sample_counts_and_ties() -> None:
    assert rank_client_ips(sample_records()) == [
        ("192.0.2.10", 2),
        ("198.51.100.20", 2),
        ("2001:db8::1", 2),
        ("203.0.113.9", 2),
    ]


def test_rankers_apply_top_n_limits_and_return_empty_results() -> None:
    assert rank_request_targets(sample_records(), limit=3) == [
        ("/alpha?x=1", 2),
        ("/beta", 2),
        ("/delta", 1),
    ]
    assert rank_client_ips(iter(())) == []
    assert rank_request_targets(iter(())) == []


@pytest.mark.parametrize("ranker", [rank_request_targets, rank_client_ips])
@pytest.mark.parametrize("limit", [0, -1])
def test_rankers_require_positive_limits(ranker, limit: int) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        ranker(iter(()), limit=limit)


@pytest.mark.parametrize(
    ("ranker", "expected"),
    [
        (rank_request_targets, [("/resource", 3)]),
        (rank_client_ips, [("192.0.2.1", 3)]),
    ],
)
def test_rankers_consume_one_shot_iterables_once(ranker, expected) -> None:
    records = OneShotRecords([make_record(200), make_record(404), make_record(200)])

    result = ranker(records)

    assert result == expected
    assert records.iterations == 1
    assert records.consumed == 3