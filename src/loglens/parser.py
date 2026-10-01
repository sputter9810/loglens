"""Parsing for the supported Common Log Format subset."""

import ipaddress
import re
from datetime import datetime, timedelta, timezone

from loglens.models import AccessLogRecord

_CLF_LINE_PATTERN = re.compile(
    r'(?P<client_ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] '
    r'"(?P<request>[^"]*)" (?P<status>[0-9]{3}) (?P<response_size>-|[0-9]+)'
)
_REQUEST_PATTERN = re.compile(
    r"(?P<method>[A-Z0-9!#$%&'*+.^_`|~-]+) "
    r"(?P<request_target>\S+) (?P<protocol>HTTP/[0-9]+\.[0-9]+)"
)
_TIMESTAMP_PATTERN = re.compile(
    r"(?P<day>[0-9]{2})/(?P<month>[A-Za-z]{3})/(?P<year>[0-9]{4}):"
    r"(?P<hour>[0-9]{2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2}) "
    r"(?P<offset_sign>[+-])(?P<offset_hour>[0-9]{2})(?P<offset_minute>[0-9]{2})"
)
_MONTHS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


class AccessLogParseError(ValueError):
    """Raised when a line is not a valid entry in the supported CLF subset."""


def _parse_timestamp(value: str) -> datetime:
    match = _TIMESTAMP_PATTERN.fullmatch(value)
    if match is None:
        raise AccessLogParseError("timestamp does not match the supported CLF form")

    month = _MONTHS.get(match.group("month"))
    if month is None:
        raise AccessLogParseError("timestamp month must be an English CLF abbreviation")

    offset_hour = int(match.group("offset_hour"))
    offset_minute = int(match.group("offset_minute"))
    if offset_hour > 23 or offset_minute > 59:
        raise AccessLogParseError("timestamp UTC offset is out of range")

    offset = timedelta(hours=offset_hour, minutes=offset_minute)
    if match.group("offset_sign") == "-":
        offset = -offset

    try:
        return datetime(
            year=int(match.group("year")),
            month=month,
            day=int(match.group("day")),
            hour=int(match.group("hour")),
            minute=int(match.group("minute")),
            second=int(match.group("second")),
            tzinfo=timezone(offset),
        )
    except ValueError as error:
        raise AccessLogParseError(
            "timestamp is not a valid calendar date and time"
        ) from error


def parse_access_log_line(line: str) -> AccessLogRecord:
    """Parse one CLF record line, optionally ending in LF or CRLF."""
    if not isinstance(line, str):
        raise TypeError("line must be a string")

    if line.endswith("\r\n"):
        line = line[:-2]
    elif line.endswith("\n"):
        line = line[:-1]

    if any(ord(character) < 0x20 or ord(character) == 0x7F for character in line):
        raise AccessLogParseError("record contains an ASCII control character")

    fields = _CLF_LINE_PATTERN.fullmatch(line)
    if fields is None:
        raise AccessLogParseError("line is not a supported CLF record")

    request = _REQUEST_PATTERN.fullmatch(fields.group("request"))
    if request is None or not request.group("request_target").startswith("/"):
        raise AccessLogParseError(
            "request line is not a supported origin-form HTTP request"
        )

    try:
        client_ip = ipaddress.ip_address(fields.group("client_ip")).compressed
    except ValueError as error:
        raise AccessLogParseError(
            "client address must be a valid IPv4 or IPv6 address"
        ) from error

    timestamp = _parse_timestamp(fields.group("timestamp"))
    status = int(fields.group("status"))
    if not 100 <= status <= 599:
        raise AccessLogParseError("status must be between 100 and 599")

    size_text = fields.group("response_size")
    try:
        response_size = None if size_text == "-" else int(size_text)
    except ValueError as error:
        raise AccessLogParseError(
            "response size must be a nonnegative integer or '-'"
        ) from error

    return AccessLogRecord(
        client_ip=client_ip,
        timestamp=timestamp,
        method=request.group("method"),
        request_target=request.group("request_target"),
        protocol=request.group("protocol"),
        status=status,
        response_size=response_size,
    )
