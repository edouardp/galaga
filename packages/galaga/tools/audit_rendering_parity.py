"""Write a reviewable v1/v2 LaTeX rendering parity report."""

from __future__ import annotations

import argparse
from pathlib import Path

from .rendering_parity import (
    DIFFERENCE_LEDGER,
    audit_all,
    default_report_path,
    difference_keys,
    write_markdown_report,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail unless the observed difference IDs exactly match the reviewed ledger",
    )
    arguments = parser.parse_args(argv)
    repository = arguments.repository.resolve()
    output = arguments.output or default_report_path(repository)
    results = audit_all()
    written = write_markdown_report(results, output, repository=repository)
    observed = difference_keys(results)
    expected = frozenset(DIFFERENCE_LEDGER)
    print(f"Wrote {written}")
    print(f"Audited {len(results)} expressions: {len(results) - len(observed)} succeeded, {len(observed)} differed")
    if arguments.check and observed != expected:
        unexpected = sorted(observed - expected)
        resolved = sorted(expected - observed)
        if unexpected:
            print(f"Unclassified differences: {', '.join(unexpected)}")
        if resolved:
            print(f"Ledgered differences no longer observed: {', '.join(resolved)}")
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - command-line entry point
    raise SystemExit(main())
