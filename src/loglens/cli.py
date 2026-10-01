"""Argument interface for the LogLens command line."""

import argparse
import json
import sys
from collections.abc import Sequence

from loglens.analysis import (
    RequestSummary,
    filter_by_method,
    filter_by_status,
    rank_client_ips,
    rank_request_targets,
    summarize_requests,
)
from loglens.input import (
    AllRecordsInvalidError,
    InputStats,
    LogInputError,
    iter_log_records,
)
from loglens.models import AccessLogRecord


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
        help="Summarize requests and response statuses.",
        description="Summarize valid requests and response statuses in a log file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    _add_file_argument(summary)

    filter_command = commands.add_parser(
        "filter",
        help="Filter records by response status and/or method.",
        description="Select valid records matching all supplied selectors.",
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
            "Rank complete request targets.",
            "Rank complete request targets, including query strings.",
        ),
        (
            "top-ips",
            "Rank canonical client IP addresses.",
            "Rank canonical client IP addresses.",
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


def _print_record(record: AccessLogRecord) -> None:
    size = "-" if record.response_size is None else f"{record.response_size} bytes"
    target = json.dumps(record.request_target, ensure_ascii=True)
    print(
        f"{record.client_ip} {record.timestamp.isoformat()} {record.method} "
        f"{target} {record.protocol} {record.status} {size}"
    )


def _print_summary(summary: RequestSummary) -> None:
    print(f"Total requests: {summary.total_requests}")
    print("Exact status counts:")
    if summary.status_counts:
        for status, count in sorted(summary.status_counts.items()):
            print(f"  {status}: {count}")
    else:
        print("  None")

    print("Status categories:")
    for category, count in summary.category_counts.items():
        print(f"  {category}: {count}")


def _print_rankings(rankings: list[tuple[str, int]]) -> None:
    if not rankings:
        print("No requests to rank.")
        return

    for value, count in rankings:
        print(f"{count}\t{json.dumps(value, ensure_ascii=True)}")


def _report_input_stats(stats: InputStats) -> None:
    if stats.malformed_records > 0:
        print(
            f"Input: {stats.valid_records} valid records; "
            f"{stats.malformed_records} malformed records skipped; "
            f"{stats.blank_lines} blank lines ignored.",
            file=sys.stderr,
        )


def main(argv: Sequence[str] | None = None) -> int:
    """Run an analysis command against a local access-log file."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "filter" and args.status is None and args.method is None:
        parser.error("filter requires at least one of --status or --method")
    if args.command in {"top-paths", "top-ips"} and args.limit <= 0:
        parser.error("--limit must be a positive integer")
    if args.command == "filter" and args.status is not None and not 100 <= args.status <= 599:
        parser.error("--status must be between 100 and 599")

    stats = InputStats()
    records = iter_log_records(args.file, stats)

    try:
        if args.command == "summary":
            _print_summary(summarize_requests(records))
        elif args.command == "filter":
            selected = records
            if args.status is not None:
                selected = filter_by_status(selected, args.status)
            if args.method is not None:
                selected = filter_by_method(selected, args.method)

            match_count = 0
            for record in selected:
                _print_record(record)
                match_count += 1
            if match_count == 0:
                print("No records matched.")
        elif args.command == "top-paths":
            _print_rankings(rank_request_targets(records, args.limit))
        else:
            _print_rankings(rank_client_ips(records, args.limit))
    except AllRecordsInvalidError as error:
        _report_input_stats(stats)
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except LogInputError as error:
        _report_input_stats(stats)
        suffix = " Output above may be incomplete." if error.incomplete else ""
        print(f"Error: {error}.{suffix}", file=sys.stderr)
        return 1

    _report_input_stats(stats)
    return 0