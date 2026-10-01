from datetime import UTC, datetime
from importlib.metadata import entry_points
from pathlib import Path

import pytest

from loglens.cli import build_parser, main
from loglens.input import LogInputError
from loglens.models import AccessLogRecord

SAMPLES = Path(__file__).parents[1] / "samples"


def command_args(command: str, path: Path) -> list[str]:
    args = [command, str(path)]
    if command == "filter":
        args.extend(["--method", "GET"])
    return args


@pytest.mark.parametrize(
    "argv",
    [
        ["--help"],
        ["summary", "--help"],
        ["filter", "--help"],
        ["top-paths", "--help"],
        ["top-ips", "--help"],
    ],
)
def test_help_pages_exit_successfully(argv: list[str], capsys) -> None:
    with pytest.raises(SystemExit) as exception:
        main(argv)

    assert exception.value.code == 0
    assert "usage:" in capsys.readouterr().out.lower()


def test_command_argument_shapes_and_defaults() -> None:
    parser = build_parser()

    summary = parser.parse_args(["summary", "access.log"])
    filtered = parser.parse_args(
        ["filter", "access.log", "--status", "404", "--method", "get"]
    )
    filter_without_selectors = parser.parse_args(["filter", "access.log"])
    top_paths = parser.parse_args(["top-paths", "access.log"])
    top_ips = parser.parse_args(["top-ips", "access.log", "--limit", "4"])

    assert (summary.command, summary.file) == ("summary", "access.log")
    assert (filtered.command, filtered.file, filtered.status, filtered.method) == (
        "filter",
        "access.log",
        404,
        "GET",
    )
    assert filter_without_selectors.command == "filter"
    assert (top_paths.command, top_paths.file, top_paths.limit) == (
        "top-paths",
        "access.log",
        10,
    )
    assert (top_ips.command, top_ips.file, top_ips.limit) == (
        "top-ips",
        "access.log",
        4,
    )


def test_summary_command_reports_sample_totals(capsys) -> None:
    assert main(["summary", str(SAMPLES / "valid-clf.log")]) == 0

    captured = capsys.readouterr()
    assert "Total requests: 8" in captured.out
    assert "  404: 2" in captured.out
    assert "  1xx: 1" in captured.out
    assert "  5xx: 1" in captured.out
    assert captured.err == ""


def test_filter_combines_status_and_method_with_and(capsys) -> None:
    assert main(
        [
            "filter",
            str(SAMPLES / "mixed-input.log"),
            "--status",
            "404",
            "--method",
            "post",
        ]
    ) == 0

    captured = capsys.readouterr()
    assert 'POST "/shared?mode=test" HTTP/1.1 404 -' in captured.out
    assert "/tea" not in captured.out
    assert captured.err == (
        "Input: 4 valid records; 4 malformed records skipped; 2 blank lines ignored.\n"
    )


def test_filter_preserves_order_and_reports_zero_matches(capsys) -> None:
    assert main(["filter", str(SAMPLES / "valid-clf.log"), "--method", "get"]) == 0
    captured = capsys.readouterr()
    assert captured.out.index('GET "/alpha?x=1"') < captured.out.index('GET "/gamma"')
    assert captured.out.index('GET "/gamma"') < captured.out.index('GET "/epsilon"')

    assert main(
        ["filter", str(SAMPLES / "valid-clf.log"), "--status", "599"]
    ) == 0
    assert capsys.readouterr().out == "No records matched.\n"


def test_empty_file_returns_zero_summary_and_empty_filter_result(capsys) -> None:
    empty = str(SAMPLES / "empty.log")
    assert main(["summary", empty]) == 0
    summary = capsys.readouterr()
    assert "Total requests: 0" in summary.out
    assert all(f"{category}: 0" in summary.out for category in ("1xx", "2xx", "3xx", "4xx", "5xx"))

    assert main(["filter", empty, "--method", "GET"]) == 0
    assert capsys.readouterr().out == "No records matched.\n"


@pytest.mark.parametrize("command", ["summary", "filter", "top-paths", "top-ips"])
def test_blank_only_file_has_no_diagnostic(command: str, tmp_path: Path, capsys) -> None:
    blank_only = tmp_path / "blank-only.log"
    blank_only.write_text("\n  \n\t\n", encoding="utf-8")

    assert main(command_args(command, blank_only)) == 0
    captured = capsys.readouterr()

    assert captured.err == ""
    if command == "summary":
        assert "Total requests: 0" in captured.out
    elif command == "filter":
        assert captured.out == "No records matched.\n"
    else:
        assert captured.out == "No requests to rank.\n"


def test_ranking_commands_report_sample_ties(capsys) -> None:
    sample = str(SAMPLES / "valid-clf.log")
    assert main(["top-paths", sample, "--limit", "3"]) == 0
    paths = capsys.readouterr()
    assert paths.out.splitlines() == [
        '2\t"/alpha?x=1"',
        '2\t"/beta"',
        '1\t"/delta"',
    ]

    assert main(["top-ips", sample]) == 0
    ips = capsys.readouterr()
    assert ips.out.splitlines() == [
        '2\t"192.0.2.10"',
        '2\t"198.51.100.20"',
        '2\t"2001:db8::1"',
        '2\t"203.0.113.9"',
    ]


@pytest.mark.parametrize("command", ["summary", "filter", "top-paths", "top-ips"])
def test_mixed_input_totals_are_consistent_across_commands(command: str, capsys) -> None:
    assert main(command_args(command, SAMPLES / "mixed-input.log")) == 0
    captured = capsys.readouterr()

    if command == "summary":
        assert "Total requests: 4" in captured.out
        assert "  2xx: 2" in captured.out
        assert "  3xx: 0" in captured.out
    assert captured.err == (
        "Input: 4 valid records; 4 malformed records skipped; 2 blank lines ignored.\n"
    )


