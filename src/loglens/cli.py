"""Argument interface for the LogLens command line."""

import argparse
import sys
from collections.abc import Sequence


def _add_file_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("file", metavar="FILE", help="Path to a local access log.")


def build_parser() -> argparse.ArgumentParser:
    """Build the approved LogLens command and argument structure."""
    parser = argparse.ArgumentParser(
        prog="loglens",
        description="Inspect local HTTP access logs.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    commands = parser.add_subparsers(dest="command", required=True)

    summary = commands.add_parser(
        "summary",
        help="Summarize a log file (not available yet).",
        description="Summary interface; request analysis is not available yet.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    _add_file_argument(summary)

    filter_command = commands.add_parser(
        "filter",
        help="Filter log records (not available yet).",
        description="Filter interface; record filtering is not available yet.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    _add_file_argument(filter_command)
    filter_command.add_argument("--status", type=int, metavar="CODE", help="Select a response status.")
    filter_command.add_argument(
        "--method",
        type=str.upper,
        metavar="METHOD",
        help="Select an HTTP request method (case-normalized to uppercase).",
    )

    for command_name, command_help, command_description in (
        (
            "top-paths",
            "Rank requested paths (not available yet).",
            "Top-paths interface; path ranking is not available yet.",
        ),
        (
            "top-ips",
            "Rank client IP addresses (not available yet).",
            "Top-ips interface; address ranking is not available yet.",
        ),
    ):
        command = commands.add_parser(
            command_name,
            help=command_help,
            description=command_description,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        _add_file_argument(command)
        command.add_argument(
            "--limit",
            type=int,
            default=10,
            metavar="N",
            help="Maximum number of ranked results.",
        )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Parse CLI arguments and report that analysis commands are not implemented."""
    args = build_parser().parse_args(argv)
    print(f"The '{args.command}' command is not available yet.", file=sys.stderr)
    return 1