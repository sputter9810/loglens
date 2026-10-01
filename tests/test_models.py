from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from loglens import AccessLogRecord


def make_record(response_size: int | None = None) -> AccessLogRecord:
    return AccessLogRecord(
        client_ip="2001:db8::1",
        timestamp=datetime(
            2026,
            10,
            1,
            12,
            30,
            tzinfo=timezone(timedelta(hours=-4)),
        ),
        method="GET",
        request_target="/reports?format=csv",
        protocol="HTTP/1.1",
        status=200,
        response_size=response_size,
    )


def test_record_preserves_fields_and_timestamp_offset() -> None:
    record = make_record()

    assert record.client_ip == "2001:db8::1"
    assert record.timestamp.utcoffset() == timedelta(hours=-4)
    assert record.method == "GET"
    assert record.request_target == "/reports?format=csv"
    assert record.protocol == "HTTP/1.1"
    assert record.status == 200

    with pytest.raises(FrozenInstanceError):
        record.status = 201


@pytest.mark.parametrize("response_size", [None, 0])
def test_record_preserves_optional_response_size(response_size: int | None) -> None:
    record = make_record(response_size)

    assert record.response_size == response_size
