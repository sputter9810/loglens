# LogLens

LogLens is a Python command-line application for analysing local HTTP server access logs. It is intended to make large text logs easier to inspect through structured parsing, filtering and summaries.

This repository contains the installable package foundation, shared access-log record contract, CLF line parser, reusable request-summary analysis, library-level status and method filters, request-target and IP ranking, and command-line argument interface. CLI data integration is not implemented yet.

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

## Request summary analysis

`summarize_requests(records)` accepts an iterable of parsed `AccessLogRecord` values and returns a `RequestSummary` with `total_requests`, exact `status_counts`, and `category_counts` for every category from `1xx` through `5xx`, including zero counts. It consumes the iterable once and performs no file access, printing, or malformed-input diagnostics; input handling is the caller's responsibility.

`filter_by_status(records, status)` lazily yields only records whose status exactly matches `status`, preserving input order and consuming the iterable once. Its preconditions are that `status` is an integer from 100 through 599 and each item is a valid parsed `AccessLogRecord`; callers are responsible for satisfying these preconditions. It does not read files, print, or add status categories or ranges.

`filter_by_method(records, method)` lazily yields only records whose normalized method exactly matches `method`, preserving input order and consuming the iterable once. Its preconditions are an uppercase HTTP token and valid parsed records whose methods are already normalized to uppercase. Callers are responsible for validation and normalization. There is no method whitelist, file access, or terminal output.

`rank_request_targets(records, limit=10)` and `rank_client_ips(records, limit=10)` return `(value, count)` pairs sorted by count descending and value ascending for ties. Targets include their preserved query strings; IPs must already be canonical. `limit` must be a positive integer. Each function consumes its iterable once and retains counts only for distinct keys; neither reads files nor formats or prints results.

## Command-line interface

Editable installation registers the `loglens` command. Its approved command forms are:

```text
loglens summary FILE
loglens filter FILE [--status CODE] [--method METHOD]
loglens top-paths FILE [--limit N]
loglens top-ips FILE [--limit N]
```

`--limit` defaults to 10, method arguments are normalized to uppercase, and a filter requires at least one selector. When both filter selectors are supplied, records must match both. The root and all subcommands provide argparse help. For example:

```powershell
loglens summary samples/valid-clf.log
loglens filter samples/mixed-input.log --status 404 --method post
loglens top-paths samples/valid-clf.log --limit 3
loglens top-ips samples/valid-clf.log
```

Summary output includes total requests, exact status counts, and every status category. Filter output preserves input order and JSON-quotes request targets so control characters cannot alter terminal layout. Rankings show count and escaped key, ordered by descending count then ascending key.

Files are read incrementally as UTF-8. Blank lines are ignored and counted; malformed records are skipped and counted. If malformed records are skipped, one concise diagnostic on standard error reports valid-record, malformed-record, and blank-line totals, including zeros. Successful input without malformed records emits no diagnostic, even when it contains only blank lines. Empty and blank-only files succeed with zero/no-match output. Nonblank all-invalid files fail with status 1. File/read/decoding failures also return status 1; a mid-read failure explicitly warns that preceding streamed output may be incomplete. Invalid argument shapes return status 2. Analysis functions remain independent of file input and presentation.

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