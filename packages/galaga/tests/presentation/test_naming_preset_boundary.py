"""Historical ownership, corruption checks and naming lesson execution."""

import ast
import copy
import hashlib
import inspect
import runpy
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from tools.isolate_phase8_legacy_tests import LEGACY_ORACLE_TESTS

import galaga as ga

TEST_ROOT = Path(__file__).parents[1]
PUBLIC_FILE = "presentation/test_naming_preset_contracts.py"
CONTRACT = runpy.run_path(str(TEST_ROOT / PUBLIC_FILE))
ARCHIVE = CONTRACT["ARCHIVE"]


def test_all_nine_naming_identities_have_complete_source_evidence_and_public_owners():
    assert ARCHIVE["schema_version"] == 1
    assert ARCHIVE["source_commit"] == "f75d7954da77350fc856e4003459f6f36e1882b1"
    assert ARCHIVE["captured_on"] == "2026-09-08"
    assert ARCHIVE["python"] == "3.14.4" and ARCHIVE["numpy"] == "2.5.2"
    assert ARCHIVE["source_path"] == "packages/galaga/tests/test_coverage.py"
    assert ARCHIVE["public_owner"] == PUBLIC_FILE
    assert ARCHIVE["sha256"] == "d53ec10b2e5360954bf9cc3803ba54db8350a8efdddc708172aa9452e8a11dbb"
    assert hashlib.sha256(ARCHIVE["source"].encode()).hexdigest() == ARCHIVE["sha256"]
    identifiers = [
        f"{cls.name}.{method.name}"
        for cls in ast.parse(ARCHIVE["source"]).body
        if isinstance(cls, ast.ClassDef)
        for method in cls.body
        if isinstance(method, ast.FunctionDef) and method.name.startswith("test_")
    ]
    assert identifiers == ARCHIVE["all_source_test_ids"] and len(set(identifiers)) == 29
    owners = {
        f"TestNamingPresets.{method}"
        for method, function in inspect.getmembers(CONTRACT["TestNamingPresets"], inspect.isfunction)
        if method.startswith("test_")
    }
    assert owners == set(ARCHIVE["test_ids"]) and len(owners) == 9
    assert owners <= set(identifiers)
    current = ast.parse((TEST_ROOT / "test_coverage.py").read_text())
    assert "TestNamingPresets" not in {node.name for node in current.body if isinstance(node, ast.ClassDef)}
    assert PUBLIC_FILE not in LEGACY_ORACLE_TESTS


def test_archive_preserves_complete_vocabularies_and_actual_errors():
    tables = ARCHIVE["tables"]
    assert [t["id"] for t in tables] == ["gamma", "sigma", "sigma_xyz", "custom_2", "custom_3"]
    assert [len(t["labels"]) for t in tables] == [16, 8, 8, 4, 8]
    assert sum(len(t["labels"]) for t in tables) == 44
    assert sum(len(r["lookups"]) for t in tables for r in t["labels"]) == 132
    assert tables[2]["labels"][1]["names"] == {"ascii": "x", "unicode": "σₓ", "latex": r"\sigma_x"}
    assert tables[2]["labels"][4]["unicode"] == "σz"
    assert tables[0]["labels"][-1]["names"]["ascii"] == "g0g1g2g3"
    assert tables[4]["labels"][-1]["unicode"] == "𝐚𝐛𝐜"
    assert ARCHIVE["errors"] == [
        {"id": "short_names", "type": "ValueError", "message": "vector_names has 1 entries, need at least 2"},
        {"id": "invalid_blades", "type": "TypeError", "message": "blades must be a BladeConvention, got str"},
        {"id": "unknown_name", "type": "ValueError", "message": "Unknown blade name: 'xyz'"},
    ]


@pytest.mark.parametrize("field", ("name", "mask", "coefficients", "shape", "nonfinite", "lookup", "square", "repr"))
def test_archive_replay_rejects_corrupted_names_values_and_squares(field):
    table = copy.deepcopy(ARCHIVE["tables"][0])
    row = table["labels"][3]
    if field == "name":
        row["names"]["ascii"] = "wrong"
    elif field == "mask":
        row["mask"] = 2
    elif field == "coefficients":
        row["data"] = [0] * 16
    elif field == "shape":
        row["data"] = [0]
    elif field == "nonfinite":
        row["data"] = [np.nan] * 16
    elif field == "lookup":
        row["lookups"]["ascii"] = [0] * 16
    elif field == "square":
        row["square"][0] *= -1
    else:
        row["repr"] = "wrong"
    with pytest.raises(AssertionError):
        CONTRACT["test_complete_archived_vocabularies_preserve_lookup_values_and_blade_squares"](table, "ascii", True)


