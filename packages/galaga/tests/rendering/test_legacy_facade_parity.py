"""Facade rendering contracts backed by historical data, not the legacy engine."""

from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime
from math import isfinite
from pathlib import Path

import pytest
from tools.isolate_phase8_legacy_tests import LEGACY_ORACLE_TESTS
from tools.rendering_parity import (
    BASELINE,
    CASES,
    DIFFERENCE_LEDGER,
    RenderedResult,
    RenderingCase,
    RenderingContext,
    RenderingProfile,
    _load_baseline,
    audit_all,
    audit_case,
    covered_operations,
    difference_keys,
    render_markdown_report,
    required_shared_operations,
    reviewed_facade_differences,
)

from galaga.facade.catalog import OPERATIONS
from tools import audit_rendering_parity


def test_case_registry_has_unique_stable_keys() -> None:
    keys = tuple(case.key for case in CASES)

    assert len(keys) == len(set(keys))
    assert set(keys) == set(BASELINE.cases)


def test_every_shared_registered_expression_operation_has_a_case() -> None:
    assert required_shared_operations() <= covered_operations()
    assert required_shared_operations() <= set(OPERATIONS)


def test_baseline_retains_capture_provenance_and_immutable_observations() -> None:
    assert BASELINE.source_commit == "d98c9f463ecd532e7d9c5b3bdc82aa471ecad1bc"
    for case in CASES:
        reference = BASELINE.cases[case.key]
        assert reference.intent == case.intent
        assert reference.channels == case.channels
        assert reference.legacy.implementation == "legacy-v1"
        assert reference.reviewed_facade.implementation == "core-facade-v2"
        assert reference.reviewed_facade.error is None
        assert isinstance(reference.reviewed_facade.coefficients, tuple)
        assert all(isfinite(value) for value in reference.reviewed_facade.coefficients)
    with pytest.raises(TypeError):
        BASELINE.cases[CASES[0].key] = BASELINE.cases[CASES[0].key]  # type: ignore[index]


def test_parity_suite_no_longer_opts_into_legacy_construction() -> None:
    assert "rendering/test_legacy_facade_parity.py" not in LEGACY_ORACLE_TESTS


def test_baseline_loader_rejects_unknown_schema(tmp_path: Path) -> None:
    path = tmp_path / "unsupported.json"
    path.write_text(json.dumps({"schema_version": 2}))
    with pytest.raises(ValueError, match="unsupported rendering baseline schema"):
        _load_baseline(path)


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.key)
def test_reviewed_latex_parity(case: RenderingCase) -> None:
    result = audit_case(case)
    ledgered = result.case.key in DIFFERENCE_LEDGER

    assert result.succeeded is not ledgered, (
        f"{result.case.key}: {'remove resolved ledger entry' if ledgered else 'classify new difference'}; "
        f"differences={result.differences!r}"
    )
    assert not reviewed_facade_differences(result), f"{case.key}: reviewed facade output regressed"


@pytest.mark.parametrize(
    "channel, mutate",
    (
        ("expression", lambda result: replace(result, expression="regression")),
        ("value", lambda result: replace(result, value="regression")),
        ("full", lambda result: replace(result, full="regression")),
        ("rich", lambda result: replace(result, rich="regression")),
        ("error", lambda result: replace(result, error="regression")),
        ("coefficients", lambda result: replace(result, coefficients=(99.0,) * len(result.coefficients or ()))),
    ),
)
@pytest.mark.parametrize("key", ("default-cl3/lie-bracket", "default-cl3/outerexp"))
def test_accepted_difference_cannot_hide_a_new_facade_regression(
    channel: str, key: str, mutate: Callable[[RenderedResult], RenderedResult]
) -> None:
    case = next(case for case in CASES if case.key == key)
    result = audit_case(case)
    regressed = replace(result, facade=mutate(result.facade))

    assert case.key in DIFFERENCE_LEDGER
    assert channel in reviewed_facade_differences(regressed)


