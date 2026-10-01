# LogLens

LogLens is a Python command-line application for analysing local HTTP server access logs. It is intended to make large text logs easier to inspect through structured parsing, filtering and summaries.

This repository currently contains the installable package foundation and the shared access-log record contract. Log parsing and CLI commands are not part of this issue and will be added in later work.

## Record contract

Import the immutable record from the package root with `from loglens import AccessLogRecord`. Its fields are:

| Field | Type | Meaning |
| --- | --- | --- |
| `client_ip` | `str` | Canonical IP text: standard dotted-decimal for IPv4 or compressed lowercase form for IPv6. |
| `timestamp` | `datetime` | A timezone-aware timestamp. Its original UTC offset is preserved. |
| `method` | `str` | The uppercase HTTP method. |
| `request_target` | `str` | The origin-form target preserved in full, including any query string. |
| `protocol` | `str` | The HTTP protocol token, such as `HTTP/1.1`. |
| `status` | `int` | The HTTP response status code. |
| `response_size` | `int | None` | Response bytes; `None` represents `-` (not recorded), while `0` is an explicitly recorded zero-byte response. |

`AccessLogRecord` is a frozen dataclass. It stores these values without validating or normalizing them; input parsing, canonical IP conversion, and timestamp-awareness checks belong to the parser. The model does not access files, format terminal output, or perform analysis.

## Supported CLF parsing

`parse_access_log_line(line)` parses one record and returns an `AccessLogRecord`. Import it with `from loglens import parse_access_log_line`; malformed or unsupported records raise `AccessLogParseError`, a `ValueError` subclass. A line may end with one LF or CRLF. The function does not read files or print output; passing a non-string is a programming error and raises `TypeError`.

The accepted record shape is:

```text
client-ip ident authuser [DD/Mon/YYYY:HH:MM:SS +HHMM] "METHOD /origin-target HTTP/major.minor" STATUS SIZE
```

- `client-ip` must be a valid IPv4 or IPv6 address. The record stores its canonical compressed textual form.
- `ident` and `authuser` are non-whitespace CLF fields and are not retained.
- The timestamp uses an English, case-sensitive month abbreviation (`Jan` through `Dec`), a valid calendar date/time, and a signed four-digit numeric UTC offset. Parsing is locale-independent and preserves the offset.
- `METHOD` must be an uppercase HTTP token. The origin-form request target must begin with `/`; it is preserved in full, including its query string. The protocol must match `HTTP/major.minor` with decimal components.
- After removing one permitted LF or CRLF line ending, ASCII control characters U+0000–U+001F and U+007F are rejected anywhere in the record, including the ignored ident and authuser fields. Ordinary spaces are permitted between fields.
- `STATUS` must be a three-digit code from 100 through 599. `SIZE` must be a nonnegative decimal integer or `-`; `-` becomes `None`, while `0` remains zero.
- Additional trailing fields, including Combined-format referer and user-agent fields, are rejected. Other log formats are not detected or supported.

## Sample data

Synthetic CLF, mixed-input, all-invalid, and empty fixtures are in [`samples/`](samples/). The mixed sample includes blank lines. Manually calculated line dispositions, status totals, ranking counts, and filter matches are documented in the [sample manifest](samples/README.md).

## Portfolio standards

The portfolio engineering standards used for this project are kept in [`docs/standards/`](docs/standards/). This is a project-local snapshot; it is not automatically synchronized with the shared standards repository.

## Requirements

- Python 3.12 or newer

## Development setup

From the repository root, run these commands in PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

The commands use the virtual environment's interpreter directly, so activating it is not required. The editable install makes changes under `src/` importable without reinstalling the package. The project uses setuptools as its standard, lightweight PEP 517 build backend. Pytest provides the initial package smoke test; Ruff supplies a focused Python linter for development checks. These tools are development-only and there are no runtime dependencies.

## Checks

Run the tests with:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Run the linter with:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
```

## Licence

Sam's licence decision is pending. No licence has been selected or granted yet.