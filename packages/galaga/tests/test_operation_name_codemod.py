"""Safety tests for the numeric-test operation-name codemod."""

from tools.canonicalize_core_test_operations import canonicalize_source


def test_only_approved_qualified_import_references_are_canonicalized() -> None:
    source = """\
from galaga.core import (
    geometric_product as gp,
    grade_involution as involute,
    outer_product as op,
)

# gp, op, and involute stay unchanged in comments.
LABEL = "gp op involute"

def identity(left, right):
    return gp(left, right), op(left, right), involute(left)
"""

    canonical = canonicalize_source(source)

    assert "geometric_product as gp" not in canonical
    assert "outer_product as op" not in canonical
    assert "grade_involution as involute" not in canonical
    assert "geometric_product(left, right)" in canonical
    assert "outer_product(left, right)" in canonical
    assert "grade_involution(left)" in canonical
    assert "# gp, op, and involute stay unchanged in comments." in canonical
    assert 'LABEL = "gp op involute"' in canonical


def test_local_names_and_unapproved_import_aliases_are_not_rewritten() -> None:
    source = """\
from galaga.core import half_commutator as lie_bracket

def gp(value):
    return value

def identity(left, right):
    return gp(left), lie_bracket(left, right)
"""

    assert canonicalize_source(source) == source


def test_canonicalization_is_idempotent() -> None:
    source = """\
from galaga.core import geometric_product as gp

result = gp(left, right)
"""

    canonical = canonicalize_source(source)

    assert canonicalize_source(canonical) == canonical
