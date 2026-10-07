# LogLens

LogLens is a Python command-line application for analysing local HTTP server access logs. It is intended to make large text logs easier to inspect through structured parsing, filtering and summaries.

The installed CLI reads local files incrementally and provides summaries, status/method filtering, and request-target/IP rankings. It was built as a portfolio project to demonstrate Python packaging, parsing, iterator-based analysis, validation, testing, and CI. Runtime code uses only the Python standard library; development uses setuptools, build, pytest, and Ruff.

## Install and run

Requires Python 3.12 or newer. Obtain a checkout of this repository and open PowerShell in its root directory:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\loglens.exe summary samples/valid-clf.log
```

For development, use the editable installation with development tools described in [Development setup](#development-setup). All examples below run from the repository root and use the installed launcher directly; activation is unnecessary. On Linux/macOS, create the environment with `python3.12 -m venv .venv` and substitute `.venv/bin/python` and `.venv/bin/loglens` for the Windows executable paths. This project is installed from source or a locally built wheel; it is not published to PyPI.

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
- After removing one permitted LF or CRLF line ending, ASCII control characters U+0000–U+001F and U+007F are rejected anywhere in the record, including the ignored ident and authuser fields. Fields require exactly one ASCII space between them, as shown above; leading/trailing whitespace and tabs are rejected.
- `STATUS` must be a three-digit code from 100 through 599. `SIZE` must be a nonnegative decimal integer or `-`; `-` becomes `None`, while `0` remains zero.
- Additional trailing fields, including Combined-format referer and user-agent fields, are rejected. Other log formats are not detected or supported.

The parser recognizes only this field order and shape. It does not auto-detect or convert Combined, NCSA-style date, virtual-host-prefixed, or custom log formats. Near-matching timestamps, timezone names in place of numeric offsets, absolute-form request targets, and extra fields are rejected as malformed records.

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

`--limit` must be positive and defaults to 10. A status selector must be an integer from 100 through 599. Method arguments must be HTTP tokens and are normalized to uppercase; extension methods are supported. A filter requires at least one selector. When both selectors are supplied, records must match both. Use `loglens --help` or `loglens COMMAND --help` for root or subcommand help.

### Summary example

```powershell
.\.venv\Scripts\loglens.exe summary samples/valid-clf.log
```

Stdout (exit 0):

```text
Total requests: 8
Exact status counts:
  100: 1
  200: 2
  201: 1
  302: 1
  404: 2
  503: 1
Status categories:
  1xx: 1
  2xx: 3
  3xx: 1
  4xx: 2
  5xx: 1
