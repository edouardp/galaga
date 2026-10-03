"""Historical ownership, corruption checks and naming lesson execution."""

import copy
import runpy
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

import galaga as ga

TEST_ROOT = Path(__file__).parents[1]
PUBLIC_FILE = "presentation/test_naming_preset_contracts.py"
CONTRACT = runpy.run_path(str(TEST_ROOT / PUBLIC_FILE))
ARCHIVE = CONTRACT["ARCHIVE"]


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