def test_repr_probe_rejects_the_old_unicode_default(monkeypatch):
    monkeypatch.setattr(ga.Multivector, "__repr__", lambda value: value.unicode())
    with pytest.raises(AssertionError):
        CONTRACT["TestNamingPresets"]().test_gamma_preset()


def test_general_gram_probe_rejects_interpreting_a_blade_label_as_a_geometric_word(monkeypatch):
    original = ga.Algebra.blade

    def parsed_word(self, key, **kwargs):
        if isinstance(key, str) and key == self.blade_label(3).name.unicode:
            a, b, _ = self.basis_vectors()
            return a * b
        return original(self, key, **kwargs)

    monkeypatch.setattr(ga.Algebra, "blade", parsed_word)
    with pytest.raises(AssertionError):
        CONTRACT["test_indexed_words_are_exterior_labels_in_general_gram_frames"](
            CONTRACT["GRAMS"][1], "juxtapose", "unicode"
        )


def test_signed_lookup_probe_rejects_the_old_unsigned_slot_behavior(monkeypatch):
    original = ga.Algebra.blade

    def unsigned(self, key, **kwargs):
        return original(self, 3 if key == "oriented_plane" else key, **kwargs)

    monkeypatch.setattr(ga.Algebra, "blade", unsigned)
    with pytest.raises(AssertionError):
        CONTRACT["test_oriented_names_aliases_and_native_masks_preserve_computed_exterior_signs"](
            CONTRACT["GRAMS"][1], "unicode", True
        )


def test_oracle_helpers_reject_unknown_conventions_and_nonfinite_data():
    with pytest.raises(AssertionError):
        CONTRACT["convention_for"]("unknown")
    with pytest.raises(AssertionError):
        CONTRACT["assert_data"]([np.inf], [0])


def test_public_naming_contracts_run_with_legacy_imports_blocked():
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
            raise AssertionError('naming contract imported legacy: ' + fullname)
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
def test_notebook_teaches_blade_words_without_hiding_oblique_metric_terms():
    path = TEST_ROOT.parents[2] / "examples/galaga_v2/algebra_construction.py"
    outputs, definitions = runpy.run_path(str(path))["app"].run()
    base, view = definitions["naming_algebra"], definitions["naming_view"]
    assert view.numeric is base.numeric
    np.testing.assert_array_equal(definitions["naming_gram"].mat, view.gram)
    gram = view.gram
    expected_pair = CONTRACT["exterior_coefficients"](3, 3)
    expected_pair[0] = gram[0, 1]
    expected_triple = CONTRACT["exterior_coefficients"](3, 7)
    expected_triple[1], expected_triple[2], expected_triple[4] = gram[1, 2], -gram[0, 2], gram[0, 1]
    for key, data in (("gp", expected_pair), ("triple", expected_triple)):
        value = definitions["naming_" + key]
        CONTRACT["assert_data"](value.data, data)
        CONTRACT["assert_data"](ga.evaluate(value.expr, algebra=view).data, data)
    a, b, c = (definitions["naming_" + key] for key in ("a", "b", "c"))
    assert definitions["naming_plane"] == view.blade("ab") == a ^ b
    assert definitions["naming_volume"] == view.blade("abc") == a ^ b ^ c
    assert definitions["naming_gp"] != definitions["naming_plane"]
    assert definitions["naming_triple"] != definitions["naming_volume"]
    assert "a" not in view.locals()
    assert definitions["naming_local_view"].locals()["a"] == a
    assert definitions["naming_local_view"].numeric is base.numeric
    html = "\n".join(getattr(output, "text", "") for output in outputs)
    for text in (
        "A blade word is a label, not a product parser",
        "Native exterior plane",
        "Geometric word",
        "False",
        "True",
    ):
        assert text in html
    for key in ("plane", "volume", "gp", "triple"):
        assert definitions["naming_" + key].latex(content="value") in html
