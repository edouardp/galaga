"""Safety tests for the maintained-notebook Galaga 2 codemod."""

import subprocess
import sys
from pathlib import Path

import pytest
from tools.migrate_v2_notebooks import migrate_path, migrate_source, migrated_notebook_paths


def test_migrates_only_structural_v1_facade_patterns() -> None:
    source = """\
from galaga import Algebra, b_sta, involute, norm

# .eval(), .name(), b_sta, and involute remain unchanged in comments.
LABEL = ".eval() .name() b_sta involute"
alg = Algebra((1, -1, -1, -1), blades=b_sta(), repr_unicode=True)
e0, e1, e2, e3 = alg.basis_vectors(lazy=True)
x = involute((e0 + e1).name("x"))
latex_only = e1.name(latex=r"\\sigma_1")
value = x.eval()
scalar = (norm(x).eval() ** 2).scalar_part
"""

    migrated = migrate_source(source)

    assert "from galaga import Algebra, spacetime_blade_convention, grade_involution, norm" in migrated
    assert "blades=spacetime_blade_convention()" in migrated
    assert "repr_unicode" not in migrated
    assert "basis_vectors(expr=True)" in migrated
    assert '(e0 + e1).named("x")' in migrated
    assert 'e1.named(r"\\sigma_1", latex=r"\\sigma_1")' in migrated
    assert "value = x" in migrated
    assert "scalar = (norm(x) ** 2)" in migrated
    assert "# .eval(), .name(), b_sta, and involute remain unchanged in comments." in migrated
    assert 'LABEL = ".eval() .name() b_sta involute"' in migrated


def test_makes_tstring_value_rendering_explicit_without_changing_string_kind() -> None:
    source = '''\
gm.md(t"""
{x} = {x.eval()}
expression = {x.reveal()}
length = {norm(x).eval():.3f}
""")
'''

    migrated = migrate_source(source)

    assert 'gm.md(t"""' in migrated
    assert "{x} = {x:value}" in migrated
    assert "expression = {x:expr}" in migrated
    assert "length = {norm(x):.3f}" in migrated


def test_preserves_non_galaga_name_protocols() -> None:
    source = """\
matrix = MatrixRepr(data).name(latex="M")
quaternion = QuatMatrixRepr(data).name(latex="Q")
converted = to_matrix(value).name("V")
mv = value.name("v")
"""

    migrated = migrate_source(source)

    assert 'MatrixRepr(data).name(latex="M")' in migrated
    assert 'QuatMatrixRepr(data).name(latex="Q")' in migrated
    assert 'to_matrix(value).name("V")' in migrated
    assert 'value.named("v")' in migrated


def test_migration_is_idempotent() -> None:
    source = """\
from galaga import Algebra

e1, e2 = Algebra((1, 1), repr_unicode=True).basis_vectors(symbolic=True)
result = (e1 * e2).name("B").eval()
"""

    migrated = migrate_source(source)

    assert migrate_source(migrated) == migrated


def test_promotes_the_explicit_facade_namespace_to_the_phase8_public_api() -> None:
    source = "from galaga.facade import Algebra, DisplayPolicy\n"

    assert migrate_source(source) == "from galaga import Algebra, DisplayPolicy\n"


def test_path_guard_rejects_files_outside_the_ledger(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    unledgered = repository / "examples" / "unledgered.py"
    unledgered.parent.mkdir(parents=True)
    unledgered.write_text("from galaga import Algebra\n")

    with pytest.raises(ValueError, match="unledgered notebook"):
        migrate_path(unledgered, repository=repository, check=False)

    outside = tmp_path / "outside.py"
    outside.write_text("from galaga import Algebra\n")
    with pytest.raises(ValueError, match="outside"):
        migrate_path(outside, repository=repository, check=False)


def test_remaining_notebooks_join_the_shared_ledger_without_duplicates(tmp_path: Path) -> None:
    paths = migrated_notebook_paths(tmp_path)
    assert len(paths) == len(set(paths))
    assert {
        tmp_path / "test_mermaid.py",
        tmp_path / "examples/basics/dynamic_notation.py",
        tmp_path / "examples/basics/latex_rewrites_demo.py",
        tmp_path / "examples/basics/galaga_marimo_demo.py",
        tmp_path / "examples/quantum/quantum_physics.py",
    } <= set(paths)


def test_root_notebook_is_an_explicit_exception_not_a_repository_wide_write_permission(tmp_path: Path) -> None:
    notebook = tmp_path / "test_mermaid.py"
    source = "value = algebra.basis_vectors(lazy=True)\n"
    notebook.write_text(source)
    assert migrate_path(notebook, repository=tmp_path, check=True)
    assert notebook.read_text() == source
    assert migrate_path(notebook, repository=tmp_path, check=False)
    assert notebook.read_text() == "value = algebra.basis_vectors(expr=True)\n"
    assert not migrate_path(notebook, repository=tmp_path, check=True)

    other = tmp_path / "test_other.py"
    other.write_text(source)
    with pytest.raises(ValueError, match="outside"):
        migrate_path(other, repository=tmp_path, check=False)
    assert other.read_text() == source


def test_root_notebook_symlink_cannot_escape_the_repository(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    outside = tmp_path / "outside.py"
    source = "value = algebra.basis_vectors(lazy=True)\n"
    outside.write_text(source)
    notebook = repository / "test_mermaid.py"
    notebook.symlink_to(outside)
    with pytest.raises(ValueError, match="outside"):
        migrate_path(notebook, repository=repository, check=False)
    assert outside.read_text() == source


def test_root_notebook_is_not_collected_as_a_pytest_module(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[3]
    conftest = tmp_path / "conftest.py"
    conftest.write_text((root / "conftest.py").read_text())
    # Deliberately invalid even on 3.14: collection must never parse this file.
    (tmp_path / "test_mermaid.py").write_text("def notebook_must_not_be_collected(\n")
    (tmp_path / "test_ordinary.py").write_text("def test_ordinary():\n    assert True\n")
    command = [sys.executable, "-m", "pytest", "--collect-only", "-q"]
    result = subprocess.run(command, cwd=tmp_path, check=False, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "test_ordinary.py::test_ordinary" in result.stdout
    assert "test_mermaid.py" not in result.stdout
    # Negative control: the test fails if the notebook exclusion disappears.
    conftest.write_text("")
    broken = subprocess.run(command, cwd=tmp_path, check=False, capture_output=True, text=True)
    assert broken.returncode != 0
    assert "test_mermaid.py" in broken.stdout + broken.stderr