```

Stderr is empty.

### Filter example

```powershell
.\.venv\Scripts\loglens.exe filter samples/mixed-input.log --status 404 --method post
```

Stdout (exit 0):

```text
2001:db8::8 2025-10-01T10:02:00+00:00 POST "/shared?mode=test" HTTP/1.1 404 -
```

Stderr:

```text
Input: 4 valid records; 4 malformed records skipped; 2 blank lines ignored.
```

### Top paths example

```powershell
.\.venv\Scripts\loglens.exe top-paths samples/valid-clf.log --limit 3
```

Stdout (exit 0):

```text
2	"/alpha?x=1"
2	"/beta"
1	"/delta"
```

Stderr is empty.

### Top IPs example

```powershell
.\.venv\Scripts\loglens.exe top-ips samples/valid-clf.log
```

Stdout (exit 0):

```text
2	"192.0.2.10"
2	"198.51.100.20"
2	"2001:db8::1"
2	"203.0.113.9"
```

Stderr is empty.

Ranking columns use a literal tab. These examples are checked against the named tracked fixtures by `tests/test_readme.py`, including stderr and exit status.

Summary output includes total requests, exact status counts, and every status category. Filter output preserves input order and JSON-quotes request targets so control characters cannot alter terminal layout. Rankings show count and escaped key, ordered by descending count then ascending key.

Files are read incrementally as UTF-8. Blank lines are ignored and counted; malformed records are skipped and counted. If malformed records are skipped, one concise diagnostic on standard error reports valid-record, malformed-record, and blank-line totals, including zeros. Successful input without malformed records emits no diagnostic, even when it contains only blank lines. Empty and blank-only files succeed with zero/no-match output. Nonblank all-invalid files fail with status 1. Non-integer or out-of-range statuses, invalid method tokens, missing filter selectors, and nonpositive limits are argument errors (status 2); lowercase valid method tokens are normalized to uppercase. Missing paths, directories, permission/read failures, and invalid UTF-8 return status 1 without a traceback. A mid-read failure explicitly warns that preceding streamed output may be incomplete. Analysis functions remain independent of file input and presentation.

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Completed operation, including empty/blank-only input or no filter matches; help also succeeds. |
| `1` | Expected file/open/read/UTF-8 decoding failure, or nonblank input with no valid records. |
| `2` | Invalid command or arguments. |

Results go to stdout; diagnostics go to stderr. LF, CRLF, and a final unterminated line are accepted by the input layer. Filters print `No records matched.` when successful with no matches; empty rankings print `No requests to rank.`. A mid-read failure reports that preceding streamed output may be incomplete. Summary and rankings consume input before printing results; a filter can already have printed matches when reading fails.

## Architecture boundaries

| Module | Responsibility |
| --- | --- |
| `models.py` | Immutable typed record, without input validation or side effects. |
| `parser.py` | Parse one supported CLF line, validate fields, canonicalise IPs, preserve target and timestamp offset; raise `AccessLogParseError` on invalid input. |
| `input.py` | Open and iterate local UTF-8 files; count blank/valid/malformed lines and report expected input failures through exceptions. |
| `analysis.py` | Consume record iterables for summaries, lazy filters and rankings; no file access or printing. |
| `cli.py` | Validate arguments, compose input/analysis, format output and translate expected failures into exit codes. |

There is no whole-file list. Summary state is bounded by the supported statuses, and filtering is lazy. Rankings retain all distinct-key counts and sort them before taking the limit: `--limit` bounds output, not memory. Very long individual lines can also increase input/parser memory. The [scaling review](#scaling-review) records measured Python allocation peaks and their limits.

## Exclusions and future ideas

V1 supports local files and only the CLF subset documented here. It provides no Combined/custom-format detection, GUI, web frontend/API, database, accounts, remote administration, live monitoring, cloud deployment, distributed processing, machine learning, alerts, or machine-readable output mode.

Additional formats, structured output, or bounded-memory ranking could be considered in separately approved future work. They are ideas, not supported capabilities or commitments. See [PROJECT.md](PROJECT.md) for scope and [the engineering standards](docs/standards/README.md) for review expectations.

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

The commands use the virtual environment's interpreter directly, so activating it is not required. The editable install makes changes under `src/` importable without reinstalling the package. The project uses setuptools as its standard PEP 517 build backend and PyPA `build` as the frontend for producing wheel and source distributions. Pytest provides automated behavior checks; Ruff's default lint selection (`E4`, `E7`, `E9`, `F`) checks common Python errors, while Ruff format enforces the configured 88-character layout and preserves existing quote choices. These tools are development-only; there are no runtime dependencies.

## Checks

Run the tests with:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Run the linter with:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
```

Check formatting with:

```powershell
.\.venv\Scripts\python.exe -m ruff format --check .
```

## Build and verify an installed distribution

Build both a wheel and source distribution locally; this does not publish either artifact:

```powershell
$repo = (Get-Location).Path
$dist = Join-Path $repo 'dist'
.\.venv\Scripts\python.exe -m build --sdist --wheel --outdir $dist
$wheel = Join-Path $dist 'loglens-0.1.0-py3-none-any.whl'
$venv = Join-Path $env:TEMP ("loglens-wheel-check-" + [guid]::NewGuid().ToString('N'))
py -3.12 -m venv $venv
& (Join-Path $venv 'Scripts\python.exe') -m pip install $wheel
$sample = (Resolve-Path (Join-Path $repo 'samples\valid-clf.log')).Path
Push-Location $env:TEMP
& (Join-Path $venv 'Scripts\loglens.exe') --help
& (Join-Path $venv 'Scripts\loglens.exe') summary $sample
& (Join-Path $venv 'Scripts\loglens.exe') filter $sample --status 200 --method get
& (Join-Path $venv 'Scripts\loglens.exe') top-paths $sample --limit 3
& (Join-Path $venv 'Scripts\loglens.exe') top-ips $sample
Pop-Location
```

