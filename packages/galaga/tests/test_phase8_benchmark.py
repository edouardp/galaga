"""Executable schema and correctness smoke test for the Phase 8 benchmark."""

import pytest
from tools.benchmark_phase8 import benchmark, render_markdown


@pytest.mark.legacy_oracle
def test_phase8_benchmark_compares_every_layer_after_coefficient_validation() -> None:
    results = benchmark(number=1, repeat=1)

    assert {(result.operation, result.implementation) for result in results} == {
        (operation, implementation)
        for operation in ("geometric product", "reverse")
        for implementation in ("legacy-v1", "direct-core", "facade-untracked", "facade-tracked")
    }
    assert all(result.microseconds > 0 for result in results)
    report = render_markdown(results, number=1, repeat=1)
    assert "vs direct core" in report
    assert "vs legacy v1" in report