@pytest.mark.parametrize("delta, expected", ((1e-13, ()), (1e-4, ("coefficients",))))
def test_reviewed_coefficients_use_numeric_tolerance_not_float_equality(
    delta: float, expected: tuple[str, ...]
) -> None:
    result = audit_case(CASES[0])
    assert result.facade.coefficients is not None
    perturbed = tuple(value + delta for value in result.facade.coefficients)

    assert (
        reviewed_facade_differences(replace(result, facade=replace(result.facade, coefficients=perturbed))) == expected
    )


@pytest.mark.parametrize("coefficients", (None, (), (0.0,), (float("nan"),) * 8, (float("inf"),) * 8))
def test_reviewed_coefficients_reject_missing_wrong_shape_and_nonfinite_values(
    coefficients: tuple[float, ...] | None,
) -> None:
    result = audit_case(CASES[0])
    regressed = replace(result, facade=replace(result.facade, coefficients=coefficients))

    assert "coefficients" in reviewed_facade_differences(regressed)


@pytest.mark.parametrize(
    "case",
    (replace(CASES[0], intent="different expression"), replace(CASES[0], channels=("full",))),
    ids=("intent", "channels"),
)
def test_case_metadata_cannot_silently_change_the_historical_comparison(case: RenderingCase) -> None:
    with pytest.raises(ValueError, match="metadata differs"):
        audit_case(case)


def test_missing_historical_case_is_not_silently_blessed() -> None:
    with pytest.raises(KeyError, match="unreviewed"):
        audit_case(replace(CASES[0], id="unreviewed"))


def test_unknown_facade_profile_is_rejected() -> None:
    with pytest.raises(KeyError, match="unknown"):
        RenderingContext(RenderingProfile("unknown", "No implicit algebra fallback"))


def test_audit_reports_facade_execution_errors_as_regressions() -> None:
    def broken_recipe(context: RenderingContext) -> None:
        raise RuntimeError("renderer failed")

    result = audit_case(replace(CASES[0], build=broken_recipe))

    assert result.facade.error == "RuntimeError: renderer failed"
    assert not result.succeeded
    assert "error" in reviewed_facade_differences(result)


def test_difference_ledger_exactly_matches_the_live_audit() -> None:
    observed = difference_keys(audit_case(case) for case in CASES)

    assert observed == frozenset(DIFFERENCE_LEDGER)


def test_markdown_report_is_structured_for_human_review() -> None:
    reviewed_difference = next(case for case in CASES if case.key == "default-cl3/lie-bracket")
    results = tuple(audit_case(case) for case in (*CASES[:6], reviewed_difference))
    failure_count = sum(not result.succeeded for result in results)
    report = render_markdown_report(
        results,
        generated_at=datetime(2026, 7, 19, tzinfo=UTC),
    )

    assert "# Galaga v1/v2 LaTeX Rendering Parity Report" in report
    assert "## How to review" in report
    assert "## Successful expressions" in report
    assert "## Differences" in report
    assert "## Coverage" in report
    assert "## Reviewed facade regressions" in report
    assert BASELINE.source_commit in report
    assert "The legacy engine is not executed" in report
    assert "| Reviewed facade regressions | 0 |" in report
    assert report.count("#### Rendered Expression (v1 vs v2)") == failure_count
    assert report.count("#### Emitted Latex (v1 vs v2)") == failure_count
    assert ("\\" * 5) + "\n" in report
    assert "```latex" in report
    assert "<details>" not in report
    assert "- [x] Accept v2" in report
    assert "- [ ] Match legacy v1" in report
    assert "> Accepted Galaga 2 correction:" in report


