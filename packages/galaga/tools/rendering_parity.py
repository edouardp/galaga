"""Differential LaTeX rendering audit for the live v1 and v2 algebras.

The case registry is deliberately implementation-neutral.  Each recipe is
built once against a small adapter, then rendered through the retained legacy
engine and the core-backed facade.  Pytest and the Markdown audit command both
consume this module so their inventories and classifications cannot drift.
"""

from __future__ import annotations

import subprocess  # nosec B404 - the audit invokes fixed local Git commands only
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Any, Literal

import numpy as np

import galaga.algebra as legacy
import galaga.facade as facade
from galaga.blade_convention import b_rga
from galaga.facade.catalog import OPERATIONS
from galaga.notation import Notation as LegacyNotation
from galaga.ops import GA_OPS

ImplementationId = Literal["legacy-v1", "core-facade-v2"]
Recipe = Callable[["RenderingContext"], Any]


@dataclass(frozen=True, slots=True)
class RenderingProfile:
    """Equivalent legacy and facade algebra construction policy."""

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


@dataclass(frozen=True, slots=True)
class RenderedResult:
    """Observable output from one implementation."""

    implementation: ImplementationId
    expression: str | None = None
    value: str | None = None
    full: str | None = None
    rich: str | None = None
    coefficients: tuple[float, ...] | None = None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class ChannelDifference:
    """One differing observable channel."""

    channel: str
    legacy: str
    facade: str


@dataclass(frozen=True, slots=True)
class AuditResult:
    """Differential result for one case."""

    case: RenderingCase
    legacy: RenderedResult
    facade: RenderedResult
    differences: tuple[ChannelDifference, ...]
    numeric_match: bool | None

    @property
    def succeeded(self) -> bool:
        return not self.differences and self.legacy.error is None and self.facade.error is None


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
    """Small adapter used by shared expression recipes."""

    __slots__ = ("algebra", "api", "basis", "implementation", "symbols")

    def __init__(
        self,
        implementation: ImplementationId,
        profile: RenderingProfile,
    ) -> None:
        self.implementation = implementation
        if implementation == "legacy-v1":
            self.api: ModuleType = legacy
            if profile.id == "default-cl3":
                self.algebra = legacy.Algebra((1, 1, 1))
            elif profile.id == "lengyel-rga":
                self.algebra = legacy.Algebra(
                    (1, 1, 1, 0),
                    blades=b_rga(),
                    notation=LegacyNotation.lengyel(),
                )
            else:  # pragma: no cover - guarded by public profile lookup
                raise KeyError(profile.id)
            self.basis = self.algebra.basis_vectors(lazy=True)
            self.symbols = tuple(
                value.copy_as(name, latex=name, unicode=name, ascii=name)
                for value, name in zip(self.basis, ("a", "b", "c", "d"), strict=False)
            )
        else:
            self.api = facade
            if profile.id == "default-cl3":
                self.algebra = facade.Algebra(
                    (1, 1, 1),
                    display=facade.DisplayPolicy("full"),
                )
            elif profile.id == "lengyel-rga":
                self.algebra = facade.Algebra(
                    config=facade.p_rga(),
                    display=facade.DisplayPolicy("full"),
                )
            else:  # pragma: no cover - guarded by public profile lookup
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
        legacy_names = {
            "geometric_product": "gp",
            "outer_product": "op",
            "grade_involution": "involute",
        }
        name = legacy_names.get(operation, operation) if self.implementation == "legacy-v1" else operation
        return getattr(self.api, name)(*args)

    def concrete(self, coefficients: Iterable[float]) -> Any:
        data = np.asarray(tuple(coefficients), dtype=np.float64)
        if self.implementation == "legacy-v1":
            return legacy.Multivector(self.algebra, data)
        return self.algebra.multivector(data)

    def name_result(self, value: Any, name: str | None) -> Any:
        if name is None:
            return value
        if self.implementation == "legacy-v1":
            return value.copy_as(name, latex=name, unicode=name, ascii=name)
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
    _unary("conjugate", "conjugate", _sum, "conjugate(a + b)"),
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
    _unary("bulk-part", "bulk_part", _mixed, "bulk_part(1 + a + a wedge b)"),
    _unary("weight-part", "weight_part", _mixed, "weight_part(1 + a + a wedge b)"),
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