@pytest.mark.parametrize("command", ["summary", "filter", "top-paths", "top-ips"])
def test_all_invalid_input_fails_consistently_without_record_dumps(
    command: str, capsys
) -> None:
    assert main(command_args(command, SAMPLES / "all-invalid.log")) == 1
    captured = capsys.readouterr()

    assert captured.out == ""
    assert "Input: 0 valid records; 5 malformed records skipped; 0 blank lines ignored." in captured.err
    assert "no valid access-log records" in captured.err
    assert "not-an-ip" not in captured.err
    assert len(captured.err.splitlines()) == 2


def test_invalid_argument_shape_exits_with_argparse_status() -> None:
    with pytest.raises(SystemExit) as exception:
        main(["summary"])

    assert exception.value.code == 2


@pytest.mark.parametrize(
    "argv",
    [
        ["filter", str(SAMPLES / "valid-clf.log")],
        ["filter", str(SAMPLES / "valid-clf.log"), "--status", "99"],
        ["filter", str(SAMPLES / "valid-clf.log"), "--status", "600"],
        ["filter", str(SAMPLES / "valid-clf.log"), "--status", "abc"],
        ["filter", str(SAMPLES / "valid-clf.log"), "--method", "GET/POST"],
        ["top-paths", str(SAMPLES / "valid-clf.log"), "--limit", "0"],
        ["top-ips", str(SAMPLES / "valid-clf.log"), "--limit", "-1"],
    ],
)
def test_invalid_arguments_exit_two_with_argparse_errors(argv: list[str], capsys) -> None:
    with pytest.raises(SystemExit) as exception:
        main(argv)

    assert exception.value.code == 2
    assert "error:" in capsys.readouterr().err


def test_status_range_boundaries_are_accepted(tmp_path: Path, capsys) -> None:
    sample = tmp_path / "boundaries.log"
    sample.write_text(
        '192.0.2.1 - - [01/Oct/2025:12:00:00 +0000] "GET /continue HTTP/1.1" 100 0\n'
        '192.0.2.2 - - [01/Oct/2025:12:01:00 +0000] "GET /network-error HTTP/1.1" 599 -\n',
        encoding="utf-8",
    )

    assert main(["filter", str(sample), "--status", "100"]) == 0
    assert '"/continue" HTTP/1.1 100' in capsys.readouterr().out
    assert main(["filter", str(sample), "--status", "599"]) == 0
    assert '"/network-error" HTTP/1.1 599' in capsys.readouterr().out


@pytest.mark.parametrize("path_kind", ["missing", "directory"])
def test_expected_path_errors_exit_one_without_traceback(
    tmp_path: Path, capsys, path_kind: str
) -> None:
    path = tmp_path / "missing.log"
    if path_kind == "directory":
        path.mkdir()

    assert main(["summary", str(path)]) == 1
    captured = capsys.readouterr()
    assert "Error: cannot open" in captured.err
    assert "Traceback" not in captured.err


def test_permission_error_exits_one_without_platform_permission_bits(
    monkeypatch, capsys
) -> None:
    def deny_open(self, *args, **kwargs):
        raise PermissionError("access denied")

    monkeypatch.setattr(Path, "open", deny_open)

    assert main(["summary", str(SAMPLES / "valid-clf.log")]) == 1
    captured = capsys.readouterr()
    assert "access denied" in captured.err
    assert "Traceback" not in captured.err


def test_utf8_decode_failure_exits_one_without_traceback(tmp_path: Path, capsys) -> None:
    invalid_utf8 = tmp_path / "invalid-utf8.log"
    invalid_utf8.write_bytes(b"\xff")

    assert main(["summary", str(invalid_utf8)]) == 1
    captured = capsys.readouterr()
    assert "failed before completion" in captured.err
    assert "Traceback" not in captured.err


def test_record_output_escapes_control_characters(monkeypatch, capsys) -> None:
    record = AccessLogRecord(
        client_ip="192.0.2.1",
        timestamp=datetime(2025, 10, 1, tzinfo=UTC),
        method="GET",
        request_target="/line\nbreak\x1b",
        protocol="HTTP/1.1",
        status=200,
        response_size=0,
    )
    monkeypatch.setattr("loglens.cli.iter_log_records", lambda path, stats: iter((record,)))

    assert main(["filter", "sample.log", "--method", "GET"]) == 0

    output = capsys.readouterr().out
    assert output.count("\n") == 1
    assert r"/line\nbreak\u001b" in output


def test_mid_read_failure_reports_incomplete_streamed_output(monkeypatch, capsys) -> None:
    record = AccessLogRecord(
        client_ip="192.0.2.1",
        timestamp=datetime(2025, 10, 1, tzinfo=UTC),
        method="GET",
        request_target="/first",
        protocol="HTTP/1.1",
        status=200,
        response_size=1,
    )

    def incomplete_records(path: str, stats):
        yield record
        raise LogInputError("simulated read failure", incomplete=True)

    monkeypatch.setattr("loglens.cli.iter_log_records", incomplete_records)

    assert main(["filter", "sample.log", "--method", "GET"]) == 1
    captured = capsys.readouterr()
    assert 'GET "/first"' in captured.out
    assert "Output above may be incomplete" in captured.err


def test_console_entry_point_is_registered() -> None:
    entry_point = next(
        entry_point
        for entry_point in entry_points(group="console_scripts")
        if entry_point.name == "loglens"
    )

    assert entry_point.value == "loglens.cli:main"