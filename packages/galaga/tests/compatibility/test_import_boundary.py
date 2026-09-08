"""Positive/negative controls for the deletion-ready test import boundary."""

import ast
import copy
import hashlib
import importlib
import json
import runpy
import subprocess
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import numpy as np
import pytest

import galaga as ga
from tools import legacy_import_boundary as boundary

TEST_ROOT = Path(__file__).parents[1]
ARCHIVE = json.loads((TEST_ROOT.parent / "tools/baselines/namespace-boundaries-v1.json").read_text())
MANIFEST = runpy.run_path(str(Path(__file__).with_name("v1_surface_manifest.py")))
RENAMED = {
    "test_explicit_legacy_namespace_preserves_a_coherent_v1_domain": "test_public_values_use_only_the_owned_core_domain",
    "test_unledgered_tests_poison_legacy_construction": "test_retired_imports_fail_before_numeric_construction",
    "test_v1_and_v2_values_do_not_mix_implicitly": "test_foreign_value_domains_do_not_mix_implicitly",
    "test_explicit_v1_numeric_aliases_remain_the_same_function_objects": "test_archived_v1_aliases_do_not_define_the_public_v2_catalog",
    "test_legacy_numeric_constructor_guard_is_active": "test_numeric_values_use_core_storage_without_importing_legacy",
}


def check_source_ownership(sources):
    count = 0
    for path, row in sources.items():
        assert hashlib.sha256(row["source"].encode()).hexdigest() == row["sha256"]
        historical = [
            node.name
            for node in ast.parse(row["source"]).body
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        ]
        assert historical == row["test_ids"]
        current = {
            node.name
            for node in ast.parse((TEST_ROOT / path).read_text()).body
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        }
        for name in historical:
            assert RENAMED.get(name, name) in current, (path, name)
        count += len(historical)
    assert count == 29


def test_namespace_and_symbolic_source_evidence_retains_every_public_owner():
    assert ARCHIVE["schema_version"] == 1
    assert ARCHIVE["source_commit"] == "0499fa49800950503467cac60eb9d199231458c0"
    assert ARCHIVE["captured_on"] == "2026-09-08"
    assert ARCHIVE["python"] == "3.14.4" and ARCHIVE["numpy"] == "2.5.2"
    assert len(ARCHIVE["sources"]) == 7
    check_source_ownership(ARCHIVE["sources"])
    legacy = ARCHIVE["legacy_domain"]
    assert legacy["algebra_module"] == legacy["multivector_module"] == "galaga.algebra"
    algebra = ga.Algebra(2)
    a, b = algebra.basis_vectors()
    np.testing.assert_array_equal([a.data, b.data], legacy["basis"])
    np.testing.assert_array_equal((a * b).data, legacy["product"])
    assert a * b == algebra.blade(3) and b * a == -algebra.blade(3)
    assert legacy["mixed_error"]["type"] == "TypeError"
    assert ARCHIVE["arithmetic"] == {"add": 6, "scalar_multiply": 12, "scalar_divide": 2}
    assert ARCHIVE["domain"]["registered_product"] == 2 * 5


@pytest.mark.parametrize("corruption", ("source", "identity", "owner", "missing_file"))
def test_source_ownership_rejects_corruption_and_unowned_historical_tests(corruption, monkeypatch):
    sources = copy.deepcopy(ARCHIVE["sources"])
    row = sources["test_symbolic_core.py"]
    if corruption == "source":
        row["source"] += "\n# changed"
    elif corruption == "identity":
        row["test_ids"].pop()
    elif corruption == "owner":
        monkeypatch.setitem(RENAMED, row["test_ids"][0], "test_missing")
    else:
        del sources["test_symbolic_core.py"]
    with pytest.raises(AssertionError):
        check_source_ownership(sources)


