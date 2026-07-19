"""Tests for public-protocol Mermaid expression diagrams."""

from __future__ import annotations

from pathlib import Path

import pytest
from galaga_mermaid import expr_to_mermaid, mv_to_mermaid

from galaga.expression import ScalarLiteral
from galaga.facade import Algebra, geometric_product


def _alg() -> Algebra:
    return Algebra(3)


class TestExprToMermaid:
    def test_symbol_leaf(self) -> None:
        algebra = _alg()
        value = algebra.vector([1, 0, 0], name="v", expr=True)

        result = expr_to_mermaid(
            value.expr,
            presentation=algebra.presentation,
            algebra=algebra,
            environment={"v": value},
        )

        assert "graph TD" in result
        assert '"v' in result

    def test_scalar_leaf(self) -> None:
        algebra = _alg()

        result = expr_to_mermaid(
            ScalarLiteral(3),
            presentation=algebra.presentation,
            algebra=algebra,
        )

        assert "3" in result

    def test_binary_geometric_product(self) -> None:
        algebra = _alg()
        left = algebra.vector([1, 0, 0], name="a", expr=True)
        right = algebra.vector([0, 1, 0], name="b", expr=True)
        value = geometric_product(left, right)

        result = expr_to_mermaid(value.expr, presentation=algebra.presentation)

        assert "ab" in result
        assert result.count("-->") == 2

    @pytest.mark.parametrize(
        ("factory", "fragment"),
        (
            (lambda value: -value, "-v"),
            (lambda value: 2 * value, "2v"),
            (lambda value: value / 3, "v / 3"),
        ),
    )
    def test_unary_and_scalar_operations(self, factory, fragment: str) -> None:
        algebra = _alg()
        value = algebra.vector([1, 0, 0], name="v", expr=True)

        result = expr_to_mermaid(factory(value).expr, presentation=algebra.presentation)

        assert fragment in result

    def test_show_values_uses_explicit_environment(self) -> None:
        algebra = _alg()
        value = algebra.vector([1, 2, 3], name="v", expr=True)

        with_values = expr_to_mermaid(
            value.expr,
            presentation=algebra.presentation,
            algebra=algebra,
            environment={"v": value},
        )
        without_values = expr_to_mermaid(
            value.expr,
            presentation=algebra.presentation,
            show_values=False,
        )

        assert "<br>" in with_values
        assert "<br>" not in without_values

    def test_direction_is_validated(self) -> None:
        algebra = _alg()
        expression = ScalarLiteral(1)

        assert "graph LR" in expr_to_mermaid(expression, presentation=algebra.presentation, direction="LR")
        with pytest.raises(ValueError, match="direction"):
            expr_to_mermaid(expression, presentation=algebra.presentation, direction="sideways")

    def test_compact_tree_skips_intermediate_calls(self) -> None:
        algebra = _alg()
        left = algebra.vector([1, 0, 0], name="a", expr=True)
        middle = algebra.vector([0, 1, 0], name="b", expr=True)
        right = algebra.vector([0, 0, 1], name="c", expr=True)
        value = left + geometric_product(middle, right)

        expanded = expr_to_mermaid(value.expr, presentation=algebra.presentation)
        compact = expr_to_mermaid(value.expr, presentation=algebra.presentation, compact=True)

        assert expanded.count("-->") == 4
        assert compact.count("-->") == 3


class TestMvToMermaid:
    def test_named_value_derives_presentation_and_environment(self) -> None:
        algebra = _alg()
        value = algebra.vector([1, 2, 3], name="v", expr=True)

        result = mv_to_mermaid(value)

        assert '"v<br>' in result

    def test_tracked_expression_uses_public_expr_property(self) -> None:
        algebra = _alg()
        left = algebra.vector([1, 0, 0], name="a", expr=True)
        right = algebra.vector([0, 1, 0], name="b", expr=True)

        result = mv_to_mermaid(geometric_product(left, right))

        assert "-->" in result

    def test_untracked_value_gets_literal_provenance_without_mutation(self) -> None:
        algebra = _alg()
        value = algebra.vector([1, 2, 3])

        result = mv_to_mermaid(value)

        assert "graph TD" in result
        assert value.expr is None


def test_implementation_has_no_legacy_expression_or_multivector_private_access() -> None:
    source = (Path(__file__).parents[1] / "galaga_mermaid/mermaid.py").read_text()

    assert "from galaga.expr import" not in source
    assert "from galaga.render import" not in source
    assert "_to_expr" not in source
    assert "._expr" not in source
    assert "._name" not in source
