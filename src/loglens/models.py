"""Domain models shared by LogLens components."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AccessLogRecord:
    """One structured access-log record, without parsing or validation logic."""

    client_ip: str
    timestamp: datetime
    method: str
    request_target: str
    protocol: str
    status: int
    response_size: int | None