def test_guard_roots_cover_the_complete_retirement_inventory_without_v2_false_positives():
    legacy = MANIFEST["LEGACY_ONLY_SUBMODULES"]
    roots = {name for name in legacy if not any(name.startswith(other + ".") for other in legacy)}
    assert roots == boundary.LEGACY_ROOTS
    assert all(boundary.is_legacy_module(name) for name in legacy)
    assert not any(boundary.is_legacy_module(name) for name in MANIFEST["SUPPORTED_SUBMODULES"])
    boundary.assert_no_legacy_modules()


def test_tests_and_test_tools_have_no_direct_retired_imports_even_in_inactive_scopes():
    architecture = runpy.run_path(str(TEST_ROOT / "facade/test_architecture_contracts.py"))
    for root, package in ((TEST_ROOT, "tests"), (TEST_ROOT.parent / "tools", "tools")):
        for module, owner, source in architecture["python_sources"](root, package):
            forbidden = [
                (line, name)
                for line, name in architecture["galaga_imports"](source, owner)
                if boundary.is_legacy_module(name)
            ]
            assert not forbidden, (module, forbidden)


@pytest.mark.parametrize("root", sorted(boundary.LEGACY_ROOTS))
@pytest.mark.parametrize("suffix", ("", ".nested"))
def test_finder_rejects_retired_roots_and_descendants_before_loading(root, suffix):
    with pytest.raises(boundary.LegacyImportError, match="retired Galaga import"):
        boundary.LegacyImportGuard().find_spec(root + suffix)
    assert not issubclass(boundary.LegacyImportError, ImportError)


@pytest.mark.parametrize(
    "name",
    (
        "galaga",
        "galaga.core",
        "galaga.expression",
        "galaga.names",
        "galaga._latex_symbols",
        "galaga.facade",
        "galaga.gram_bridge",
        "galaga.legacy_notes",
        "galaga.symbolic_core_extra",
        "other.galaga.legacy",
    ),
)
def test_finder_passes_unrelated_and_live_modules_to_the_next_loader(name):
    assert not boundary.is_legacy_module(name)
    assert boundary.LegacyImportGuard().find_spec(name, [], ModuleType(name)) is None
    boundary.assert_no_legacy_modules({name: None})


@pytest.mark.parametrize("name", ("galaga.legacy", "galaga.symbolic_core.expr"))
@pytest.mark.parametrize("value", (None, object()))
def test_cache_checks_reject_preloaded_modules_including_failed_import_sentinels(name, value):
    modules = {name: value, "galaga.core": object()}
    with pytest.raises(boundary.LegacyImportError, match="already loaded"):
        boundary.assert_no_legacy_modules(modules)
    assert modules[name] is value  # Detection must not evict or rewrite user state.
    boundary.assert_no_legacy_modules({})


def test_installation_precedes_other_finders_and_cleanup_removes_only_its_own_guard(monkeypatch):
    before = list(sys.meta_path)
    calls = []

    class Probe:
        def find_spec(self, fullname, path=None, target=None):
            calls.append(fullname)
            raise AssertionError("reached a later finder")

    monkeypatch.setattr(sys, "meta_path", [Probe(), *before])
    guard = boundary.install_import_guard()
    try:
        assert sys.meta_path[0] is guard
        with pytest.raises(boundary.LegacyImportError):
            importlib.import_module("galaga.legacy")
        assert calls == []
        with pytest.raises(AssertionError, match="reached a later finder"):
            importlib.import_module("not_a_galaga_test_module")
        assert calls == ["not_a_galaga_test_module"]
    finally:
        boundary.remove_import_guard(guard)
    assert sys.meta_path[1:] == before
    boundary.remove_import_guard(guard)
    assert sys.meta_path[1:] == before


def test_installation_refuses_a_cached_module_without_mutating_the_cache_or_finders(monkeypatch):
    before = list(sys.meta_path)
    fake = ModuleType("galaga.legacy")
    with monkeypatch.context() as patch:
        patch.setitem(sys.modules, "galaga.legacy", fake)
        with pytest.raises(boundary.LegacyImportError, match="already loaded"):
            boundary.install_import_guard()
        assert sys.modules["galaga.legacy"] is fake and sys.meta_path == before
    boundary.assert_no_legacy_modules()