# Tests require the observed difference set to equal this reviewed ledger
# exactly. New regressions and resolved differences both demand an explicit
# update, while accepted Galaga 2 corrections remain visible and executable.
DIFFERENCE_LEDGER: Mapping[str, str] = {
    "default-cl3/lie-bracket": (
        "Accepted Galaga 2 correction: lie_bracket is the unscaled commutator and uses the same bracket notation."
    ),
    "default-cl3/jordan-product": (
        "Accepted Galaga 2 correction: jordan_product is the unscaled anticommutator and uses the same brace notation."
    ),
    "default-cl3/reverse-atom": "Accepted Galaga 2 typography: use the consistently wide \\widetilde accent.",
    "default-cl3/outerexp": "Accepted Galaga 2 rendering; legacy v1 raises RecursionError.",
    "default-cl3/outersin": "Accepted Galaga 2 rendering; legacy v1 raises RecursionError.",
    "default-cl3/outercos": "Accepted Galaga 2 rendering; legacy v1 raises RecursionError.",
    "default-cl3/outertan": "Accepted Galaga 2 rendering; legacy v1 raises RecursionError.",
    "default-cl3/grades": (
        "Accepted Galaga 2 improvement: preserve provenance and render a multi-grade projection "
        "as angle brackets subscripted by the selected grade list."
    ),
}


def required_shared_operations() -> frozenset[str]:
    """Return the live legacy registry translated to facade operation IDs."""
    aliases = {
        "gp": "geometric_product",
        "op": "outer_product",
        "involute": "grade_involution",
    }
    translated = {aliases.get(name, name) for name in GA_OPS}
    return frozenset(translated & set(OPERATIONS))


def covered_operations() -> frozenset[str]:
    return frozenset(operation for case in CASES for operation in case.operations)


def audit_case(case: RenderingCase) -> AuditResult:
    """Build and compare one case without raising on an implementation error."""
    profile = PROFILES[case.profile]
    old = _render(case, RenderingContext("legacy-v1", profile))
    new = _render(case, RenderingContext("core-facade-v2", profile))
    differences: list[ChannelDifference] = []
    if old.error is not None or new.error is not None:
        differences.append(ChannelDifference("error", old.error or "none", new.error or "none"))
    else:
        for channel in case.channels:
            old_value = getattr(old, channel)
            new_value = getattr(new, channel)
            if old_value != new_value:
                differences.append(ChannelDifference(channel, old_value or "", new_value or ""))
    numeric_match: bool | None = None
    if old.coefficients is not None and new.coefficients is not None:
        numeric_match = bool(
            np.allclose(
                np.asarray(old.coefficients),
                np.asarray(new.coefficients),
                rtol=1e-12,
                atol=1e-12,
            )
        )
        if not numeric_match:
            differences.append(
                ChannelDifference(
                    "coefficients",
                    repr(old.coefficients),
                    repr(new.coefficients),
                )
            )
    return AuditResult(case, old, new, tuple(differences), numeric_match)


def audit_all(cases: Iterable[RenderingCase] = CASES) -> tuple[AuditResult, ...]:
    """Run every registered differential case."""
    return tuple(audit_case(case) for case in cases)


def _render(case: RenderingCase, context: RenderingContext) -> RenderedResult:
    try:
        value = case.build(context)
        value = context.name_result(value, case.result_name)
        if context.implementation == "legacy-v1":
            expression = value.reveal().latex()
            concrete = value.eval().latex()
            full = value.display().latex()
            rich = value.display()._repr_latex_()
        else:
            expression = value.latex(content="expr")
            concrete = value.latex(content="value")
            full = value.latex()
            rich = value._repr_latex_()
        coefficients = tuple(float(coefficient) for coefficient in value.data)
        return RenderedResult(
            context.implementation,
            expression=expression,
            value=concrete,
            full=full,
            rich=rich,
            coefficients=coefficients,
        )
    except Exception as error:  # noqa: BLE001 - an audit must report both implementations
        return RenderedResult(
            context.implementation,
            error=f"{type(error).__name__}: {error}",
        )


def difference_keys(results: Iterable[AuditResult]) -> frozenset[str]:
    return frozenset(result.case.key for result in results if not result.succeeded)


def _display_math_body(source: str) -> str:
    """Remove a rich-display wrapper before nesting source in display math."""
    if source.startswith("$$") and source.endswith("$$"):
        return source[2:-2]
    if source.startswith("$") and source.endswith("$"):
        return source[1:-1]
    return source


def _full_latex(result: RenderedResult) -> str:
    """Return full teaching-form LaTeX or an honest render-error placeholder."""
    if result.full is not None:
        return _display_math_body(result.full)
    error_kind = (result.error or "no output").partition(":")[0]
    return rf"\text{{render failed: {error_kind}}}"