def test_report_does_not_preapprove_a_regression_in_an_accepted_difference() -> None:
    case = next(case for case in CASES if case.key == "default-cl3/lie-bracket")
    result = audit_case(case)
    regressed = replace(result, facade=replace(result.facade, full="regression"))
    report = render_markdown_report((regressed,))

    assert "| Reviewed facade regressions | 1 |" in report
    assert "changed reviewed v2 channels: full" in report
    assert "- [x] Accept v2" not in report
    assert "- [ ] Accept v2" in report
    assert "Reviewed v2 output regressed" in report


def test_command_check_rejects_regression_even_with_unchanged_difference_ids(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    results = audit_all()
    regressed = tuple(
        replace(result, facade=replace(result.facade, full="regression"))
        if result.case.key == "default-cl3/lie-bracket"
        else result
        for result in results
    )
    assert difference_keys(regressed) == frozenset(DIFFERENCE_LEDGER)
    monkeypatch.setattr(audit_rendering_parity, "audit_all", lambda: regressed)

    assert audit_rendering_parity.main(["--output", str(tmp_path / "report.md"), "--check"]) == 1
    assert "Reviewed facade regression: default-cl3/lie-bracket (full)" in capsys.readouterr().out


@pytest.mark.parametrize("cases", (CASES[:-1], (*CASES, CASES[0])))
def test_command_check_rejects_removed_or_duplicate_cases(
    cases: tuple[RenderingCase, ...], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(audit_rendering_parity, "CASES", cases)

    assert audit_rendering_parity.main(["--output", str(tmp_path / "report.md"), "--check"]) == 1


def test_command_check_rejects_removing_a_captured_operation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(audit_rendering_parity, "OPERATIONS", {})

    assert audit_rendering_parity.main(["--output", str(tmp_path / "report.md"), "--check"]) == 1


@pytest.mark.parametrize("check", (False, True))
def test_command_writes_a_passing_review_report(tmp_path: Path, check: bool) -> None:
    report_path = tmp_path / "report.md"
    arguments = ["--output", str(report_path)]
    if check:
        arguments.append("--check")

    assert audit_rendering_parity.main(arguments) == 0
    assert "| Reviewed facade regressions | 0 |" in report_path.read_text()


@pytest.mark.parametrize(
    "ledger, message",
    (
        ({}, "Unclassified differences:"),
        ({**DIFFERENCE_LEDGER, "stale-entry": "old reason"}, "Ledgered differences no longer observed: stale-entry"),
    ),
)
def test_command_still_requires_exact_difference_ledger(
    ledger: dict[str, str],
    message: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(audit_rendering_parity, "DIFFERENCE_LEDGER", ledger)

    assert audit_rendering_parity.main(["--output", str(tmp_path / "report.md"), "--check"]) == 1
    assert message in capsys.readouterr().out


def test_command_runs_in_a_fresh_process_with_all_legacy_imports_blocked(tmp_path: Path) -> None:
    program = """
import importlib.abc
import sys

blocked = {
    'galaga.legacy', 'galaga.algebra', 'galaga.basis_blade', 'galaga.blade_convention',
    'galaga.expr', 'galaga.latex_build', 'galaga.latex_emit', 'galaga.latex_nodes',
    'galaga.latex_rewrite', 'galaga.lazy', 'galaga.notation', 'galaga.ops', 'galaga.symbolic',
}

class RejectLegacy(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if any(fullname == name or fullname.startswith(name + '.') for name in blocked):
            raise AssertionError('rendering audit imported legacy module: ' + fullname)

sys.meta_path.insert(0, RejectLegacy())
from tools.audit_rendering_parity import main
assert main(['--output', sys.argv[1], '--check']) == 0
assert not blocked.intersection(sys.modules)
"""
    report_path = tmp_path / "without-legacy.md"
    completed = subprocess.run(
        [sys.executable, "-c", program, str(report_path)],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert (
        f"Audited {len(CASES)} expressions: {len(CASES) - len(DIFFERENCE_LEDGER)} succeeded, "
        f"{len(DIFFERENCE_LEDGER)} differed"
    ) in completed.stdout
    assert "Every facade result matches its reviewed v2 baseline" in report_path.read_text()
