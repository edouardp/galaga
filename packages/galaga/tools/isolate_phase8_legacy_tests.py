"""Isolate retained Galaga 1 tests behind the explicit legacy namespace.

The file list is both an executable migration ledger and a write guard.  The
codemod changes only real ``from galaga import ...`` statements; comments,
strings, and imports from more specific Galaga modules remain untouched.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

import libcst as cst
from libcst.helpers import get_full_name_for_node

LEGACY_ORACLE_TESTS = (
    "test_blade_convention.py",
    "test_chisolm_transformations.py",
    "test_coverage.py",
    "test_coverage_gaps.py",
    "test_display_order.py",
    "test_latex_build.py",
    "test_latex_symbols.py",
    "test_locals.py",
    "test_low_dim.py",
    "test_notation.py",
    "test_numeric_formatting.py",
    "test_numeric_function_expressions.py",
    "test_precedence.py",
    "test_quaternion.py",
    "test_redesign.py",
    "test_render.py",
    "test_rga_convention_layer.py",
    "test_scalar_helpers.py",
    "test_symbolic.py",
    "facade/test_numeric_contract.py",
    "rendering/test_compound_latex_contract.py",
    "rendering/test_legacy_facade_parity.py",
    "rendering/test_rga_latex_contract.py",
    "rendering/test_sta_latex_contract.py",
)

_LEGACY_ORACLE_TEST_SET = frozenset(LEGACY_ORACLE_TESTS)


class _UseExplicitLegacyNamespace(cst.CSTTransformer):
    def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) -> cst.ImportFrom:
        if get_full_name_for_node(original_node.module) != "galaga":
            return updated_node
        return updated_node.with_changes(module=cst.parse_expression("galaga.legacy"))


def isolate_source(source: str) -> str:
    """Return source with actual top-level Galaga imports made explicitly v1."""
    return cst.parse_module(source).visit(_UseExplicitLegacyNamespace()).code


def isolate_path(path: Path, *, tests_root: Path, check: bool) -> bool:
    """Rewrite one ledgered test and return whether its source differs."""
    resolved_root = tests_root.resolve()
    resolved_path = path.resolve()
    try:
        relative = resolved_path.relative_to(resolved_root).as_posix()
    except ValueError as error:
        raise ValueError(f"test path is outside {resolved_root}: {resolved_path}") from error
    if relative not in _LEGACY_ORACLE_TEST_SET:
        raise ValueError(f"test is not in the Phase 8 legacy-oracle ledger: {relative}")

    source = resolved_path.read_text()
    isolated = isolate_source(source)
    changed = isolated != source
    if changed and not check:
        resolved_path.write_text(isolated)
    return changed


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--check", action="store_true", help="fail if a ledgered test still needs rewriting")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    tests_root = args.repository / "packages/galaga/tests"
    changed = [
        relative
        for relative in LEGACY_ORACLE_TESTS
        if isolate_path(tests_root / relative, tests_root=tests_root, check=args.check)
    ]
    if args.check and changed:
        print("Phase 8 legacy test imports require isolation:")
        for relative in changed:
            print(f"- {relative}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
