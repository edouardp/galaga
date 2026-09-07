"""The compatibility contract must survive removal of the v1 implementation."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

import galaga
import galaga.facade as facade

from . import test_v1_surface_manifest as contract
from . import v1_surface_manifest as manifest


@pytest.mark.parametrize("surface", tuple(contract.HISTORICAL_SURFACES))
@pytest.mark.parametrize("change", ("missing", "invented"))
def test_historical_contract_rejects_missing_and_invented_dispositions(
    surface: str, change: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    changed = set(contract.HISTORICAL_SURFACES[surface])
    if change == "missing":
        changed.remove(sorted(changed)[0])
    else:
        changed.add("invented_v1_name")
    monkeypatch.setitem(contract.HISTORICAL_SURFACES, surface, changed)

    with pytest.raises(AssertionError, match="historical disposition mismatch"):
        contract.test_every_observed_v1_name_has_exactly_one_disposition(surface)


@pytest.mark.parametrize(
    "observed, message",
    (
        (None, "nonempty list"),
        ("Algebra", "nonempty list"),
        ([], "nonempty list"),
        (["Algebra", "Algebra"], "duplicate observation"),
        ([None], "invalid name"),
        ([["Algebra"]], "invalid name"),
        ([""], "invalid name"),
    ),
)
def test_historical_comparison_rejects_malformed_or_duplicate_observations(observed, message: str) -> None:
    with pytest.raises(AssertionError, match=message):
        contract._assert_classified_names(observed, {"Algebra"}, label="intentional corruption")


@pytest.mark.parametrize("field, value", (("schema_version", 2), ("source_commit", "unknown"), ("python", "unknown")))
def test_archive_provenance_cannot_silently_change(field: str, value, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(contract.BASELINE, field, value)

    with pytest.raises(AssertionError):
        contract.test_historical_surface_archive_preserves_capture_provenance_and_completeness()


def test_disposition_merge_rejects_duplicate_ownership() -> None:
    row = manifest.TOP_LEVEL_EXPORTS["Algebra"]
    with pytest.raises(RuntimeError, match="duplicate v1 surface classification"):
        manifest._merge({"Algebra": row}, {"Algebra": row})


@pytest.mark.parametrize("name", ("__add__", "__pos__", "_repr_latex_"))
def test_current_protocol_and_rendering_regressions_are_not_hidden_by_history(
    name: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delattr(facade.Multivector, name)

    with pytest.raises(AssertionError):
        contract.test_v2_protocol_and_formatting_hooks_remain_live_contracts()


def test_current_namespace_identity_regression_is_not_hidden_by_history(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(galaga, "Algebra", object())

    with pytest.raises(AssertionError):
        contract.test_top_level_v2_exports_are_owned_by_the_facade()


@pytest.mark.parametrize("change", ("missing", "overlapping", "unclassified"))
def test_module_partition_rejects_gaps_overlaps_and_unclassified_entry_points(
    change: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    supported = dict(contract.SUPPORTED_SUBMODULES)
    if change == "missing":
        supported.pop("galaga.names")
    elif change == "overlapping":
        supported["galaga.algebra"] = contract.SUBMODULE_DISPOSITIONS["galaga.algebra"]
    else:
        supported["galaga.unclassified"] = supported["galaga.names"]
    monkeypatch.setattr(contract, "SUPPORTED_SUBMODULES", supported)

    with pytest.raises(AssertionError):
        contract.test_current_entry_points_and_legacy_only_modules_form_an_explicit_partition()


@pytest.mark.parametrize("kind", ("file", "package"))
def test_live_package_inventory_rejects_new_and_missing_unclassified_modules(
    kind: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(contract, "TOP_LEVEL_PACKAGE_MODULES", frozenset({"galaga.names"}))
    with pytest.raises(AssertionError):
        contract._assert_current_module_inventory(tmp_path)

    (tmp_path / "names.py").touch()
    contract._assert_current_module_inventory(tmp_path)
    if kind == "file":
        (tmp_path / "unclassified.py").touch()
    else:
        (tmp_path / "unclassified").mkdir()
        (tmp_path / "unclassified/__init__.py").touch()
    with pytest.raises(AssertionError):
        contract._assert_current_module_inventory(tmp_path)


def test_surface_and_deprecation_contracts_execute_with_all_legacy_imports_forbidden() -> None:
    program = """
import importlib.abc
import sys

legacy_roots = {
    'galaga.algebra', 'galaga.basis_blade', 'galaga.blade_convention',
    'galaga.expr', 'galaga.latex_build', 'galaga.latex_emit',
    'galaga.latex_nodes', 'galaga.latex_rewrite', 'galaga.latex_symbols',
    'galaga.lazy', 'galaga.legacy', 'galaga.notation', 'galaga.ops',
    'galaga.symbolic', 'galaga.symbolic_core',
}
def is_legacy(fullname):
    return any(fullname == root or fullname.startswith(root + '.') for root in legacy_roots)

class RejectLegacy(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if is_legacy(fullname):
            raise AssertionError('compatibility contract imported legacy module: ' + fullname)

sys.meta_path.insert(0, RejectLegacy())
import pytest
# Replace the ordinary parent's constructor-poisoning fixture with this
# stronger import prohibition; run the real contract tests unchanged.
result = pytest.main(['--noconftest', '-q', *sys.argv[1:]])
assert result == 0
assert not any(is_legacy(name) for name in sys.modules)
"""
    directory = Path(__file__).parent
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            program,
            str(directory / "test_v1_surface_manifest.py"),
            str(directory / "test_v2_deprecations.py"),
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