Run the help command with `summary`, `filter`, `top-paths`, and `top-ips` plus `--help` to inspect each installed command. The sample path is resolved before changing directories, so all operations exercise the installed package from outside the checkout. The wheel contains the `loglens` package and console entry point; sample logs remain repository fixtures and are not installed into the package. The source distribution is built from the same PEP 517 configuration. A `LICENSE` is not included because Sam's license decision is pending; local packaging does not grant a license, and this project does not publish to PyPI.

The suite uses fixed sample expectations and one-shot iterables to verify behavior without deriving expected values from the implementation. CLI integration tests run complete commands against tracked sample files and cross-check summary totals, a combined filter, and both rankings against `samples/README.md`; they also smoke-test the installed console launcher locally. The suite does not set timing or memory thresholds, which are environment-sensitive, or exhaustively fuzz log formats outside the documented CLF subset.

GitHub Actions runs the same lint, format, and pytest commands on pushes and pull requests with Python 3.12. Its token has only `contents: read` permission; no project secrets are required.

## Scaling review

Run the reproducible standard-library benchmark from the repository root with:

```powershell
.\.venv\Scripts\python.exe scripts/benchmark_scaling.py --sizes 1000 5000 --repeats 3
```

The script writes temporary UTF-8 CLF files and removes them when it exits. The repeat-heavy dataset reuses one request target and IP; the high-cardinality dataset varies both for every record and alternates statuses 200/404. It measures summary, status-200 filtering, target ranking, and IP ranking. Each operation is timed with `perf_counter`; the table reports median wall time and the maximum Python allocation peak from `tracemalloc` across repetitions. File generation is outside the measured region. Python and platform details are printed by the script.

These results are diagnostic, not an SLA. `tracemalloc` measures traced Python allocations, not process RSS or OS page cache. Summary and filter operations retain bounded aggregate/iterator state; ranking retains counters and sorting state proportional to distinct keys, as the ranking contract permits. No large dataset is committed.

### Recorded run

Run on Python 3.12.10 (CPython), Windows 11 10.0.26200, AMD64, AMD64 Family 25 Model 97 Stepping 2, AuthenticAMD. Each row is the median of three runs; peak is the maximum traced Python allocation observed across those runs.

| Dataset | Records | Operation | Median wall time (ms) | Peak traced memory (KiB) |
| --- | ---: | --- | ---: | ---: |
| Repeat-heavy | 1,000 | Summary | 60.3 | 28.6 |
| Repeat-heavy | 1,000 | Status-200 filter | 57.5 | 28.6 |
| Repeat-heavy | 1,000 | Top targets | 58.8 | 28.4 |
| Repeat-heavy | 1,000 | Top IPs | 59.9 | 28.4 |
| High-cardinality | 1,000 | Summary | 95.0 | 28.7 |
| High-cardinality | 1,000 | Status-200 filter | 88.6 | 28.9 |
| High-cardinality | 1,000 | Top targets | 92.1 | 217.5 |
| High-cardinality | 1,000 | Top IPs | 93.9 | 209.6 |
| Repeat-heavy | 5,000 | Summary | 293.0 | 28.3 |
| Repeat-heavy | 5,000 | Status-200 filter | 286.1 | 28.3 |
| Repeat-heavy | 5,000 | Top targets | 291.2 | 28.2 |
| Repeat-heavy | 5,000 | Top IPs | 291.0 | 28.1 |
| High-cardinality | 5,000 | Summary | 461.2 | 28.5 |
| High-cardinality | 5,000 | Status-200 filter | 449.5 | 28.7 |
| High-cardinality | 5,000 | Top targets | 472.0 | 1,070.8 |
| High-cardinality | 5,000 | Top IPs | 461.1 | 1,007.6 |

The input iterator, summary and filter remain close to constant traced memory as row count grows. Rankers stay similarly small when every record shares a key, but their counters and sorted distinct-key result grow with cardinality, as designed. Wall times include Python-level parsing and tracing overhead and are not suitable as uninstrumented throughput estimates.

## Licence
Copyright (c) 2026 Samuel Briggs

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.