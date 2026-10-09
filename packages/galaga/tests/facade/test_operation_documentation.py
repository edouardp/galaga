"""Public operation help must be visible to runtime and static discovery."""

from __future__ import annotations

import ast
import inspect
import textwrap

import pytest

import galaga

PUBLIC_NUMERIC_FUNCTIONS = [
    name
    for name in galaga.__all__
    if inspect.isfunction(function := getattr(galaga, name)) and function.__module__ == "galaga.facade._numeric"
]


@pytest.mark.parametrize("name", PUBLIC_NUMERIC_FUNCTIONS)
def test_public_numeric_functions_have_literal_source_docstrings(name):
    function = getattr(galaga, name)
    definition = ast.parse(textwrap.dedent(inspect.getsource(function))).body[0]
    assert isinstance(definition, ast.FunctionDef)
    docstring = ast.get_docstring(definition)
    assert docstring, f"{name} needs a source docstring for static editor help"
    assert inspect.getdoc(function) == docstring


def test_right_hodge_dual_static_signature_help():
    jedi = pytest.importorskip("jedi")
    script = jedi.Script("from galaga import right_hodge_dual\nright_hodge_dual(")
    (signature,) = script.get_signatures()
    documentation = signature.docstring()
    assert "right_hodge_dual(value: Multivector)" in documentation
    assert "right_complement(metric_apply(value))" in documentation


def test_right_hodge_dual_static_completion_help():
    jedi = pytest.importorskip("jedi")
    script = jedi.Script("from galaga import right_hodge_dual\nright_hodge_du")
    (completion,) = [item for item in script.complete() if item.name == "right_hodge_dual"]
    assert "right_complement(metric_apply(value))" in completion.docstring(raw=True)