def test_pytest_hooks_install_clean_up_and_reject_retired_markers_or_ledger_entries(monkeypatch):
    hooks = runpy.run_path(str(TEST_ROOT / "conftest.py"))
    cleanups, markers = [], []
    config = SimpleNamespace(add_cleanup=cleanups.append, addinivalue_line=lambda *args: markers.append(args))
    before = list(sys.meta_path)
    hooks["pytest_configure"](config)
    assert len(sys.meta_path) == len(before) + 1 and len(cleanups) == 1 and markers
    cleanups[0]()
    assert sys.meta_path == before
    plain = SimpleNamespace(nodeid="plain", get_closest_marker=lambda name: None)
    marked = SimpleNamespace(nodeid="marked", get_closest_marker=lambda name: True)
    hooks["pytest_collection_modifyitems"]([plain])
    with pytest.raises(pytest.UsageError, match="markers are retired"):
        hooks["pytest_collection_modifyitems"]([marked])
    globals_ = hooks["pytest_configure"].__globals__
    monkeypatch.setitem(globals_, "LEGACY_ORACLE_TESTS", ("test_old.py",))
    with pytest.raises(pytest.UsageError, match="empty legacy-construction ledger"):
        hooks["pytest_configure"](config)
    hooks["pytest_collection_finish"](None)
    hooks["pytest_sessionfinish"](None, 0)
    fixture = hooks["reject_cached_legacy_modules"].__wrapped__()
    next(fixture)
    with pytest.raises(StopIteration):
        next(fixture)


FAILURES = {
    "collection": ("import galaga.legacy\n", "retired Galaga import"),
    "call": ("def test_probe():\n    import galaga.algebra\n", "retired Galaga import"),
    "fixture_setup": (
        "import pytest\n@pytest.fixture(autouse=True)\ndef fixture():\n    import galaga.legacy\n"
        "def test_probe(): pass\n",
        "retired Galaga import",
    ),
    "fixture_teardown": (
        "import pytest\n@pytest.fixture(autouse=True)\ndef fixture():\n    yield\n    import galaga.legacy\n"
        "def test_probe(): pass\n",
        "retired Galaga import",
    ),
    "optional_fallback": (
        "def test_probe():\n    try:\n        import galaga.legacy\n    except ImportError:\n        pass\n",
        "retired Galaga import",
    ),
    "function_marker": (
        "import pytest\n@pytest.mark.legacy_oracle\ndef test_probe(): pass\n",
        "markers are retired",
    ),
    "module_marker": (
        "import pytest\npytestmark = pytest.mark.legacy_oracle\ndef test_probe(): pass\n",
        "markers are retired",
    ),
    "cached_collection": (
        "import sys\nsys.modules['galaga.legacy'] = None\ndef test_probe(): pass\n",
        "already loaded",
    ),
    "cached_call": (
        "def test_probe():\n    import sys\n    sys.modules['galaga.legacy'] = None\n",
        "already loaded",
    ),
    "cached_session_fixture": (
        "import pytest\n@pytest.fixture(scope='session', autouse=True)\ndef fixture():\n"
        "    yield\n    import sys\n    sys.modules['galaga.legacy'] = None\n"
        "def test_probe(): pass\n",
        "already loaded",
    ),
}


def run_isolated_pytest(tmp_path, source, *, suffix=""):
    (tmp_path / "conftest.py").write_text((TEST_ROOT / "conftest.py").read_text() + suffix)
    (tmp_path / "test_probe.py").write_text(source)
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-c",
            "/dev/null",
            "-p",
            "no:cacheprovider",
            "--confcutdir",
            str(tmp_path),
            "-q",
            "--tb=short",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


@pytest.mark.parametrize("case", FAILURES)
def test_real_pytest_rejects_legacy_dependencies_at_every_lifecycle_stage(tmp_path, case):
    source, message = FAILURES[case]
    result = run_isolated_pytest(tmp_path, source)
    assert result.returncode != 0
    assert message in result.stdout + result.stderr, result.stdout + result.stderr


