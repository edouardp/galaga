"""Symbol conversion must not preserve an implicit legacy-engine dependency."""

import subprocess
import sys
from pathlib import Path

from tools.isolate_phase8_legacy_tests import LEGACY_ORACLE_TESTS

TEST_ROOT = Path(__file__).parents[1]
CONTRACT_FILES = ("test_latex_symbols.py", "presentation/test_name_conversion.py")
IMPORT_GUARD = """
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
            raise AssertionError('symbol conversion imported legacy module: ' + fullname)

sys.meta_path.insert(0, RejectLegacy())
"""


def test_symbol_conversion_suites_execute_without_legacy_imports():
    program = (
        IMPORT_GUARD
        + """
import pytest
result = pytest.main(['--noconftest', '-q', *sys.argv[1:]])
assert result == 0
assert not any(forbidden(name) for name in sys.modules)
"""
    )
    completed = subprocess.run(
        [sys.executable, "-c", program, *(str(TEST_ROOT / name) for name in CONTRACT_FILES)],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_old_symbol_import_is_removed_and_public_conversion_still_works():
    program = (
        r"""
import importlib
import importlib.util
assert importlib.util.find_spec('galaga.latex_symbols') is None
try:
    importlib.import_module('galaga.latex_symbols')
except ModuleNotFoundError as error:
    assert error.name == 'galaga.latex_symbols'
else:
    raise AssertionError('the retired symbol shim is still importable')
"""
        + IMPORT_GUARD
        + r"""
from galaga.names import LatexSymbols, Name
assert LatexSymbols().lookup(r'\mathbb{a}') == ('𝕒', 'a')
assert Name.from_latex(r'\mathbb{a}').unicode == '𝕒'
assert not any(forbidden(name) for name in sys.modules)
"""
    )
    completed = subprocess.run(
        [sys.executable, "-c", program],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_symbol_conversion_suites_are_not_exempt_from_legacy_construction_guard():
    assert not (set(CONTRACT_FILES) & set(LEGACY_ORACLE_TESTS))
