"""galaga_annotation — semantic annotations and KaTeX rendering for galaga.

Immutable rules, callable annotators, and a first KaTeX renderer for
expressions, values and multivector components. This package is optional:
importing ``galaga`` never imports ``galaga_annotation``.
"""

from .annotator import Annotator, annotate, annotator
from .cga import CGAObject, HighlightDecomposition, cga_parts, classify_cga, highlight_cga
from .katex import KatexResult, LabelPlacement, SpanLayoutError, render_katex
from .model import Annotation, AnnotationStyle, on
from .plan import AnnotationPlan, MissingTargetError, Placement, resolve
from .presenter import AnnotationPresenter
from .targets import (
    CoefficientTarget,
    ExpressionPath,
    GradeTarget,
    OperationTarget,
    TermTarget,
    VariableTarget,
    WholeExpression,
    blade_mask,
    coefficient,
    coefficients,
    grade,
    grades,
    operand,
    operator,
    path,
    term,
    terms,
    variable,
    whole,
)
from .view import Annotated

__all__ = [
    "Annotation",
    "AnnotationPlan",
    "AnnotationPresenter",
    "AnnotationStyle",
    "Annotated",
    "Annotator",
    "CGAObject",
    "CoefficientTarget",
    "ExpressionPath",
    "GradeTarget",
    "HighlightDecomposition",
    "KatexResult",
    "LabelPlacement",
    "MissingTargetError",
    "OperationTarget",
    "Placement",
    "SpanLayoutError",
    "TermTarget",
    "VariableTarget",
    "WholeExpression",
    "annotate",
    "annotator",
    "blade_mask",
    "cga_parts",
    "classify_cga",
    "coefficient",
    "coefficients",
    "grade",
    "grades",
    "highlight_cga",
    "on",
    "operand",
    "operator",
    "path",
    "render_katex",
    "resolve",
    "term",
    "terms",
    "variable",
    "whole",
]
