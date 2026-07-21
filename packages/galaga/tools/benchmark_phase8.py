"""Measure the Phase 8 diagonal-operation cutover layers reproducibly."""

from __future__ import annotations

import argparse
import platform
import sys
import timeit
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import galaga
import galaga.core as core
import galaga.legacy as legacy


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    operation: str
    implementation: str
    microseconds: float


def _median_microseconds(function: Callable[[], object], *, number: int, repeat: int) -> float:
    samples = timeit.repeat(function, number=number, repeat=repeat)
    return float(np.median(samples) * 1_000_000 / number)


def benchmark(*, number: int = 2_000, repeat: int = 7) -> tuple[BenchmarkResult, ...]:
    """Benchmark equivalent dense Cl(1,3) operations across all cutover layers."""
    if number <= 0 or repeat <= 0:
        raise ValueError("number and repeat must be positive")

    signature = (1, -1, -1, -1)
    rng = np.random.default_rng(20260721)
    left_data = rng.standard_normal(16)
    right_data = rng.standard_normal(16)

    legacy_algebra = legacy.Algebra(signature)
    legacy_left = legacy.Multivector(legacy_algebra, left_data)
    legacy_right = legacy.Multivector(legacy_algebra, right_data)

    core_algebra = core.Algebra(signature=signature)
    core_left = core_algebra.multivector(left_data)
    core_right = core_algebra.multivector(right_data)

    public_algebra = galaga.Algebra(signature=signature)
    facade_left = public_algebra.multivector(left_data)
    facade_right = public_algebra.multivector(right_data)
    tracked_left = facade_left.with_expr()
    tracked_right = facade_right.with_expr()

    expected_product = legacy.geometric_product(legacy_left, legacy_right).data
    expected_reverse = legacy.reverse(legacy_left).data
    for value in (
        core.geometric_product(core_left, core_right),
        galaga.geometric_product(facade_left, facade_right),
        galaga.geometric_product(tracked_left, tracked_right),
    ):
        np.testing.assert_allclose(value.data, expected_product, rtol=0.0, atol=1e-12)
    for value in (core.reverse(core_left), galaga.reverse(facade_left), galaga.reverse(tracked_left)):
        np.testing.assert_allclose(value.data, expected_reverse, rtol=0.0, atol=1e-12)

    cases: tuple[tuple[str, str, Callable[[], object]], ...] = (
        ("geometric product", "legacy-v1", lambda: legacy.geometric_product(legacy_left, legacy_right)),
        ("geometric product", "direct-core", lambda: core.geometric_product(core_left, core_right)),
        ("geometric product", "facade-untracked", lambda: galaga.geometric_product(facade_left, facade_right)),
        ("geometric product", "facade-tracked", lambda: galaga.geometric_product(tracked_left, tracked_right)),
        ("reverse", "legacy-v1", lambda: legacy.reverse(legacy_left)),
        ("reverse", "direct-core", lambda: core.reverse(core_left)),
        ("reverse", "facade-untracked", lambda: galaga.reverse(facade_left)),
        ("reverse", "facade-tracked", lambda: galaga.reverse(tracked_left)),
    )
    return tuple(
        BenchmarkResult(operation, implementation, _median_microseconds(call, number=number, repeat=repeat))
        for operation, implementation, call in cases
    )


def render_markdown(results: Sequence[BenchmarkResult], *, number: int, repeat: int) -> str:
    """Render benchmark results with separate core and legacy ratios."""
    lookup = {(result.operation, result.implementation): result.microseconds for result in results}
    lines = [
        "# Phase 8 Performance Baseline",
        "",
        "This is a local microbenchmark, not a cross-machine release threshold. It",
        "separates the numeric engine from facade wrapping and optional expression",
        "provenance. Every timed path is first checked against the same legacy",
        "Cl(1,3) coefficients.",
        "",
        f"- Python: {platform.python_version()} ({platform.python_implementation()})",
        f"- Platform: {platform.platform()}",
        f"- NumPy: {np.__version__}",
        f"- Samples: median of {repeat} repeats × {number} calls",
        "- Seed: `20260721`",
        "",
        "| Operation | Implementation | Median µs | vs direct core | vs legacy v1 |",
        "|---|---|---:|---:|---:|",
    ]
    for result in results:
        core_time = lookup[(result.operation, "direct-core")]
        legacy_time = lookup[(result.operation, "legacy-v1")]
        lines.append(
            f"| {result.operation} | {result.implementation} | {result.microseconds:.3f} "
            f"| {result.microseconds / core_time:.2f}× | {result.microseconds / legacy_time:.2f}× |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `direct-core` measures the Gram-matrix numeric engine without facade work.",
            "- `facade-untracked` isolates public wrapping, coercion, and catalog dispatch.",
            "- `facade-tracked` additionally creates immutable expression provenance.",
            "- `legacy-v1` is the retained table-engine reference during Phase 8.",
            (
                "- In this run, direct-core geometric product is "
                f"{lookup[('geometric product', 'direct-core')] / lookup[('geometric product', 'legacy-v1')]:.2f}× "
                "the retained diagonal table engine; the untracked facade is "
                f"{lookup[('geometric product', 'facade-untracked')] / lookup[('geometric product', 'direct-core')]:.2f}× "
                "direct core."
            ),
            (
                "- Direct-core reverse is "
                f"{lookup[('reverse', 'direct-core')] / lookup[('reverse', 'legacy-v1')]:.2f}× "
                "the legacy time; tracked results additionally pay for immutable expression provenance."
            ),
            "",
            "Re-run from the repository root with:",
            "",
            "```shell",
            "PYTHONPATH=packages/galaga uv run --python 3.11 python -m tools.benchmark_phase8 \\",
            "  --output docs/v2/phase8-performance.md",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--number", type=int, default=2_000)
    parser.add_argument("--repeat", type=int, default=7)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    results = benchmark(number=args.number, repeat=args.repeat)
    report = render_markdown(results, number=args.number, repeat=args.repeat)
    if args.output is None:
        sys.stdout.write(report)
    else:
        args.output.write_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
