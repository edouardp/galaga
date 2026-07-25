"""Remove repository import-path bootstraps from Marimo notebooks.

Local source selection belongs to the process that launches Marimo.  Keeping
that concern out of notebook cells lets the same source run from a repository
checkout, an installed wheel, or a copied standalone notebook.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

import libcst as cst
from libcst.helpers import get_full_name_for_node

_MARIMO_APP_MARKER = "app = marimo.App"


def _is_marimo_cell(node: cst.FunctionDef) -> bool:
    for decorator in node.decorators:
        expression = decorator.decorator
        if isinstance(expression, cst.Call):
            expression = expression.func
        if get_full_name_for_node(expression) == "app.cell":
            return True
    return False


class _PathMutationFinder(cst.CSTVisitor):
    def __init__(self) -> None:
        self.found = False

    def visit_Call(self, node: cst.Call) -> None:
        if get_full_name_for_node(node.func) == "sys.path.insert":
            self.found = True


class _RemoveRepositoryPathCells(cst.CSTTransformer):
    def leave_FunctionDef(
        self,
        original_node: cst.FunctionDef,
        updated_node: cst.FunctionDef,
    ) -> cst.FunctionDef | cst.RemovalSentinel:
        if not _is_marimo_cell(original_node):
            return updated_node

        finder = _PathMutationFinder()
        original_node.visit(finder)
        if finder.found:
            return cst.RemoveFromParent()
        return updated_node


def make_notebook_portable(source: str) -> str:
    """Return Marimo source with repository path-mutation cells removed."""
    if _MARIMO_APP_MARKER not in source:
        return source
    return cst.parse_module(source).visit(_RemoveRepositoryPathCells()).code


def _example_path(path: Path, *, repository: Path) -> Path:
    examples = (repository / "examples").resolve()
    resolved = path.resolve()
    try:
        resolved.relative_to(examples)
    except ValueError as error:
        raise ValueError(f"refusing to rewrite a file outside {examples}: {path}") from error
    return resolved


def make_path_portable(path: Path, *, repository: Path, check: bool) -> bool:
    """Remove a path bootstrap and return whether the notebook required a change."""
    resolved = _example_path(path, repository=repository)
    source = resolved.read_text()
    if _MARIMO_APP_MARKER not in source:
        raise ValueError(f"refusing to rewrite a non-Marimo example: {path}")

    portable = make_notebook_portable(source)
    changed = portable != source
    if changed and not check:
        resolved.write_text(portable)
    return changed


def _marimo_notebooks(repository: Path) -> list[Path]:
    examples = repository / "examples"
    return sorted(path for path in examples.rglob("*.py") if _MARIMO_APP_MARKER in path.read_text())


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--check", action="store_true")
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args(argv)

    paths = args.paths or _marimo_notebooks(args.repository)
    changed = [path for path in paths if make_path_portable(path, repository=args.repository, check=args.check)]
    for path in changed:
        print(path)
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
