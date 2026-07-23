"""Executable ownership and disposition matrix for the Galaga v1 surface."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SurfaceDisposition:
    owner: str
    action: str
    target: str
    milestone: str
    warning: str | None = None


def _rows(
    names: set[str],
    *,
    owner: str,
    action: str,
    milestone: str,
    target_prefix: str,
    warning: str | None = None,
) -> dict[str, SurfaceDisposition]:
    return {name: SurfaceDisposition(owner, action, f"{target_prefix}{name}", milestone, warning) for name in names}


def _merge(*groups: dict[str, SurfaceDisposition]) -> dict[str, SurfaceDisposition]:
    result: dict[str, SurfaceDisposition] = {}
    for group in groups:
        overlap = set(result) & set(group)
        if overlap:
            raise RuntimeError(f"duplicate v1 surface classification: {sorted(overlap)}")
        result.update(group)
    return result


_PRESENTATION_EXPORTS = {
    "BasisBlade",
    "BladeConvention",
    "Notation",
    "b_cga",
    "b_complex",
    "b_default",
    "b_gamma",
    "b_pga",
    "b_quaternion",
    "b_rga",
    "b_sigma",
    "b_sigma_xyz",
    "b_sta",
}

_CANONICAL_NUMERIC_EXPORTS = {
    "antidot_product",
    "anticommutator",
    "antimetric_apply",
    "antireverse",
    "antiwedge",
    "bulk_part",
    "commutator",
    "complement",
    "conjugate",
    "doran_lasenby_inner",
    "dual",
    "even_grades",
    "exp",
    "geometric_antiproduct",
    "geometric_product",
    "grade",
    "grade_involution",
    "grades",
    "hestenes_inner",
    "inverse",
    "is_basis_blade",
    "is_bivector",
    "is_even",
    "is_rotor",
    "is_scalar",
    "is_vector",
    "jordan_product",
    "left_complement",
    "left_contraction",
    "left_hodge_dual",
    "left_interior_product",
    "left_weight_dual",
    "lie_bracket",
    "log",
    "metric_apply",
    "metric_inner_product",
    "metric_regressive_product",
    "norm",
    "norm2",
    "odd_grades",
    "outer_product",
    "outercos",
    "outerexp",
    "outersin",
    "outertan",
    "regressive_product",
    "reverse",
    "right_complement",
    "right_contraction",
    "right_hodge_dual",
    "right_interior_product",
    "right_weight_dual",
    "sandwich",
    "scalar_product",
    "scalar_sqrt",
    "sqrt",
    "squared",
    "transwedge",
    "transwedge_antiproduct",
    "uncomplement",
    "undual",
    "unit",
    "weight_part",
}

CURATED_OPERATION_ALIASES = {
    "dorst_inner": "doran_lasenby_inner",
    "gp": "geometric_product",
    "join": "outer_product",
    "meet": "regressive_product",
    "op": "outer_product",
    "rev": "reverse",
    "sw": "sandwich",
    "wedge": "outer_product",
}

TEMPORARY_OPERATION_ALIASES = {
    "involute": "grade_involution",
    "mag2": "norm2",
    "magnitude_squared": "norm2",
    "normalise": "unit",
    "normalize": "unit",
    "norm_squared": "norm2",
}


TOP_LEVEL_EXPORTS = _merge(
    {
        "Algebra": SurfaceDisposition("facade", "replace", "galaga.facade.Algebra", "phase-2"),
        "Multivector": SurfaceDisposition("facade", "replace", "galaga.facade.Multivector", "phase-2"),
    },
    _rows(
        _PRESENTATION_EXPORTS,
        owner="presentation",
        action="redesign",
        milestone="phase-4",
        target_prefix="galaga.presentation.",
    ),
    _rows(
        {"simplify", "sym"},
        owner="expression",
        action="redesign",
        milestone="phase-5",
        target_prefix="galaga.expression.",
    ),
    _rows(
        _CANONICAL_NUMERIC_EXPORTS,
        owner="facade",
        action="replace",
        milestone="phase-2",
        target_prefix="galaga.facade.",
    ),
    {
        alias: SurfaceDisposition(
            "compatibility",
            "curated-alias",
            f"galaga.facade.{canonical}",
            "permanent",
        )
        for alias, canonical in CURATED_OPERATION_ALIASES.items()
    },
    {
        alias: SurfaceDisposition(
            "compatibility",
            "deprecated-alias",
            f"galaga.facade.{canonical}",
            "phase-9",
            f"{alias} is deprecated in Galaga 2; use {canonical}",
        )
        for alias, canonical in TEMPORARY_OPERATION_ALIASES.items()
    },
    {
        name: SurfaceDisposition(
            "compatibility",
            "remove-redundant-helper",
            "explicit primitive composition or a model-specific geometry API",
            "phase-9",
            f"{name} is not part of the Galaga 2 numeric facade; "
            "compose explicit operations or use a model-specific geometry helper",
        )
        for name in ("project", "reflect", "reject")
    },
    {
        name: SurfaceDisposition(
            "compatibility",
            "deprecated-adapter",
            "explicit named inner-product variant",
            "phase-9",
            f"{name} is deprecated in Galaga 2; import an explicit inner-product function",
        )
        for name in ("inner_product", "ip")
    },
)


ALGEBRA_SPECIAL_METHODS = frozenset({"__init__", "__repr__"})


ALGEBRA_MEMBERS = _merge(
    _rows(
        {
            "I",
            "basis_blades",
            "basis_vectors",
            "dim",
            "extended_metric_matrix",
            "identity",
            "metric_antiexomorphism_matrix",
            "n",
            "pseudoscalar",
            "scalar",
            "signature",
            "vector",
        },
        owner="facade",
        action="replace",
        milestone="phase-2",
        target_prefix="galaga.facade.Algebra.",
    ),
    _rows(
        {"blade", "get_basis_blade", "locals", "notation"},
        owner="presentation",
        action="redesign",
        milestone="phase-4",
        target_prefix="galaga.facade.Algebra.",
    ),
    _rows(
        {"frac", "fraction", "rotor", "rotor_from_bivector", "rotor_from_plane_angle"},
        owner="helper",
        action="composition",
        milestone="phase-7",
        target_prefix="galaga.helpers.",
    ),
    {
        name: SurfaceDisposition(
            "helper",
            "remove-member",
            "explicit domain helper or algebra.scalar(value)",
            "phase-9",
            f"Algebra.{name} is removed from the Galaga 2 kernel",
        )
        for name in ("c", "e", "h", "hbar", "pi", "sqrt2", "tau")
    },
)


MULTIVECTOR_MEMBERS = _merge(
    _rows(
        {"algebra", "data", "homogeneous_grade", "vector_part"},
        owner="facade",
        action="replace",
        milestone="phase-2",
        target_prefix="galaga.facade.Multivector.",
    ),
    _rows(
        {"anon", "copy_as", "eager", "eval", "lazy", "name", "numeric", "reveal", "symbolic"},
        owner="expression",
        action="redesign-nonmutating",
        milestone="phase-5",
        target_prefix="galaga.facade.Multivector.",
    ),
    _rows(
        {"display", "latex"},
        owner="rendering",
        action="redesign",
        milestone="phase-6",
        target_prefix="galaga.rendering.",
    ),
    {
        name: SurfaceDisposition(
            "compatibility",
            "curated-convenience",
            target,
            "phase-7",
        )
        for name, target in {
            "bar": "galaga.facade.grade_involution",
            "dag": "galaga.facade.reverse",
            "inv": "galaga.facade.inverse",
            "sq": "galaga.facade.squared",
        }.items()
    },
    {
        "scalar_part": SurfaceDisposition(
            "compatibility",
            "remove-member",
            "galaga.facade.scalar_part(value) or float(grade(value, 0))",
            "phase-9",
            "Multivector.scalar_part is removed in Galaga 2; use scalar_part(value)",
        )
    },
)


V1_MULTIVECTOR_SPECIAL_METHODS = frozenset(
    {
        "__init__",
        "__abs__",
        "__add__",
        "__eq__",
        "__float__",
        "__format__",
        "__getitem__",
        "__hash__",
        "__invert__",
        "__mul__",
        "__neg__",
        "__or__",
        "__pow__",
        "__radd__",
        "__repr__",
        "__rmul__",
        "__rsub__",
        "__rtruediv__",
        "__str__",
        "__sub__",
        "__truediv__",
        "__xor__",
    }
)


V2_MULTIVECTOR_PROTOCOL_ADDITIONS = frozenset({"__pos__", "__ror__", "__rxor__"})


V2_MULTIVECTOR_SPECIAL_METHODS = V1_MULTIVECTOR_SPECIAL_METHODS | V2_MULTIVECTOR_PROTOCOL_ADDITIONS


MULTIVECTOR_FORMATTING_HOOKS = _merge(
    {
        "__repr__": SurfaceDisposition(
            "facade",
            "numeric-shell-then-rendering",
            "galaga.facade.Multivector.__repr__",
            "phase-6",
        )
    },
    _rows(
        {"__format__", "__str__", "_repr_latex_", "display", "latex"},
        owner="rendering",
        action="redesign",
        milestone="phase-6",
        target_prefix="galaga.rendering.",
    ),
)


ALGEBRA_CONSTRUCTION_FORMS = {
    "legacy-signature-positional": "Algebra((1, -1, 0))",
    "legacy-empty-signature-positional": "Algebra(())",
    "legacy-pqr-positional": "Algebra(2, 1, 0)",
    "signature-keyword": "Algebra(signature=(1, -1, 0))",
    "signature-short-keyword": "Algebra(sig=(1, -1, 0))",
    "diagonal-gram-keyword": "Algebra(gram=((2.0, 0.0), (0.0, -3.0)))",
    "full-gram-keyword": "Algebra(gram=((1.0, 0.25), (0.25, 1.0)))",
}


ALGEBRA_CONSTRUCTOR_PARAMETERS = {
    "p_or_signature": SurfaceDisposition("facade", "replace", "p or positional signature", "phase-2"),
    "q": SurfaceDisposition("facade", "replace", "q", "phase-2"),
    "r": SurfaceDisposition("facade", "replace", "r", "phase-2"),
    "blades": SurfaceDisposition("presentation", "redesign", "AlgebraConfig.blade_convention", "phase-4"),
    "repr_unicode": SurfaceDisposition("presentation", "redesign", "PresentationConfig.default_target", "phase-4"),
    "notation": SurfaceDisposition("presentation", "redesign", "PresentationConfig.notation", "phase-4"),
    "display_repr": SurfaceDisposition("presentation", "redesign", "PresentationConfig.display_mode", "phase-4"),
}


OPERATION_CALL_FORMS = {
    "variadic-geometric-product": "geometric_product(first, *rest)",
    "variadic-outer-product": "outer_product(first, *rest)",
    "binary-inner-products": "explicit_inner_product(left, right)",
    "unary-involutions": "involution(value)",
    "parameterized-grade": "grade(value, target)",
}


EXPRESSION_NODE_CLASSES = {
    "Expr": SurfaceDisposition("expression", "retain-base", "galaga.expression.Expr", "phase-5"),
    "Scalar": SurfaceDisposition("expression", "replace", "galaga.expression.ScalarLiteral", "phase-5"),
    "Sym": SurfaceDisposition("expression", "replace", "galaga.expression.Symbol", "phase-5"),
}

for _node_name in {
    "Add",
    "AntidotProduct",
    "Anticommutator",
    "AntimetricApply",
    "Antireverse",
    "BulkPart",
    "Commutator",
    "Complement",
    "Conjugate",
    "Div",
    "Dli",
    "Dual",
    "Even",
    "Exp",
    "GeometricAntiproduct",
    "Gp",
    "Grade",
    "Hi",
    "Inverse",
    "Involute",
    "JordanProduct",
    "Lc",
    "LeftHodgeDual",
    "LeftInteriorProduct",
    "LeftWeightDual",
    "LieBracket",
    "Log",
    "MetricApply",
    "MetricInnerProduct",
    "Neg",
    "Norm",
    "Norm2",
    "Odd",
    "Op",
    "OuterCos",
    "OuterExp",
    "OuterSin",
    "OuterTan",
    "Rc",
    "Regressive",
    "RightHodgeDual",
    "RightInteriorProduct",
    "RightWeightDual",
    "ScalarDiv",
    "ScalarMul",
    "Sp",
    "Sqrt",
    "Squared",
    "Sub",
    "Transwedge",
    "TranswedgeAntiproduct",
    "Uncomplement",
    "Undual",
    "Unit",
    "WeightPart",
    "Reverse",
}:
    EXPRESSION_NODE_CLASSES[_node_name] = SurfaceDisposition(
        "compatibility",
        "deprecated-constructor-adapter",
        "galaga.expression.Call(operation_id, operands)",
        "phase-9",
        f"galaga.expr.{_node_name} is deprecated; construct expressions through facade operations",
    )


SUPPORTED_SUBMODULES = {
    "galaga.algebra": SurfaceDisposition("compatibility", "privatize", "galaga.facade", "phase-8"),
    "galaga.basis_blade": SurfaceDisposition("presentation", "compatibility-reexport", "galaga.blades", "phase-7"),
    "galaga.blade_convention": SurfaceDisposition("presentation", "compatibility-reexport", "galaga.blades", "phase-7"),
    "galaga.blades": SurfaceDisposition("presentation", "retain", "galaga.blades", "permanent"),
    "galaga.cga": SurfaceDisposition("model", "retain", "galaga.cga", "permanent"),
    "galaga.core": SurfaceDisposition("core", "retain", "galaga.core", "permanent"),
    "galaga.display": SurfaceDisposition("rendering", "retain", "galaga.display", "permanent"),
    "galaga.expr": SurfaceDisposition("expression", "compatibility-reexport", "galaga.expression", "phase-7"),
    "galaga.expression": SurfaceDisposition("expression", "retain", "galaga.expression", "permanent"),
    "galaga.facade": SurfaceDisposition("facade", "retain", "galaga.facade", "permanent"),
    "galaga.facade.catalog": SurfaceDisposition("facade", "retain", "galaga.facade.catalog", "permanent"),
    "galaga.gram_bridge": SurfaceDisposition(
        "compatibility",
        "deprecated-reexport",
        "galaga.facade",
        "phase-9",
        "galaga.gram_bridge is deprecated; import galaga.facade",
    ),
    "galaga.gram_bridge.catalog": SurfaceDisposition(
        "compatibility",
        "deprecated-reexport",
        "galaga.facade.catalog",
        "phase-9",
        "galaga.gram_bridge.catalog is deprecated; import galaga.facade.catalog",
    ),
    "galaga.gram_bridge.facade": SurfaceDisposition(
        "compatibility",
        "deprecated-reexport",
        "galaga.facade",
        "phase-9",
        "galaga.gram_bridge.facade is deprecated; import galaga.facade",
    ),
    "galaga.legacy": SurfaceDisposition(
        "compatibility",
        "temporary-v1-oracle",
        "galaga.legacy",
        "phase-9",
    ),
    "galaga.latex_build": SurfaceDisposition("rendering", "compatibility-reexport", "galaga.rendering", "phase-7"),
    "galaga.latex_emit": SurfaceDisposition("rendering", "compatibility-reexport", "galaga.rendering", "phase-7"),
    "galaga.latex_nodes": SurfaceDisposition("rendering", "compatibility-reexport", "galaga.rendering", "phase-7"),
    "galaga.latex_rewrite": SurfaceDisposition("rendering", "compatibility-reexport", "galaga.rendering", "phase-7"),
    "galaga.latex_symbols": SurfaceDisposition("rendering", "compatibility-reexport", "galaga.rendering", "phase-7"),
    "galaga.lazy": SurfaceDisposition(
        "compatibility",
        "deprecated-reexport",
        "galaga expression provenance API",
        "phase-9",
        "galaga.lazy is deprecated; use expression provenance",
    ),
    "galaga.names": SurfaceDisposition("presentation", "retain", "galaga.names", "permanent"),
    "galaga.notation": SurfaceDisposition("presentation", "compatibility-reexport", "galaga.notation", "phase-7"),
    "galaga.ops": SurfaceDisposition("facade", "redesign", "galaga.facade.catalog", "phase-5"),
    "galaga.presentation": SurfaceDisposition("presentation", "retain", "galaga.presentation", "permanent"),
    "galaga.presets": SurfaceDisposition("presentation", "retain", "galaga.presets", "permanent"),
    "galaga.rga": SurfaceDisposition("model", "retain", "galaga.rga", "permanent"),
    "galaga.legacy.render": SurfaceDisposition(
        "compatibility",
        "temporary-v1-oracle",
        "galaga.legacy.render",
        "phase-9",
    ),
    "galaga.rendering": SurfaceDisposition("rendering", "retain", "galaga.rendering", "permanent"),
    "galaga.legacy.simplify": SurfaceDisposition(
        "compatibility", "temporary-v1-oracle", "galaga.legacy.simplify", "phase-9"
    ),
    "galaga.symbolic": SurfaceDisposition(
        "compatibility",
        "deprecated-reexport",
        "galaga.expr and galaga.facade",
        "phase-9",
        "galaga.symbolic is deprecated; use facade operations on expression-tracked values",
    ),
    "galaga.symbolic_core": SurfaceDisposition("expression", "consolidate", "galaga.expression", "phase-7"),
    "galaga.symbolic_core.domain": SurfaceDisposition("expression", "consolidate", "galaga.expression", "phase-7"),
    "galaga.symbolic_core.expr": SurfaceDisposition("expression", "consolidate", "galaga.expression", "phase-7"),
    "galaga.symbolic_core.naming": SurfaceDisposition("expression", "consolidate", "galaga.expression", "phase-7"),
    "galaga.symbolic_core.render": SurfaceDisposition("rendering", "consolidate", "galaga.rendering", "phase-7"),
}


TOP_LEVEL_PACKAGE_MODULES = frozenset(
    {
        "galaga.algebra",
        "galaga.basis_blade",
        "galaga.blade_convention",
        "galaga.blades",
        "galaga.cga",
        "galaga.core",
        "galaga.display",
        "galaga.expr",
        "galaga.expression",
        "galaga.facade",
        "galaga.gram_bridge",
        "galaga.legacy",
        "galaga.latex_build",
        "galaga.latex_emit",
        "galaga.latex_nodes",
        "galaga.latex_rewrite",
        "galaga.latex_symbols",
        "galaga.lazy",
        "galaga.names",
        "galaga.notation",
        "galaga.ops",
        "galaga.presentation",
        "galaga.presets",
        "galaga.rga",
        "galaga.rendering",
        "galaga.symbolic",
        "galaga.symbolic_core",
    }
)


COMPANION_TOUCHPOINTS = {
    "galaga_matrix": SurfaceDisposition(
        "integration", "numeric-migrated", "facade/core public linear actions", "phase-7-in-progress"
    ),
    "galaga_marimo": SurfaceDisposition(
        "integration", "migrated", "galaga facade display protocol", "phase-7-complete"
    ),
    "galaga_mermaid": SurfaceDisposition(
        "integration", "migrated", "galaga facade expression protocol", "phase-7-complete"
    ),
    "examples": SurfaceDisposition("integration", "migrate", "top-level Galaga 2 API", "phase-7"),
}


ACCIDENTAL_PRIVATE_DEPENDENCIES = {
    "galaga_matrix:Algebra._mul_index/_mul_sign": SurfaceDisposition(
        "integration",
        "replaced-private-table-access",
        "galaga.core.Algebra.left_action and public linear-action APIs",
        "phase-7-complete",
    ),
    "galaga_matrix:Multivector._to_expr/_expr/_is_symbolic": SurfaceDisposition(
        "expression",
        "replace-private-expression-access",
        "public expression provenance protocol",
        "phase-7",
    ),
    "galaga_mermaid:Expr internals/Multivector._to_expr": SurfaceDisposition(
        "rendering",
        "replaced-private-expression-access",
        "public expression traversal protocol",
        "phase-7-complete",
    ),
    "examples:Multivector._is_lazy/_name": SurfaceDisposition(
        "expression",
        "replace-private-state-demonstration",
        "immutable name and expression provenance API",
        "phase-7",
    ),
}


V2_ADDITIONS = {
    "half_anticommutator",
    "half_commutator",
    "scalar_part",
}
