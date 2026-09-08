"""Archive integrity, mutation controls and executable inner-product teaching."""

import ast
import copy
import hashlib
import inspect
import runpy
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from tools.isolate_phase8_legacy_tests import LEGACY_ORACLE_TESTS

import galaga as ga

TEST_ROOT = Path(__file__).parents[1]
PUBLIC_FILE = "facade/test_inner_product_contracts.py"
CONTRACT = runpy.run_path(str(TEST_ROOT / PUBLIC_FILE))
ARCHIVE = CONTRACT["ARCHIVE"]


def test_all_thirteen_identities_retain_source_evidence_and_a_public_owner():
    assert ARCHIVE["schema_version"] == 1
    assert ARCHIVE["source_commit"] == "02c7654638ed0d846943e224afecba79de886182"
    assert ARCHIVE["captured_on"] == "2026-09-08"
    assert ARCHIVE["python"] == "3.14.4" and ARCHIVE["numpy"] == "2.5.2"
    assert ARCHIVE["source_path"] == "packages/galaga/tests/test_coverage.py"
    assert ARCHIVE["public_owner"] == PUBLIC_FILE
    assert ARCHIVE["sha256"] == "464ecca03437ea54a17d20baa5b9af8d8f86516acc043ecc0062f41d6ec1a90f"
    assert hashlib.sha256(ARCHIVE["source"].encode()).hexdigest() == ARCHIVE["sha256"]
    classes = {cls.name: cls for cls in ast.parse(ARCHIVE["source"]).body if isinstance(cls, ast.ClassDef)}
    all_ids = [
        f"{cls.name}.{method.name}"
        for cls in classes.values()
        for method in cls.body
        if isinstance(method, ast.FunctionDef) and method.name.startswith("test_")
    ]
    assert ARCHIVE["all_source_test_ids"] == all_ids
    assert len(all_ids) == len(set(all_ids)) == 192
    owners = {"TestIpFunction", "TestSymbolicIp"}
    ids = {name for name in all_ids if name.split(".")[0] in owners}
    assert len(ids) == len(ARCHIVE["test_ids"]) == 13
    assert (
        ids
        == set(ARCHIVE["test_ids"])
        == {
            f"{name}.{method}"
            for name in owners
            for method, _function in inspect.getmembers(CONTRACT[name], inspect.isfunction)
            if method.startswith("test_")
        }
    )
    assert PUBLIC_FILE not in LEGACY_ORACLE_TESTS
    current = ast.parse((TEST_ROOT / "test_coverage.py").read_text())
    assert not owners & {node.name for node in current.body if isinstance(node, ast.ClassDef)}


def test_archive_keeps_the_actual_default_and_all_modes_even_when_the_old_test_name_was_misleading():
    assert ARCHIVE["seed"] == 112
    assert len(ARCHIVE["cases"]) == len({case["id"] for case in ARCHIVE["cases"]}) == 15
    assert {tuple(case["signature"]) for case in ARCHIVE["cases"]} == {(1, 1, 1), (1, -1, 1), (1, 1, 0)}
    spellings = {
        "doran_lasenby": "a·b",
        "hestenes": "a·b",
        "left": "a⌋b",
        "right": "a⌊b",
        "scalar": "a∗b",
    }
    latex = {
        "doran_lasenby": r"a \cdot b",
        "hestenes": r"a \cdot b",
        "left": r"a \;\lrcorner\; b",
        "right": r"a \;\llcorner\; b",
        "scalar": "a * b",
    }
    for case in ARCHIVE["cases"]:
        assert case["default_type"] == "Multivector"
        assert case["default_node"] == "Dli"
        assert [row["mode"] for row in case["results"]] == list(spellings)
        for row in case["results"]:
            assert row["unicode"] == spellings[row["mode"]]
            assert row["latex"] == latex[row["mode"]]
    source = ast.parse(ARCHIVE["source"])
    cls = next(node for node in source.body if isinstance(node, ast.ClassDef) and node.name == "TestSymbolicIp")
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "test_ip_hestenes")
    call = next(
        node
        for node in ast.walk(method)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "sip"
    )
    assert call.keywords == []  # Despite its name, this historical test exercised the default.
    assert [error["tracked"] for error in ARCHIVE["errors"]] == [False, True]
    assert all(
        error["type"] == "ValueError" and "Unknown inner product mode" in error["message"]
        for error in ARCHIVE["errors"]
    )


@pytest.mark.parametrize("data", ([1], [np.nan] * 8, [0] * 8))
def test_archive_replay_rejects_malformed_nonfinite_and_erased_coefficients(data):
    case = copy.deepcopy(ARCHIVE["cases"][3])
    case["results"][0]["data"] = data
    with pytest.raises(AssertionError):
        CONTRACT["test_archived_modes_replay_through_explicit_public_operations"](case, True)


def test_scalar_handling_probe_rejects_doran_lasenby_substituted_for_hestenes(monkeypatch):
    monkeypatch.setattr(ga, "hestenes_inner", ga.doran_lasenby_inner)
    with pytest.raises(AssertionError):
        CONTRACT["test_archived_modes_replay_through_explicit_public_operations"](ARCHIVE["cases"][0], True)