def render_markdown_report(
    results: Iterable[AuditResult],
    *,
    generated_at: datetime | None = None,
    repository: Path | None = None,
) -> str:
    """Render a Typora-friendly, reviewable audit report."""
    materialized = tuple(results)
    generated = generated_at or datetime.now().astimezone()
    root = repository or Path.cwd()
    succeeded = tuple(result for result in materialized if result.succeeded)
    failed = tuple(result for result in materialized if not result.succeeded)
    commit = _git_metadata(root)
    lines = [
        "<!-- rumdl-disable MD013 MD033 -->",
        "",
        "# Galaga v1/v2 LaTeX Rendering Parity Report",
        "",
        f"Generated: `{generated.isoformat(timespec='seconds')}`",
        f"Repository state: `{commit}`",
        'Primary policy: legacy `Multivector.display()` versus facade `DisplayPolicy("full")`.',
        "",
        "## Summary",
        "",
        "| Result | Count |",
        "|---|---:|",
        f"| Expressions audited | {len(materialized)} |",
        f"| Succeeded | {len(succeeded)} |",
        f"| Different or errored | {len(failed)} |",
        "",
        "A success means expression, concrete value, full teaching display, rich",
        "wrapper, and compatible numeric coefficients all agreed exactly.",
        "",
        "## How to review",
        "",
        "For each difference, compare the rendered forms and check one reviewer",
        "decision. Review the emitted source only when exact LaTeX commands matter.",
        "Add channel-specific exceptions or a preferred third form in the notes.",
        "Save the annotated report; its stable case IDs can then be promoted into",
        "the executable difference ledger and implementation backlog.",
        "",
        "## Successful expressions",
        "",
    ]
    if succeeded:
        for result in succeeded:
            lines.append(f"- `{result.case.key}` — {result.case.intent} — **expression succeeded**")
    else:
        lines.append("No expression succeeded.")
    lines.extend(("", "## Differences", ""))
    if not failed:
        lines.append("No differences were found.")
    for result in failed:
        reviewed_reason = DIFFERENCE_LEDGER.get(result.case.key)
        lines.extend(
            (
                f"### `{result.case.key}`",
                "",
                f"Expression intent: **{result.case.intent}**",
                "",
            )
        )
        legacy_full = _full_latex(result.legacy)
        facade_full = _full_latex(result.facade)
        lines.extend(
            (
                "#### Rendered Expression (v1 vs v2)",
                "",
                "$$",
                legacy_full,
                "",
                "\\" * 5,
                "",
                facade_full,
                "$$",
                "",
                "#### Emitted Latex (v1 vs v2)",
                "",
                "```latex",
                legacy_full,
                "",
                facade_full,
                "```",
                "",
                "#### Reviewer decision",
                "",
                f"- [{'x' if reviewed_reason else ' '}] Accept v2",
                "- [ ] Match legacy v1",
                "- [ ] Prefer another rendering",
                "- [ ] Investigate as defect",
                "",
                "Reviewer notes:",
                "",
                f"> {reviewed_reason or 'Add review notes here.'}",
                "",
            )
        )
    lines.extend(
        (
            "## Coverage",
            "",
            f"- Shared registered legacy/facade operations: {len(required_shared_operations())}",
            f"- Shared registered operations exercised: {len(required_shared_operations() & covered_operations())}",
            f"- Total operation IDs exercised, including structural helpers: {len(covered_operations())}",
            "",
        )
    )
    missing = sorted(required_shared_operations() - covered_operations())
    if missing:
        lines.append(f"Missing shared operations: `{', '.join(missing)}`")
    else:
        lines.append("Every shared registered expression operation has at least one case.")
    lines.append("")
    return "\n".join(lines)


def write_markdown_report(
    results: Iterable[AuditResult],
    output: Path,
    *,
    generated_at: datetime | None = None,
    repository: Path | None = None,
) -> Path:
    """Write one complete Markdown report and return its resolved path."""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        render_markdown_report(results, generated_at=generated_at, repository=repository),
        encoding="utf-8",
    )
    return output.resolve()


def default_report_path(repository: Path, generated_at: datetime | None = None) -> Path:
    generated = generated_at or datetime.now().astimezone()
    stamp = generated.strftime("%Y%m%d-%H%M%S%z")
    return repository / "docs" / "v2" / "rendering-parity-reports" / f"latex-parity-{stamp}.md"


def _git_metadata(repository: Path) -> str:
    try:
        branch = subprocess.run(  # nosec B603 - fixed executable and arguments
            ("git", "branch", "--show-current"),
            cwd=repository,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        commit = subprocess.run(  # nosec B603 - fixed executable and arguments
            ("git", "rev-parse", "--short", "HEAD"),
            cwd=repository,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        dirty = subprocess.run(  # nosec B603 - fixed executable and arguments
            ("git", "status", "--short"),
            cwd=repository,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"
    return f"{branch}@{commit}{' (dirty)' if dirty else ''}"


__all__ = [
    "CASES",
    "DIFFERENCE_LEDGER",
    "PROFILES",
    "AuditResult",
    "ChannelDifference",
    "RenderedResult",
    "RenderingCase",
    "RenderingContext",
    "RenderingProfile",
    "audit_all",
    "audit_case",
    "covered_operations",
    "default_report_path",
    "difference_keys",
    "render_markdown_report",
    "required_shared_operations",
    "write_markdown_report",
]
