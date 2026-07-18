"""Canonicalize approved operation imports in migrated ``galaga.core`` tests.

The codemod uses LibCST qualified-name metadata. It rewrites only references
that resolve to an approved aliased import from ``galaga.core``; strings,
comments, unrelated local names, and convention-sensitive operations are left
untouched.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

import libcst as cst
from libcst import metadata
from libcst.helpers import get_full_name_for_node

APPROVED_IMPORT_ALIASES = {
    ("geometric_product", "gp"),
    ("grade_involution", "involute"),
    ("outer_product", "op"),
}

CANONICAL_QUALIFIED_NAMES = {f"galaga.core.{canonical}": canonical for canonical, _alias in APPROVED_IMPORT_ALIASES}


class _CanonicalizeOperations(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (
        metadata.ParentNodeProvider,
        metadata.QualifiedNameProvider,
    )

    def leave_Name(
        self,
        original_node: cst.Name,
        updated_node: cst.Name,
    ) -> cst.Name:
        parent = self.get_metadata(metadata.ParentNodeProvider, original_node)
        if isinstance(parent, (cst.AsName, cst.ImportAlias)):
            return updated_node

        qualified_names = self.get_metadata(
            metadata.QualifiedNameProvider,
            original_node,
            set(),
        )
        canonical_names = {
            CANONICAL_QUALIFIED_NAMES[qualified_name.name]
            for qualified_name in qualified_names
            if qualified_name.source is metadata.QualifiedNameSource.IMPORT
            and qualified_name.name in CANONICAL_QUALIFIED_NAMES
        }
        if not canonical_names:
            return updated_node
        if len(canonical_names) != 1:
            names = ", ".join(sorted(canonical_names))
            raise ValueError(f"ambiguous canonical operation names: {names}")
        return updated_node.with_changes(value=canonical_names.pop())

    def leave_ImportFrom(
        self,
        original_node: cst.ImportFrom,
        updated_node: cst.ImportFrom,
    ) -> cst.ImportFrom:
        if get_full_name_for_node(original_node.module) != "galaga.core":
            return updated_node
        if isinstance(original_node.names, cst.ImportStar) or isinstance(updated_node.names, cst.ImportStar):
            return updated_node

        updated_aliases: list[cst.ImportAlias] = []
        for original_alias, updated_alias in zip(original_node.names, updated_node.names, strict=True):
            imported_name = get_full_name_for_node(original_alias.name)
            local_name = (
                original_alias.asname.name.value
                if original_alias.asname is not None and isinstance(original_alias.asname.name, cst.Name)
                else None
            )
            if (imported_name, local_name) in APPROVED_IMPORT_ALIASES:
                updated_alias = updated_alias.with_changes(asname=None)
            updated_aliases.append(updated_alias)

        return updated_node.with_changes(names=tuple(updated_aliases))


def canonicalize_source(source: str) -> str:
    """Return ``source`` with approved core operation aliases canonicalized."""
    module = cst.parse_module(source)
    wrapper = metadata.MetadataWrapper(module)
    return wrapper.visit(_CanonicalizeOperations()).code


def _is_core_test(path: Path) -> bool:
    parts = path.resolve().parts
    expected = ("packages", "galaga", "tests", "core")
    return any(parts[index : index + len(expected)] == expected for index in range(len(parts) - len(expected) + 1))


def canonicalize_path(path: Path, *, check: bool) -> bool:
    """Canonicalize one core test and return whether it required a change."""
    if not _is_core_test(path):
        raise ValueError(f"refusing to rewrite a file outside packages/galaga/tests/core: {path}")
    source = path.read_text()
    canonical = canonicalize_source(source)
    changed = source != canonical
    if changed and not check:
        path.write_text(canonical)
    return changed


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="report changes without writing them")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args(argv)

    changed = [path for path in args.paths if canonicalize_path(path, check=args.check)]
    for path in changed:
        print(path)
    return int(args.check and bool(changed))


if __name__ == "__main__":
    raise SystemExit(main())
