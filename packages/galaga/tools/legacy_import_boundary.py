"""Test-only import boundary for the retired Galaga 1 module tree.

Unlike constructor poisoning, this guard never imports the code it rejects.
It is a regression aid, not a security boundary against arbitrary Python.
"""

from __future__ import annotations

import sys
from collections.abc import Mapping, Sequence
from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec
from types import ModuleType

# Root prefixes cover the retired engine and migration-only bridge inventory.
LEGACY_ROOTS = frozenset(
    {
        "galaga.algebra",
        "galaga.basis_blade",
        "galaga.blade_convention",
        "galaga.expr",
        "galaga.gram_bridge",
        "galaga.latex_build",
        "galaga.latex_emit",
        "galaga.latex_nodes",
        "galaga.latex_rewrite",
        "galaga.latex_symbols",
        "galaga.lazy",
        "galaga.legacy",
        "galaga.notation",
        "galaga.ops",
        "galaga.symbolic",
        "galaga.symbolic_core",
    }
)
_LEGACY_PREFIXES = tuple(root + "." for root in sorted(LEGACY_ROOTS))


class LegacyImportError(AssertionError):
    """A retired import was attempted or was already cached.

    Deliberately not ImportError: optional-import fallbacks must not hide an
    accidental dependency on code scheduled for deletion.
    """


def is_legacy_module(name: str) -> bool:
    return name in LEGACY_ROOTS or name.startswith(_LEGACY_PREFIXES)


def assert_no_legacy_modules(modules: Mapping[str, object] | None = None) -> None:
    """Reject cached modules too, since Python can bypass meta-path finders."""
    names = tuple(sys.modules if modules is None else modules)
    loaded = sorted(name for name in names if name.startswith("galaga.") and is_legacy_module(name))
    if loaded:
        raise LegacyImportError(f"retired Galaga modules already loaded: {', '.join(loaded)}")


class LegacyImportGuard(MetaPathFinder):
    def find_spec(
        self, fullname: str, path: Sequence[str] | None = None, target: ModuleType | None = None
    ) -> ModuleSpec | None:
        if is_legacy_module(fullname):
            raise LegacyImportError(f"retired Galaga import: {fullname}; use the public Galaga 2 API")
        return None


def install_import_guard() -> LegacyImportGuard:
    """Install a fresh finder without discarding preloaded modules."""
    assert_no_legacy_modules()
    guard = LegacyImportGuard()
    sys.meta_path.insert(0, guard)
    return guard


def remove_import_guard(guard: LegacyImportGuard) -> None:
    """Remove only this installation, preserving other finders and guards."""
    if guard in sys.meta_path:
        sys.meta_path.remove(guard)
