from importlib.metadata import entry_points

import pytest

from loglens.cli import build_parser, main


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


@pytest.mark.parametrize(
    "argv",
    [
        ["summary", "access.log"],
        ["filter", "access.log", "--status", "200"],
        ["top-paths", "access.log"],
        ["top-ips", "access.log"],
    ],
)
def test_unimplemented_commands_report_unavailable(argv: list[str], capsys) -> None:
    assert main(argv) == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "not available yet" in captured.err


def test_invalid_argument_shape_exits_with_argparse_status() -> None:
    with pytest.raises(SystemExit) as exception:
        main(["summary"])

    assert exception.value.code == 2


def test_console_entry_point_is_registered() -> None:
    entry_point = next(
        entry_point
        for entry_point in entry_points(group="console_scripts")
        if entry_point.name == "loglens"
    )

    assert entry_point.value == "loglens.cli:main"