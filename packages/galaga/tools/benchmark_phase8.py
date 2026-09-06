"""Measure current Galaga 2 cutover layers without executing the legacy engine.

The historical Phase 8 timings remain in docs/v2/phase8-performance.md. This
command retains its name for existing callers, but measures only live v2 paths.
"""

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


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    operation: str
    implementation: str
    microseconds: float


def _median_microseconds(function: Callable[[], object], *, number: int, repeat: int) -> float:
    samples = timeit.repeat(function, number=number, repeat=repeat)
    return float(np.median(samples) * 1_000_000 / number)


def benchmark(*, number: int = 2_000, repeat: int = 7) -> tuple[BenchmarkResult, ...]:
    """Validate and benchmark dense Cl(1,3) operations across the three v2 layers."""
    if number <= 0 or repeat <= 0:
        raise ValueError("number and repeat must be positive")

    signature = (1, -1, -1, -1)
    core_algebra = core.Algebra(signature=signature)
    rng = np.random.default_rng(20260721)
    left_data = rng.standard_normal(core_algebra.dim)
    right_data = rng.standard_normal(core_algebra.dim)
    core_left = core_algebra.multivector(left_data)
    core_right = core_algebra.multivector(right_data)

    public_algebra = galaga.Algebra(signature=signature)
    facade_left = public_algebra.multivector(left_data)
    facade_right = public_algebra.multivector(right_data)
    tracked_left = facade_left.with_expr()
    tracked_right = facade_right.with_expr()

    # An untimed Chevalley left action independently checks the default product
    # backend and its public operation entry point. Reverse uses its grade law,
    # not the same implementation or cached signs as the timed operation.
    reference = core.Algebra(gram=core_algebra.gram, product_backend="reference")
    expected_product = reference.left_action(reference.multivector(left_data)) @ right_data
    grades = np.array([mask.bit_count() for mask in range(core_algebra.dim)])
    reverse_signs = np.where((grades * (grades - 1) // 2) % 2, -1, 1)
    expected_reverse = reverse_signs * left_data
    for value in (
        core.geometric_product(core_left, core_right),
        galaga.geometric_product(facade_left, facade_right),
        galaga.geometric_product(tracked_left, tracked_right),
    ):
        np.testing.assert_allclose(value.data, expected_product, rtol=0.0, atol=1e-12)
    for value in (core.reverse(core_left), galaga.reverse(facade_left), galaga.reverse(tracked_left)):
        np.testing.assert_allclose(value.data, expected_reverse, rtol=0.0, atol=1e-12)

    cases: tuple[tuple[str, str, Callable[[], object]], ...] = (
        ("geometric product", "direct-core", lambda: core.geometric_product(core_left, core_right)),
        ("geometric product", "facade-untracked", lambda: galaga.geometric_product(facade_left, facade_right)),
        ("geometric product", "facade-tracked", lambda: galaga.geometric_product(tracked_left, tracked_right)),
        ("reverse", "direct-core", lambda: core.reverse(core_left)),
        ("reverse", "facade-untracked", lambda: galaga.reverse(facade_left)),
        ("reverse", "facade-tracked", lambda: galaga.reverse(tracked_left)),
    )
    return tuple(
        BenchmarkResult(operation, implementation, _median_microseconds(call, number=number, repeat=repeat))
        for operation, implementation, call in cases
    )


def render_markdown(results: Sequence[BenchmarkResult], *, number: int, repeat: int) -> str:
    """Report live facade overhead without mixing old and new timing samples."""
    lookup = {(result.operation, result.implementation): result.microseconds for result in results}
    lines = [
        "# Galaga 2 Performance Check",
        "",
        "This is a local microbenchmark, not a cross-machine release threshold. It",
        "separates the numeric engine from facade wrapping and optional expression",
        "provenance. Every timed path is first checked against a forced core",
        "reference-backend left action for the Cl(1,3) product and the grade-sign",
        "law for reverse. Reference construction and validation are not timed.",
        "",
        "The legacy engine is not imported or timed. Historical v1 measurements",
        "remain in `docs/v2/phase8-performance.md`; they are not samples from this run.",
        "",
        f"- Python: {platform.python_version()} ({platform.python_implementation()})",
        f"- Platform: {platform.platform()}",
        f"- NumPy: {np.__version__}",
        f"- Samples: median of {repeat} repeats × {number} calls",
        "- Seed: `20260721`",
        "",
        "| Operation | Implementation | Median µs | vs direct core |",
        "|---|---|---:|---:|",
    ]
    for result in results:
        core_time = lookup[(result.operation, "direct-core")]
        lines.append(
            f"| {result.operation} | {result.implementation} | {result.microseconds:.3f} "
            f"| {result.microseconds / core_time:.2f}× |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `direct-core` measures the Gram-matrix numeric engine without facade work.",
            "- `facade-untracked` isolates public wrapping, coercion, and catalog dispatch.",
            "- `facade-tracked` additionally creates immutable expression provenance.",
            (
                "- In this run, untracked facade geometric product is "
                f"{lookup[('geometric product', 'facade-untracked')] / lookup[('geometric product', 'direct-core')]:.2f}× "
                "direct core."
            ),
            (
                "- Untracked facade reverse is "
                f"{lookup[('reverse', 'facade-untracked')] / lookup[('reverse', 'direct-core')]:.2f}× "
                "direct core; tracked results additionally pay for immutable expression provenance."
            ),
            "",
            "Re-run from the repository root with:",
            "",
            "```shell",
            "PYTHONPATH=packages/galaga uv run --python 3.11 python -m tools.benchmark_phase8 \\",
            "  --output /tmp/galaga-performance.md",
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
