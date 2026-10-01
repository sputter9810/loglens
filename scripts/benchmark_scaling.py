"""Reproducible, temporary-file scaling measurements for the LogLens pipeline."""

import argparse
import gc
import ipaddress
import platform
import statistics
import time
import tracemalloc
from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory

from loglens.analysis import (
    filter_by_status,
    rank_client_ips,
    rank_request_targets,
    summarize_requests,
)
from loglens.input import InputStats, iter_log_records


def _write_dataset(path: Path, record_count: int, *, high_cardinality: bool) -> None:
    base_ip = int(ipaddress.IPv6Address("2001:db8::"))
    with path.open("w", encoding="utf-8", newline="\n") as output:
        for index in range(record_count):
            if high_cardinality:
                client_ip = str(ipaddress.IPv6Address(base_ip + index + 1))
                target = f"/item/{index}?batch=benchmark"
                status = 200 if index % 2 == 0 else 404
            else:
                client_ip = "192.0.2.10"
                target = "/repeat?batch=benchmark"
                status = 200

            output.write(
                f'{client_ip} - - [01/Oct/2025:12:00:00 +0000] '
                f'"GET {target} HTTP/1.1" {status} 1\n'
            )


def _summarize(path: Path) -> int:
    stats = InputStats()
    summary = summarize_requests(iter_log_records(path, stats))
    return summary.total_requests


def _filter_200(path: Path) -> int:
    stats = InputStats()
    return sum(
        1 for _ in filter_by_status(iter_log_records(path, stats), 200)
    )


def _rank_targets(path: Path) -> list[tuple[str, int]]:
    stats = InputStats()
    return rank_request_targets(iter_log_records(path, stats))


def _rank_ips(path: Path) -> list[tuple[str, int]]:
    stats = InputStats()
    return rank_client_ips(iter_log_records(path, stats))


def _measure(
    operation: Callable[[Path], object], path: Path, repeats: int
) -> tuple[float, int]:
    elapsed_seconds = []
    peak_bytes = []
    for _ in range(repeats):
        gc.collect()
        tracemalloc.start()
        started = time.perf_counter()
        result = operation(path)
        elapsed_seconds.append(time.perf_counter() - started)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        peak_bytes.append(peak)
        del result

    return statistics.median(elapsed_seconds), max(peak_bytes)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sizes",
        type=int,
        nargs="+",
        default=[10_000, 50_000],
        help="Record counts per temporary dataset (default: 10000 50000).",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=3,
        help="Measurement repetitions per operation (default: 3).",
    )
    args = parser.parse_args()
    if args.repeats <= 0 or any(size <= 0 for size in args.sizes):
        parser.error("sizes and repeats must be positive integers")

    print(
        f"Python {platform.python_version()} ({platform.python_implementation()}); "
        f"{platform.platform()}; machine={platform.machine()}; "
        f"processor={platform.processor() or 'unknown'}"
    )
    print(f"sizes={args.sizes}; repeats={args.repeats}; peak=tracemalloc Python bytes")
    print("dataset         records operation       median_ms peak_KiB")

    operations = (
        ("summary", _summarize),
        ("filter-200", _filter_200),
        ("top-targets", _rank_targets),
        ("top-ips", _rank_ips),
    )
    with TemporaryDirectory(prefix="loglens-benchmark-") as temp_dir:
        temp_path = Path(temp_dir)
        for size in args.sizes:
            for dataset_name, high_cardinality in (
                ("repeat-heavy", False),
                ("high-cardinality", True),
            ):
                data_path = temp_path / f"{dataset_name}-{size}.log"
                _write_dataset(data_path, size, high_cardinality=high_cardinality)
                for operation_name, operation in operations:
                    median_seconds, peak_bytes = _measure(
                        operation, data_path, args.repeats
                    )
                    print(
                        f"{dataset_name:<16} {size:>8} {operation_name:<14} "
                        f"{median_seconds * 1000:>9.1f} {peak_bytes / 1024:>8.1f}"
                    )


if __name__ == "__main__":
    main()
