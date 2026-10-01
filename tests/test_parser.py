from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from loglens import AccessLogParseError, AccessLogRecord, parse_access_log_line

SAMPLE_PATH = Path(__file__).parents[1] / "samples" / "valid-clf.log"
SAMPLE_LINES = SAMPLE_PATH.read_text(encoding="utf-8").splitlines()


@pytest.mark.parametrize(
    ("line_number", "expected"),
    [
        (
            0,
            AccessLogRecord(
                client_ip="192.0.2.10",
                timestamp=datetime(2025, 10, 1, 9, 0, tzinfo=UTC),
                method="GET",
                request_target="/alpha?x=1",
                protocol="HTTP/1.1",
                status=200,
                response_size=120,
            ),
        ),
        (
            1,
            AccessLogRecord(
                client_ip="198.51.100.20",
                timestamp=datetime(2025, 10, 1, 9, 1, tzinfo=UTC),
                method="POST",
                request_target="/beta",
                protocol="HTTP/1.1",
                status=201,
                response_size=0,
            ),
        ),
        (
            2,
            AccessLogRecord(
                client_ip="2001:db8::1",
                timestamp=datetime(2025, 10, 1, 9, 2, tzinfo=UTC),
                method="BREW",
                request_target="/alpha?x=1",
                protocol="HTTP/1.1",
                status=404,
                response_size=None,
            ),
        ),
        (
            4,
            AccessLogRecord(
                client_ip="203.0.113.9",
                timestamp=datetime(2025, 10, 1, 9, 4, tzinfo=UTC),
                method="M-SEARCH",
                request_target="/beta",
                protocol="HTTP/1.1",
                status=503,
                response_size=72,
            ),
        ),
    ],
)
def test_parses_known_sample_lines(line_number: int, expected: AccessLogRecord) -> None:
    assert parse_access_log_line(SAMPLE_LINES[line_number]) == expected


def test_preserves_non_utc_offset_and_canonicalizes_ipv6() -> None:
    line = (
        '2001:0DB8:0000:0000:0000:0000:0000:000A - - '
        '[01/Oct/2025:09:30:00 -0730] '
        '"M-SEARCH /search?q=a%2Fb HTTP/2.0" 204 6'
    )

    record = parse_access_log_line(line)

    assert record == AccessLogRecord(
        client_ip="2001:db8::a",
        timestamp=datetime(
            2025,
            10,
            1,
            9,
            30,
            tzinfo=timezone(-timedelta(hours=7, minutes=30)),
        ),
        method="M-SEARCH",
        request_target="/search?q=a%2Fb",
        protocol="HTTP/2.0",
        status=204,
        response_size=6,
    )


@pytest.mark.parametrize("ending", ["\n", "\r\n"])
def test_accepts_one_line_ending(ending: str) -> None:
    assert parse_access_log_line(SAMPLE_LINES[0] + ending).request_target == "/alpha?x=1"


@pytest.mark.parametrize("control", ["\x00", "\x1b", "\x7f"])
def test_rejects_control_characters_in_request_target(control: str) -> None:
    line = (
        '192.0.2.1 - - [01/Oct/2025:12:00:00 +0000] '
        f'"GET /before{control}after?q=1 HTTP/1.1" 200 1'
    )

    with pytest.raises(AccessLogParseError):
        parse_access_log_line(line)


def test_rejects_control_character_in_ignored_clf_field() -> None:
    line = (
        '192.0.2.1 - user\x1bname [01/Oct/2025:12:00:00 +0000] '
        '"GET / HTTP/1.1" 200 1'
    )

    with pytest.raises(AccessLogParseError):
        parse_access_log_line(line)


@pytest.mark.parametrize(
    "line",
    [
        "",
        "not-an-ip - - [01/Oct/2025:12:00:00 +0000] \"GET / HTTP/1.1\" 200 1",
        "999.0.0.1 - - [01/Oct/2025:12:00:00 +0000] \"GET / HTTP/1.1\" 200 1",
        "2001:db8::zz - - [01/Oct/2025:12:00:00 +0000] \"GET / HTTP/1.1\" 200 1",
        "192.0.2.1 - - [01/Otc/2025:12:00:00 +0000] \"GET / HTTP/1.1\" 200 1",
        "192.0.2.1 - - [31/Feb/2025:12:00:00 +0000] \"GET / HTTP/1.1\" 200 1",
        "192.0.2.1 - - [01/Oct/2025:12:00:00 +2460] \"GET / HTTP/1.1\" 200 1",
        "192.0.2.1 - - [01/Oct/2025:12:00:00 +0000] \"get / HTTP/1.1\" 200 1",
        "192.0.2.1 - - [01/Oct/2025:12:00:00 +0000] \"GET http://example.invalid/ HTTP/1.1\" 200 1",
        "192.0.2.1 - - [01/Oct/2025:12:00:00 +0000] \"GET / HTTP/one.one\" 200 1",
        "192.0.2.1 - - [01/Oct/2025:12:00:00 +0000] \"GET / HTTP/1.1\" 099 1",
        "192.0.2.1 - - [01/Oct/2025:12:00:00 +0000] \"GET / HTTP/1.1\" 600 1",
        "192.0.2.1 - - [01/Oct/2025:12:00:00 +0000] \"GET / HTTP/1.1\" 200 -1",
        "192.0.2.1 - - [01/Oct/2025:12:00:00 +0000] \"GET / HTTP/1.1\" 200 +1",
        "192.0.2.1 - - [01/Oct/2025:12:00:00 +0000] \"GET / HTTP/1.1\" 200 1 \"referer\" \"agent\"",
    ],
)
def test_malformed_lines_raise_parse_error_without_output(line: str, capsys) -> None:
    with pytest.raises(AccessLogParseError):
        parse_access_log_line(line)

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_non_string_input_is_a_programming_error() -> None:
    with pytest.raises(TypeError, match="line must be a string"):
        parse_access_log_line(None)


@pytest.mark.parametrize(
    "line",
    [
        '192.0.2.1 - - [01-Oct-2025:12:00:00 +0000] "GET / HTTP/1.1" 200 1',
        '192.0.2.1 - - [01/Oct/2025:12:00:00 UTC] "GET / HTTP/1.1" 200 1',
        'web-01 192.0.2.1 - - [01/Oct/2025:12:00:00 +0000] "GET / HTTP/1.1" 200 1',
    ],
)
def test_rejects_near_matching_non_clf_formats(line: str) -> None:
    with pytest.raises(AccessLogParseError):
        parse_access_log_line(line)