"""Compare live facade rendering with frozen v1 and reviewed v2 observations."""

from __future__ import annotations

import argparse
from pathlib import Path

from galaga.facade.catalog import OPERATIONS

from .rendering_parity import (
    BASELINE,
    CASES,
    DIFFERENCE_LEDGER,
    audit_all,
    covered_operations,
    default_report_path,
    difference_keys,
    required_shared_operations,
    reviewed_facade_differences,
    write_markdown_report,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--check",
        action="store_true",
        help="require the reviewed difference ledger, pinned v2 outputs, and complete case/operation coverage",
    )
    arguments = parser.parse_args(argv)
    if arguments.check:
        keys = tuple(case.key for case in CASES)
        if len(keys) != len(set(keys)) or set(keys) != set(BASELINE.cases):
            print("Rendering case inventory differs from the frozen baseline")
            return 1
        if not required_shared_operations() <= (covered_operations() & set(OPERATIONS)):
            print("Captured shared rendering operations are missing from the cases or facade catalog")
            return 1
    repository = arguments.repository.resolve()
    output = arguments.output or default_report_path(repository)
    results = audit_all()
    written = write_markdown_report(results, output, repository=repository)
    observed = difference_keys(results)
    expected = frozenset(DIFFERENCE_LEDGER)
    regressions = {result.case.key: reviewed_facade_differences(result) for result in results}
    regressions = {key: channels for key, channels in regressions.items() if channels}
    print(f"Wrote {written}")
    print(f"Audited {len(results)} expressions: {len(results) - len(observed)} succeeded, {len(observed)} differed")
    if arguments.check and (observed != expected or regressions):
        unexpected = sorted(observed - expected)
        resolved = sorted(expected - observed)
        if unexpected:
            print(f"Unclassified differences: {', '.join(unexpected)}")
        if resolved:
            print(f"Ledgered differences no longer observed: {', '.join(resolved)}")
        for key, channels in regressions.items():
            print(f"Reviewed facade regression: {key} ({', '.join(channels)})")
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - command-line entry point
    raise SystemExit(main())
