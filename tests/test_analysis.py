from datetime import UTC, datetime

from loglens import AccessLogRecord, RequestSummary, summarize_requests


def make_record(status: int) -> AccessLogRecord:
    return AccessLogRecord(
        client_ip="192.0.2.1",
        timestamp=datetime(2025, 10, 1, tzinfo=UTC),
        method="GET",
        request_target="/resource",
        protocol="HTTP/1.1",
        status=status,
        response_size=1,
    )


class OneShotRecords:
    def __init__(self, records: list[AccessLogRecord]) -> None:
        self.records = records
        self.iterations = 0

    def __iter__(self):
        self.iterations += 1
        if self.iterations > 1:
            raise AssertionError("records must be traversed once")
        yield from self.records


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