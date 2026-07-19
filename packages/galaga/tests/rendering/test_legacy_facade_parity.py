"""Executable differential contract for the retained v1 and v2 renderers."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from tools.rendering_parity import (
    CASES,
    DIFFERENCE_LEDGER,
    audit_case,
    covered_operations,
    difference_keys,
    render_markdown_report,
    required_shared_operations,
)


def test_case_registry_has_unique_stable_keys() -> None:
    keys = tuple(case.key for case in CASES)

    assert len(keys) == len(set(keys))


def test_every_shared_registered_expression_operation_has_a_case() -> None:
    assert required_shared_operations() <= covered_operations()


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.key)
def test_reviewed_latex_parity(case: object) -> None:
    result = audit_case(case)  # type: ignore[arg-type]
    ledgered = result.case.key in DIFFERENCE_LEDGER

    assert result.succeeded is not ledgered, (
        f"{result.case.key}: {'remove resolved ledger entry' if ledgered else 'classify new difference'}; "
        f"differences={result.differences!r}"
    )


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
    assert report.count("#### Rendered Expression (v1 vs v2)") == failure_count
    assert report.count("#### Emitted Latex (v1 vs v2)") == failure_count
    assert ("\\" * 5) + "\n" in report
    assert "```latex" in report
    assert "<details>" not in report
    assert "- [x] Accept v2" in report
    assert "- [ ] Match legacy v1" in report
    assert "> Accepted Galaga 2 correction:" in report