@pytest.mark.parametrize(
    "suffix, message",
    (
        ("\nimport sys\nsys.modules['galaga.legacy'] = None\n", "already loaded"),
        ("\nLEGACY_ORACLE_TESTS = ('test_probe.py',)\n", "empty legacy-construction ledger"),
    ),
)
def test_real_pytest_refuses_preloaded_modules_and_new_construction_exemptions(tmp_path, suffix, message):
    result = run_isolated_pytest(tmp_path, "def test_probe(): pass\n", suffix=suffix)
    assert result.returncode != 0 and message in result.stdout + result.stderr


def test_real_pytest_accepts_public_core_facade_and_bridge_values_without_legacy(tmp_path):
    source = """
import galaga as ga
import galaga.core as core
import galaga.facade as facade
import galaga.gram_bridge as bridge
from tools.legacy_import_boundary import assert_no_legacy_modules
def test_probe():
    assert ga.Algebra is bridge.Algebra is facade.Algebra
    algebra = ga.Algebra(gram=((2, 0.5), (0.5, -1)))
    a, b = algebra.basis_vectors()
    assert isinstance(a.numeric, core.Multivector)
    assert a * b + b * a == 2 * algebra.gram[0, 1]
    result = a.named('a') * b.named('b')
    assert ga.evaluate(result.expr, algebra=algebra, environment={'a': a, 'b': b}) == a * b
    assert_no_legacy_modules()
"""
    result = run_isolated_pytest(tmp_path, source)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    "source",
    (
        "import galaga.legacy",
        "def later():\n    from .. import algebra",
        "if TYPE_CHECKING:\n    from ..symbolic_core import Sym",
        "class Nested:\n    from ..latex_symbols import LatexSymbols",
    ),
)
def test_facade_source_guard_detects_retired_imports_in_every_scope(source, monkeypatch):
    contract = runpy.run_path(str(Path(__file__).with_name("test_facade_namespace.py")))
    monkeypatch.setitem(
        contract["ARCHITECTURE"],
        "python_sources",
        lambda root, package: iter([("galaga.facade.probe", "galaga.facade", source)]),
    )
    with pytest.raises(AssertionError):
        contract["test_facade_implementation_has_no_outer_layer_imports"]()


@pytest.mark.parametrize("attribute", ("_mul_sign", "_mul_index"))
def test_facade_private_table_guard_detects_spaced_attribute_access(attribute, monkeypatch):
    contract = runpy.run_path(str(Path(__file__).with_name("test_facade_namespace.py")))
    source = f"def later(value):\n    return value . {attribute}"
    monkeypatch.setitem(
        contract["ARCHITECTURE"],
        "python_sources",
        lambda root, package: iter([("galaga.facade.probe", "galaga.facade", source)]),
    )
    with pytest.raises(AssertionError):
        contract["test_facade_does_not_read_private_core_product_tables"]()


@pytest.mark.parametrize("file", ("compatibility/test_facade_namespace.py", "core/test_migration_boundary.py"))
def test_both_core_guards_check_nested_resources_and_allow_inward_absolute_imports(file, monkeypatch):
    contract = runpy.run_path(str(TEST_ROOT / file))
    test = contract[
        "test_core_has_no_import_edge_to_any_outer_galaga_layer"
        if "compatibility" in file
        else "test_core_source_does_not_import_outer_galaga_modules"
    ]
    for source, forbidden in (
        ("from ...facade import Algebra", True),
        ("from galaga.core import Algebra", False),
    ):
        monkeypatch.setitem(
            contract["ARCHITECTURE"],
            "python_sources",
            lambda root, package, source=source: iter([("galaga.core.nested.probe", "galaga.core.nested", source)]),
        )
        if forbidden:
            with pytest.raises(AssertionError):
                test()
        else:
            test()
