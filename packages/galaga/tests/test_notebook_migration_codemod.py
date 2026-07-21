"""Safety tests for the maintained-notebook Galaga 2 codemod."""

from pathlib import Path

import pytest
from tools.migrate_v2_notebooks import migrate_path, migrate_source


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


def test_makes_tstring_value_rendering_explicit_without_breaking_python_formats() -> None:
    source = '''\
gm.md(t"""
{x} = {x.eval()}
expression = {x.reveal()}
length = {norm(x).eval():.3f}
""")
'''

    migrated = migrate_source(source)

    assert 'gm.md(rt"""' in migrated
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
