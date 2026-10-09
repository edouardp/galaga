"""Expression recipes for exact rendering and coefficient snapshots."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np

import galaga.facade as facade
from galaga import presets

Recipe = Callable[["RenderingContext"], Any]


@dataclass(frozen=True, slots=True)
class RenderingProfile:
    """Algebra policy shared by the historical capture and live facade."""

    id: str
    description: str


@dataclass(frozen=True, slots=True)
class RenderingCase:
    """One implementation-neutral expression recipe."""

    id: str
    intent: str
    build: Recipe
    operations: frozenset[str] = frozenset()
    profile: str = "default-cl3"
    result_name: str | None = "x"
    channels: tuple[str, ...] = ("expression", "value", "full", "rich")

    @property
    def key(self) -> str:
        return f"{self.profile}/{self.id}"


PROFILES: Mapping[str, RenderingProfile] = {
    "default-cl3": RenderingProfile(
        "default-cl3",
        "Cl(3,0), default blade convention and notation, full teaching display",
    ),
    "lengyel-rga": RenderingProfile(
        "lengyel-rga",
        "Lengyel RGA signature, blade convention, notation, and full teaching display",
    ),
}


class RenderingContext:
    """Facade-only vocabulary used by the retained expression recipes."""

    __slots__ = ("algebra", "api", "basis", "symbols")

    def __init__(self, profile: RenderingProfile) -> None:
        self.api = facade
        if profile.id == "default-cl3":
            self.algebra = facade.Algebra(
                (1, 1, 1),
                display=facade.DisplayPolicy("full"),
            )
        elif profile.id == "lengyel-rga":
            self.algebra = facade.Algebra(
                config=presets.rga(),
                display=facade.DisplayPolicy("full"),
            )
        else:
            raise KeyError(profile.id)
        self.basis = self.algebra.basis_vectors(expr=True)
        self.symbols = tuple(
            value.named(name, latex=name, unicode=name)
            for value, name in zip(self.basis, ("a", "b", "c", "d"), strict=False)
        )

    @property
    def a(self) -> Any:
        return self.symbols[0]

    @property
    def b(self) -> Any:
        return self.symbols[1]

    @property
    def c(self) -> Any:
        return self.symbols[2]

    @property
    def sum(self) -> Any:
        return self.a + self.b

    @property
    def bivector(self) -> Any:
        return self.a ^ self.b

    @property
    def mixed(self) -> Any:
        return 1 + self.a + self.bivector

    @property
    def invertible(self) -> Any:
        return 2 + 0.25 * self.a

    @property
    def rotor(self) -> Any:
        return self.call("exp", 0.25 * self.bivector)

    def call(self, operation: str, *args: Any) -> Any:
        return getattr(self.api, operation)(*args)

    def concrete(self, coefficients: Iterable[float]) -> Any:
        data = np.asarray(tuple(coefficients), dtype=np.float64)
        return self.algebra.multivector(data)

    def name_result(self, value: Any, name: str | None) -> Any:
        if name is None:
            return value
        return value.named(name, latex=name, unicode=name)


def _ops(*names: str) -> frozenset[str]:
    return frozenset(names)


def _unary(
    case_id: str,
    operation: str,
    operand: Callable[[RenderingContext], Any],
    intent: str,
    *,
    profile: str = "default-cl3",
) -> RenderingCase:
    return RenderingCase(
        case_id,
        intent,
        lambda context: context.call(operation, operand(context)),
        _ops(operation),
        profile,
    )


def _binary(
    case_id: str,
    operation: str,
    left: Callable[[RenderingContext], Any],
    right: Callable[[RenderingContext], Any],
    intent: str,
    *,
    profile: str = "default-cl3",
) -> RenderingCase:
    return RenderingCase(
        case_id,
        intent,
        lambda context: context.call(operation, left(context), right(context)),
        _ops(operation),
        profile,
    )


def _a(context: RenderingContext) -> Any:
    return context.a


def _b(context: RenderingContext) -> Any:
    return context.b


def _sum(context: RenderingContext) -> Any:
    return context.sum


def _bivector(context: RenderingContext) -> Any:
    return context.bivector


def _mixed(context: RenderingContext) -> Any:
    return context.mixed


def _invertible(context: RenderingContext) -> Any:
    return context.invertible


def _rotor(context: RenderingContext) -> Any:
    return context.rotor


def _right_bivector(context: RenderingContext) -> Any:
    return context.b ^ context.c


CASES: tuple[RenderingCase, ...] = (
    RenderingCase("add", "a + b", lambda context: context.a + context.b, _ops("add")),
    RenderingCase("subtract", "a - b", lambda context: context.a - context.b, _ops("subtract")),
    RenderingCase("negate-sum", "-(a + b)", lambda context: -context.sum, _ops("negate")),
    RenderingCase(
        "scalar-multiply",
        "1.23456789 a",
        lambda context: 1.23456789 * context.a,
        _ops("scalar_multiply"),
    ),
    RenderingCase(
        "scalar-divide-sum",
        "(a + b) / 3",
        lambda context: context.sum / 3,
        _ops("scalar_divide"),
    ),
    RenderingCase("power-sum", "(a + b)^2", lambda context: context.sum**2, _ops("power")),
    _binary("geometric-product", "geometric_product", _a, _b, "a b"),
    _binary("geometric-product-left-sum", "geometric_product", _sum, _b, "(a + b) b"),
    _binary("geometric-product-right-sum", "geometric_product", _a, _sum, "a (a + b)"),
    _binary("outer-product", "outer_product", _a, _b, "a wedge b"),
    _binary("outer-product-right-sum", "outer_product", _a, _sum, "a wedge (a + b)"),
    _binary("left-contraction", "left_contraction", _a, _right_bivector, "a left-contract (b wedge c)"),
    _binary("right-contraction", "right_contraction", _bivector, _b, "(a wedge b) right-contract b"),
    _binary("hestenes-inner", "hestenes_inner", _sum, _right_bivector, "(a + b) Hestenes-inner (b wedge c)"),
    _binary(
        "doran-lasenby-inner",
        "doran_lasenby_inner",
        _sum,
        _right_bivector,
        "(a + b) Doran-Lasenby-inner (b wedge c)",
    ),
    _binary("scalar-product", "scalar_product", _bivector, _bivector, "(a wedge b) scalar-product itself"),
    _binary(
        "metric-inner-product",
        "metric_inner_product",
        _bivector,
        _bivector,
        "(a wedge b) metric-inner-product itself",
    ),
    _binary("antidot-product", "antidot_product", _a, _b, "antidot_product(a, b)"),
    _binary("commutator", "commutator", _a, _b, "commutator(a, b)"),
    _binary("anticommutator", "anticommutator", _a, _b, "anticommutator(a, b)"),
    _binary("lie-bracket", "lie_bracket", _a, _b, "lie_bracket(a, b)"),
    _binary("jordan-product", "jordan_product", _a, _a, "jordan_product(a, a)"),
    _binary("geometric-antiproduct", "geometric_antiproduct", _a, _b, "geometric_antiproduct(a, b)"),
    _binary("regressive-product", "regressive_product", _bivector, _right_bivector, "(a wedge b) vee (b wedge c)"),
    _binary(
        "left-interior-product", "left_interior_product", _a, _right_bivector, "left_interior_product(a, b wedge c)"
    ),
    _binary("right-interior-product", "right_interior_product", _bivector, _b, "right_interior_product(a wedge b, b)"),
    RenderingCase(
        "transwedge",
        "transwedge(a, b, 0)",
        lambda context: context.call("transwedge", context.a, context.b, 0),
        _ops("transwedge"),
    ),
    RenderingCase(
        "transwedge-antiproduct",
        "transwedge_antiproduct(a, b, 0)",
        lambda context: context.call("transwedge_antiproduct", context.a, context.b, 0),
        _ops("transwedge_antiproduct"),
    ),
    _unary("reverse-atom", "reverse", _a, "reverse(a)"),
    _unary("reverse-sum", "reverse", _sum, "reverse(a + b)"),
    _unary("grade-involution", "grade_involution", _sum, "grade_involution(a + b)"),
    _unary("conjugate", "clifford_conjugate", _sum, "conjugate(a + b)"),
    _unary("dual", "dual", _bivector, "dual(a wedge b)"),
    _unary("undual", "undual", lambda context: context.call("dual", context.bivector), "undual(dual(a wedge b))"),
    _unary("complement", "complement", _bivector, "complement(a wedge b)"),
    _unary(
        "uncomplement",
        "uncomplement",
        lambda context: context.call("complement", context.bivector),
        "uncomplement(complement(a wedge b))",
    ),
    _unary("antireverse", "antireverse", _bivector, "antireverse(a wedge b)"),
    _unary("metric-apply", "metric_apply", _sum, "metric_apply(a + b)"),
    _unary("antimetric-apply", "antimetric_apply", _sum, "antimetric_apply(a + b)"),
    _unary("metric-apply-mixed", "metric_apply", _mixed, "metric_apply(1 + a + a wedge b)"),
    _unary("antimetric-apply-mixed", "antimetric_apply", _mixed, "antimetric_apply(1 + a + a wedge b)"),
    _unary("right-hodge-dual", "right_hodge_dual", _bivector, "right_hodge_dual(a wedge b)"),
    _unary("left-hodge-dual", "left_hodge_dual", _bivector, "left_hodge_dual(a wedge b)"),
    _unary("right-weight-dual", "right_weight_dual", _bivector, "right_weight_dual(a wedge b)"),
    _unary("left-weight-dual", "left_weight_dual", _bivector, "left_weight_dual(a wedge b)"),
    _unary("unit", "unit", _sum, "unit(a + b)"),
    _unary("inverse", "inverse", _invertible, "inverse(2 + 0.25 a)"),
    _unary("even-grades", "even_grades", _mixed, "even_grades(1 + a + a wedge b)"),
    _unary("odd-grades", "odd_grades", _mixed, "odd_grades(1 + a + a wedge b)"),
    _unary("exp", "exp", lambda context: 0.25 * context.bivector, "exp(0.25 a wedge b)"),
    _unary("log", "log", _rotor, "log(exp(0.25 a wedge b))"),
    _unary("outerexp", "outerexp", _a, "outerexp(a)"),
    _unary("outersin", "outersin", _a, "outersin(a)"),
    _unary("outercos", "outercos", _a, "outercos(a)"),
    _unary("outertan", "outertan", _a, "outertan(a)"),
    RenderingCase(
        "grade-projection",
        "grade((a + b) c, 1)",
        lambda context: context.call("grade", context.call("geometric_product", context.sum, context.c), 1),
        _ops("grade", "geometric_product"),
    ),
    RenderingCase(
        "grades",
        "grades(1 + a + a wedge b, [0, 2])",
        lambda context: context.call("grades", context.mixed, [0, 2]),
        _ops("grades"),
    ),
    RenderingCase(
        "squared",
        "squared(a + b)",
        lambda context: context.call("squared", context.sum),
        _ops("squared"),
    ),
    RenderingCase(
        "sqrt",
        "sqrt(exp(0.25 a wedge b))",
        lambda context: context.call("sqrt", context.rotor),
        _ops("sqrt", "exp"),
    ),
    RenderingCase(
        "norm2",
        "norm2(a + b)",
        lambda context: context.call("norm2", context.sum),
        _ops("norm2"),
    ),
    RenderingCase(
        "sandwich",
        "sandwich(exp(0.25 a wedge b), c)",
        lambda context: context.call("sandwich", context.rotor, context.c),
        _ops("sandwich", "exp"),
    ),
    RenderingCase(
        "metric-regressive-product",
        "metric_regressive_product(a wedge b, b wedge c)",
        lambda context: context.call("metric_regressive_product", context.bivector, context.b ^ context.c),
        _ops("metric_regressive_product"),
    ),
    RenderingCase(
        "right-complement-alias",
        "right_complement(a wedge b)",
        lambda context: context.call("right_complement", context.bivector),
        _ops("right_complement"),
    ),
    RenderingCase(
        "left-complement-alias",
        "left_complement(a wedge b)",
        lambda context: context.call("left_complement", context.bivector),
        _ops("left_complement"),
    ),
    RenderingCase(
        "named-literal-deduplication",
        "u := 2 e1 + e2",
        lambda context: 2 * context.basis[0] + context.basis[1],
        _ops("add", "scalar_multiply"),
        result_name="u",
    ),
    RenderingCase(
        "anonymous-expression-value",
        "(a + b) c, anonymous full display",
        lambda context: context.call("geometric_product", context.sum, context.c),
        _ops("geometric_product", "add"),
        result_name=None,
    ),
    RenderingCase(
        "near-zero-value",
        "x := 1 + 1.4524e-16 e1",
        lambda context: context.concrete((1.0, 1.4524e-16, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)),
        result_name="x",
        channels=("value", "full", "rich"),
    ),
    RenderingCase(
        "six-significant-digits",
        "x := 1.23456789 e1",
        lambda context: context.concrete((0.0, 1.23456789, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)),
        result_name="x",
        channels=("value", "full", "rich"),
    ),
    _binary(
        "rga-geometric-product",
        "geometric_product",
        _sum,
        _right_bivector,
        "RGA geometric_product(a + b, b wedge c)",
        profile="lengyel-rga",
    ),
    _binary(
        "rga-metric-inner-product",
        "metric_inner_product",
        _bivector,
        _bivector,
        "RGA metric_inner_product(a wedge b, a wedge b)",
        profile="lengyel-rga",
    ),
    _binary(
        "rga-antidot-product",
        "antidot_product",
        _a,
        _b,
        "RGA antidot_product(a, b)",
        profile="lengyel-rga",
    ),
    _unary(
        "rga-right-weight-dual",
        "right_weight_dual",
        _bivector,
        "RGA right_weight_dual(a wedge b)",
        profile="lengyel-rga",
    ),
    RenderingCase(
        "rga-transwedge",
        "RGA transwedge(a, b, 1)",
        lambda context: context.call("transwedge", context.a, context.b, 1),
        _ops("transwedge"),
        profile="lengyel-rga",
    ),
)
