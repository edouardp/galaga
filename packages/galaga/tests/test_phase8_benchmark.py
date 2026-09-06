"""The cutover benchmark validates current layers without a live v1 oracle."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from tools.benchmark_phase8 import BenchmarkResult, benchmark, main, render_markdown

import galaga
import galaga.core as core
from tools import benchmark_phase8


def test_benchmark_compares_current_layers_after_coefficient_validation() -> None:
    results = benchmark(number=1, repeat=1)

    assert {(result.operation, result.implementation) for result in results} == {
        (operation, implementation)
        for operation in ("geometric product", "reverse")
        for implementation in ("direct-core", "facade-untracked", "facade-tracked")
    }
    assert all(result.microseconds > 0 for result in results)
    report = render_markdown(results, number=1, repeat=1)
    assert "vs direct core" in report
    assert "vs legacy v1" not in report
    assert "The legacy engine is not imported or timed" in report
    assert "docs/v2/phase8-performance.md" in report
    assert "--output /tmp/galaga-performance.md" in report


@pytest.mark.parametrize("number, repeat", ((0, 1), (-1, 1), (1, 0), (1, -1)))
def test_benchmark_rejects_nonpositive_sample_counts(number: int, repeat: int) -> None:
    with pytest.raises(ValueError, match="number and repeat must be positive"):
        benchmark(number=number, repeat=repeat)


def test_product_oracle_uses_the_forced_reference_backend_before_timing(monkeypatch: pytest.MonkeyPatch) -> None:
    observed = []
    timed = []
    original = core.Algebra.left_action

    def record_reference(algebra, value):
        observed.append(algebra.product_backend)
        return original(algebra, value)

    def time_after_validation(function, *, number, repeat):
        assert observed == ["reference"]
        timed.append(function())
        return 1.0

    monkeypatch.setattr(core.Algebra, "left_action", record_reference)
    monkeypatch.setattr(benchmark_phase8, "_median_microseconds", time_after_validation)

    results = benchmark(number=1, repeat=1)

    assert len(timed) == len(results) == 6
    assert all(value.algebra.dim == 1 << value.algebra.n for value in timed)


@pytest.mark.parametrize("operation", ("geometric_product", "reverse"))
@pytest.mark.parametrize("layer", ("direct-core", "facade-untracked", "facade-tracked"))
def test_each_timed_path_must_pass_the_independent_oracle(
    operation: str, layer: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    api = core if layer == "direct-core" else galaga
    original = getattr(api, operation)

    def incorrect(*values):
        value = values[0]
        targeted = layer == "direct-core" or (value.expr is not None) == (layer == "facade-tracked")
        return value.algebra.scalar(0.0) if targeted else original(*values)

    def reject_timing(*args, **kwargs):
        raise AssertionError("timing started before validation failed")

    monkeypatch.setattr(api, operation, incorrect)
    monkeypatch.setattr(benchmark_phase8, "_median_microseconds", reject_timing)

    with pytest.raises(AssertionError, match="Not equal to tolerance"):
        benchmark(number=1, repeat=1)


def test_sample_aggregation_reports_the_median_per_call_in_microseconds(monkeypatch: pytest.MonkeyPatch) -> None:
    def repeat(function, *, number, repeat):
        assert number == 10 and repeat == 3
        return [0.0003, 0.0001, 0.0002]

    monkeypatch.setattr(benchmark_phase8.timeit, "repeat", repeat)

    assert benchmark_phase8._median_microseconds(lambda: None, number=10, repeat=3) == pytest.approx(20.0)


def test_report_ratios_use_only_same_run_core_timings() -> None:
    results = tuple(
        BenchmarkResult(operation, layer, duration)
        for operation in ("geometric product", "reverse")
        for layer, duration in (("direct-core", 2.0), ("facade-untracked", 3.0), ("facade-tracked", 5.0))
    )

    report = render_markdown(results, number=10, repeat=3)

    assert "| geometric product | facade-untracked | 3.000 | 1.50× |" in report
    assert "| reverse | facade-tracked | 5.000 | 2.50× |" in report
    assert "not samples from this run" in report


def test_benchmark_does_not_construct_legacy_values_or_import_their_modules() -> None:
    program = """
import importlib.abc
import sys

class RejectLegacy(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in {'galaga.algebra', 'galaga.expr', 'galaga.ops'} or fullname.startswith('galaga.legacy'):
            raise AssertionError('benchmark imported legacy module: ' + fullname)

sys.meta_path.insert(0, RejectLegacy())
from tools.benchmark_phase8 import main
assert main(['--number', '1', '--repeat', '1']) == 0
assert 'galaga.algebra' not in sys.modules
assert 'galaga.legacy' not in sys.modules
"""
    completed = subprocess.run([sys.executable, "-c", program], check=False, capture_output=True, text=True, timeout=60)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "# Galaga 2 Performance Check" in completed.stdout


def test_command_writes_current_results_without_replacing_the_historical_report(tmp_path: Path) -> None:
    historical = Path(__file__).resolve().parents[3] / "docs/v2/phase8-performance.md"
    original = historical.read_bytes()
    report = tmp_path / "current-performance.md"

    assert main(["--number", "1", "--repeat", "1", "--output", str(report)]) == 0
    assert "# Galaga 2 Performance Check" in report.read_text()
    assert historical.read_bytes() == original


def test_reverse_reference_is_derived_for_each_exterior_grade(monkeypatch: pytest.MonkeyPatch) -> None:
    observed = []
    original = core.reverse

    def check_grade_law(value):
        result = original(value)
        for mask, coefficient in enumerate(value.data):
            grade = mask.bit_count()
            expected = (-1) ** (grade * (grade - 1) // 2) * coefficient
            assert result.data[mask] == expected
        observed.append(value.algebra.n)
        return result

    monkeypatch.setattr(core, "reverse", check_grade_law)

    benchmark(number=1, repeat=1)

    assert observed and all(dimension == 4 for dimension in observed)