def test_coordinate_probe_rejects_left_substituted_for_right_contraction(monkeypatch):
    monkeypatch.setattr(ga, "right_contraction", ga.left_contraction)
    with pytest.raises(AssertionError):
        CONTRACT["test_vector_blade_contractions_follow_coordinate_pairings_and_operand_order"](CONTRACT["GRAMS"][1])


def test_minor_oracle_rejects_the_scalar_product_in_place_of_the_metric_pairing(monkeypatch):
    monkeypatch.setattr(ga, "metric_inner_product", ga.scalar_product)
    with pytest.raises(AssertionError):
        CONTRACT["test_vector_blade_contractions_follow_coordinate_pairings_and_operand_order"](CONTRACT["GRAMS"][0])


def test_default_glyph_probe_rejects_reversed_contraction_floors(monkeypatch):
    original = ga.Multivector.display
    monkeypatch.setattr(
        ga.Multivector,
        "display",
        lambda value, *args, **kwargs: original(value, *args, **kwargs).replace(r"\lfloor", r"\rfloor"),
    )
    with pytest.raises(AssertionError):
        CONTRACT["TestSymbolicIp"]().test_ip_right(ga.Algebra(3))


def test_changed_bindings_probe_rejects_cached_eager_replay(monkeypatch):
    original = ga.evaluate
    saved = {}

    def cached(expression, **kwargs):
        if expression not in saved:
            saved[expression] = original(expression, **kwargs)
        return saved[expression]

    monkeypatch.setattr(ga, "evaluate", cached)
    with pytest.raises(AssertionError):
        CONTRACT["test_every_grade_pair_and_mixed_values_match_metric_and_reference_oracles"](
            CONTRACT["GRAMS"][1], "left_contraction", "named", "latex"
        )


def test_invalid_oracle_operation_is_not_silently_treated_as_a_right_contraction():
    with pytest.raises(AssertionError):
        CONTRACT["oracle_tensor"]("unknown", CONTRACT["GRAMS"][0])


def test_inner_product_contracts_run_with_legacy_imports_blocked():
    program = """
import importlib.abc
import sys
roots = {
    'galaga.algebra', 'galaga.basis_blade', 'galaga.blade_convention',
    'galaga.expr', 'galaga.latex_build', 'galaga.latex_emit',
    'galaga.latex_nodes', 'galaga.latex_rewrite', 'galaga.latex_symbols',
    'galaga.lazy', 'galaga.legacy', 'galaga.notation', 'galaga.ops',
    'galaga.symbolic', 'galaga.symbolic_core',
}
def forbidden(name):
    return any(name == root or name.startswith(root + '.') for root in roots)
class RejectLegacy(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if forbidden(fullname):
            raise AssertionError('inner-product contract imported legacy: ' + fullname)
sys.meta_path.insert(0, RejectLegacy())
import pytest
result = pytest.main(['--noconftest', '-q', sys.argv[1]])
assert result == 0
assert not any(forbidden(name) for name in sys.modules)
"""
    result = subprocess.run(
        [sys.executable, "-c", program, str(TEST_ROOT / PUBLIC_FILE)],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.skipif(sys.version_info < (3, 14), reason="notebook uses Python 3.14 t-strings")
@pytest.mark.parametrize("gram", (((2, 1), (1, 3)), ((1, 0), (0, 1)), ((2, 1), (1, -1)), ((1, 0), (0, 0))))
def test_notebook_runs_all_metric_choices_and_displays_computed_pairings(gram):
    notebook = TEST_ROOT.parents[2] / "examples/algebra/inner_product_family.py"
    app = runpy.run_path(str(notebook))["app"]
    overrides = {} if gram == ((2, 1), (1, 3)) else {"metric_selector": SimpleNamespace(value=gram)}
    outputs, definitions = app.run(defs=overrides)
    np.testing.assert_array_equal(definitions["gram_matrix"].mat, gram)
    np.testing.assert_array_equal(definitions["B"].data, [0, 0, 0, 1])
    assert np.isclose(definitions["determinant"], np.linalg.det(gram), rtol=0, atol=1e-12)
    results = definitions["comparison_results"]
    pairs = definitions["comparison_pairs"]
    assert len(results) == len(pairs) == 6
    html = "\n".join(getattr(output, "text", "") for output in outputs)
    assert r"\begin{pmatrix}" in html
    assert "G_{12}+B" in html
    assert "shared symbol" in html and "nonzero bivector" in html
    for title, (a, b) in pairs.items():
        assert title in html
        for label, function in definitions["inner_operations"].items():
            value = results[title][label]
            expected = CONTRACT["expected_coefficients"](function.__name__, gram, a.data, b.data)
            CONTRACT["assert_coefficients"](value, expected)
            assert value.latex(content="value") in html
    assert definitions["mixed_dli"].expr.operation_id == "doran_lasenby_inner"
    assert definitions["mixed_hi"].expr.operation_id == "hestenes_inner"
