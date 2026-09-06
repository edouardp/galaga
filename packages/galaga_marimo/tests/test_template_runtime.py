"""Collecting renderer tests must not replace Python's real template runtime."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="galaga-marimo requires Python 3.14")


@pytest.mark.parametrize("import_order", ("tests-first", "runtime-first"))
def test_collecting_renderer_tests_preserves_native_t_strings(import_order: str) -> None:
    program = """
import runpy
import sys
import string.templatelib as native

if sys.argv[2] == "runtime-first":
    import galaga_marimo

runpy.run_path(sys.argv[1])

assert sys.modules["string.templatelib"] is native
from galaga_marimo import renderer
from galaga_marimo import api
assert renderer.Template is native.Template
assert renderer.Interpolation is native.Interpolation
assert api.Template is native.Template

value = 7
template = t"Value: {value}, formatted: {value:.1f}"
assert type(template) is native.Template
assert renderer.render_template(template) == "Value: 7, formatted: 7.0"
"""
    completed = subprocess.run(
        [sys.executable, "-c", program, str(Path(__file__).with_name("test_galaga_marimo.py")), import_order],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
