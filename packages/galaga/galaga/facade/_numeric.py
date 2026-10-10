"""Composition facade over :mod:`galaga.core`.

Facade values remain eager numeric wrappers. Facade algebras additionally own
immutable presentation configuration and context-local selection. Optional
expression provenance records how an eager value was obtained without changing
numeric evaluation.
"""

from __future__ import annotations

from collections.abc import Generator, Iterable, Iterator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from numbers import Integral, Real
from types import MappingProxyType, NotImplementedType
from typing import TYPE_CHECKING, Any, cast

import numpy as np

from .. import core
from ..blades import BladeConvention, BladeLabel, BladePatch, BladeRef, DisplayOrder, LocalNamePolicy
from ..composition import ConfiguredPreset, NotationPatch, PresentationRecipe, _as_recipe, resolve_blades
from ..config import apply_defaults
from ..config import load as load_user_config
from ..expression._nodes import BladeLiteral, Call, Expr, MultivectorLiteral, ScalarLiteral, Symbol
from ..names import Name
from ..presentation import (
    AlgebraConfig,
    AlgebraDefinition,
    DisplayPolicy,
    ModelConfig,
    Notation,
    PresentationConfig,
    default_presentation,
)
from ..rendering._emit import _number
from .catalog import LeftFoldCall, get_operation

if TYPE_CHECKING:
    from ..display import BilinearFormTable, PresentationTable, WedgeProductTable
    from ..presets import BladePreset, Preset


class Algebra:
    """An eager algebra with configurable presentation and factory tracking.

    ``expr=True`` makes public value factories infer expression provenance by
    default. Per-factory ``expr=False`` opts out; omitted or ``None`` inherits.
    This facade policy does not alter numeric evaluation or operation dispatch.
    ``user_config_files=False`` skips ambient presentation preferences for
    this algebra; the default is to load them. ``config="@name"`` explicitly
    selects a named algebra from those files.
    """

    __slots__ = (
        "_basis_vectors",
        "_basis_vector_views",
        "_default_presentation",
        "_expr",
        "_model",
        "_numeric",
        "_presentation_override",
    )

    def __init__(
        self,
        *args: Any,
        config: AlgebraConfig | Preset | str | None = None,
        expr: bool = False,
        user_config_files: bool = True,
        presentation: (
            PresentationConfig
            | PresentationRecipe
            | BladeConvention
            | BladePreset
            | BladePatch
            | Notation
            | NotationPatch
            | LocalNamePolicy
            | DisplayOrder
            | DisplayPolicy
            | None
        ) = None,
        blades: BladeConvention | BladePreset | BladePatch | PresentationRecipe | None = None,
        notation: Notation | NotationPatch | None = None,
        local_names: LocalNamePolicy | None = None,
        display_order: DisplayOrder | None = None,
        display: DisplayPolicy | None = None,
        **kwargs: Any,
    ) -> None:
        _require_expr_flag(expr)
        if not isinstance(user_config_files, bool):
            raise TypeError("user_config_files must be a boolean")
        self._expr = expr
        if config is not None:
            if args or kwargs:
                conflicting = [repr(value) for value in args]
                conflicting.extend(f"{name}=" for name in sorted(kwargs))
                details = ", ".join(conflicting)
                raise TypeError(f"config= defines the numeric algebra and cannot be combined with {details}")
            if isinstance(config, str):
                if not config.startswith("@") or len(config) == 1 or config[1] == "@":
                    raise ValueError("config string must be a named algebra reference such as '@name'")
                if not user_config_files:
                    raise ValueError("config='@name' requires user_config_files=True")
                config = load_user_config().algebra(config[1:])
            if isinstance(config, ConfiguredPreset):
                expanded = _expand_config(config.base)
                if user_config_files and not isinstance(config.base, AlgebraConfig):
                    expanded = expanded.with_presentation(
                        apply_defaults(expanded.presentation, expanded.definition.gram)
                    )
                expanded = config.presentation.apply(expanded)
            else:
                expanded = _expand_config(config)
                if user_config_files and not isinstance(config, AlgebraConfig):
                    expanded = expanded.with_presentation(
                        apply_defaults(expanded.presentation, expanded.definition.gram)
                    )
            self._numeric = _numeric_from_definition(expanded.definition)
            base_presentation = expanded.presentation
            self._model = expanded.model
        else:
            if args and isinstance(args[0], (tuple, list)):
                if len(args) != 1:
                    raise TypeError("a positional signature cannot be combined with q or r")
                if "signature" in kwargs or "sig" in kwargs or "gram" in kwargs:
                    raise TypeError("a positional signature cannot be combined with signature, sig, or gram")
                positional_signature = args[0]
                if len(positional_signature) == 0:
                    if kwargs.get("q", 0) != 0 or kwargs.get("r", 0) != 0:
                        raise TypeError("a positional signature cannot be combined with q or r")
                    args = (0,)
                else:
                    kwargs["signature"] = positional_signature
                    args = ()
            self._numeric = core.Algebra(*args, **kwargs)
            base_presentation = default_presentation(self._numeric.n)
            if user_config_files:
                base_presentation = apply_defaults(base_presentation, self._numeric.gram)
            self._model = None

        if presentation is not None:
            if isinstance(presentation, PresentationConfig):
                base_presentation = presentation
            else:
                recipe = _as_recipe(presentation)
                if recipe is None:
                    raise TypeError("presentation must be a PresentationConfig or presentation recipe component")
                base_presentation = recipe.apply_to(base_presentation, self._numeric.gram)
        if blades is not None:
            blades = resolve_blades(blades, self._numeric.gram, base_presentation.blades)
        self._default_presentation = _override_presentation(
            base_presentation,
            blades=blades,
            notation=notation,
            local_names=local_names,
            display_order=display_order,
            display=display,
        )
        if self._default_presentation.dimension != self._numeric.n:
            raise ValueError(
                "presentation dimension "
                f"{self._default_presentation.dimension} does not match numeric dimension {self._numeric.n}"
            )
        self._basis_vectors: tuple[Multivector, ...] | None = None
        self._basis_vector_views: dict[PresentationConfig, BasisMultivectors] = {}
        self._presentation_override: ContextVar[PresentationConfig | None] = ContextVar(
            f"galaga_presentation_{id(self)}",
            default=None,
        )

    @classmethod
    def from_numeric(
        cls,
        numeric: core.Algebra,
        *,
        presentation: PresentationConfig | None = None,
        model: ModelConfig | None = None,
        expr: bool = False,
        user_config_files: bool = True,
    ) -> Algebra:
        """Create a facade over an existing numeric algebra."""
        if not isinstance(numeric, core.Algebra):
            raise TypeError("numeric must be a core.Algebra")
        _require_expr_flag(expr)
        if not isinstance(user_config_files, bool):
            raise TypeError("user_config_files must be a boolean")
        if presentation is None:
            selected = default_presentation(numeric.n)
            if user_config_files:
                selected = apply_defaults(selected, numeric.gram)
        else:
            selected = _require_presentation(presentation)
        if selected.dimension != numeric.n:
            raise ValueError(
                f"presentation dimension {selected.dimension} does not match numeric dimension {numeric.n}"
            )
        if model is not None:
            limit = 1 << numeric.n
            for name, ref in model.roles:
                if ref.mask >= limit:
                    raise ValueError(f"model role {name!r} refers to mask {ref.mask} outside the algebra dimension")
        instance = cls.__new__(cls)
        instance._numeric = numeric
        instance._expr = expr
        instance._basis_vectors = None
        instance._basis_vector_views = {}
        instance._default_presentation = selected
        instance._model = model
        instance._presentation_override = ContextVar(
            f"galaga_presentation_{id(instance)}",
            default=None,
        )
        return instance

    @property
    def numeric(self) -> core.Algebra:
        """The wrapped numeric algebra."""
        return self._numeric

    @property
    def expr(self) -> bool:
        """Whether public value factories infer provenance by default."""
        return self._expr

    def _resolve_expr(self, expr: bool | None) -> bool:
        if expr is None:
            return self._expr
        _require_expr_flag(expr)
        return expr

    @property
    def default_presentation(self) -> PresentationConfig:
        """The persistent presentation for this cheap algebra view."""
        return self._default_presentation

    @property
    def presentation(self) -> PresentationConfig:
        """The context-local presentation currently in effect."""
        return self._presentation_override.get() or self._default_presentation

    @property
    def model(self) -> ModelConfig | None:
        """Optional semantic model metadata supplied by a complete config."""
        return self._model

    def resolve_presentation(self, explicit: PresentationConfig | None = None) -> PresentationConfig:
        """Resolve explicit, scoped, and persistent presentation precedence."""
        if explicit is None:
            return self.presentation
        selected = _require_presentation(explicit)
        if selected.dimension != self.n:
            raise ValueError(f"presentation dimension {selected.dimension} does not match numeric dimension {self.n}")
        return selected

    def with_presentation(self, presentation: PresentationConfig | PresentationRecipe) -> Algebra:
        """Return a cheap view with a complete presentation or applied recipe."""
        selected = (
            presentation.apply_to(self.presentation, self.gram)
            if isinstance(presentation, PresentationRecipe)
            else self.resolve_presentation(presentation)
        )
        return Algebra.from_numeric(
            self._numeric,
            presentation=selected,
            model=self._model,
            expr=self._expr,
        )

    def with_blades(self, blades: BladeConvention | BladePreset | BladePatch | PresentationRecipe) -> Algebra:
        if blades is None:
            raise TypeError("blades must be a BladeConvention, BladePatch, or resolvable blade preset")
        resolved = resolve_blades(blades, self._numeric.gram, self.presentation.blades)
        return self.with_presentation(self.presentation.with_blades(resolved))

    def with_notation(self, notation: Notation | NotationPatch) -> Algebra:
        selected = notation.apply(self.presentation.notation) if isinstance(notation, NotationPatch) else notation
        return self.with_presentation(self.presentation.with_notation(selected))

    def with_local_names(self, local_names: LocalNamePolicy) -> Algebra:
        return self.with_presentation(self.presentation.with_local_names(local_names))

    def with_display_order(self, display_order: DisplayOrder) -> Algebra:
        return self.with_presentation(self.presentation.with_display_order(display_order))

    def with_display(self, display: DisplayPolicy) -> Algebra:
        return self.with_presentation(self.presentation.with_display(display))

    @contextmanager
    def use_presentation(self, presentation: PresentationConfig | PresentationRecipe) -> Generator[Algebra, None, None]:
        """Temporarily select a complete presentation or apply a recipe."""
        selected = (
            presentation.apply_to(self.presentation, self.gram)
            if isinstance(presentation, PresentationRecipe)
            else self.resolve_presentation(presentation)
        )
        token = self._presentation_override.set(selected)
        try:
            yield self
        finally:
            self._presentation_override.reset(token)

    @contextmanager
    def use_notation(self, notation: Notation | NotationPatch) -> Generator[Algebra, None, None]:
        """Temporarily replace only the current presentation's notation.

        Other presentation components, including enclosing scoped overrides,
        are preserved. Render inside the scope to use the selected notation;
        results do not capture it for later display.
        """
        selected = notation.apply(self.presentation.notation) if isinstance(notation, NotationPatch) else notation
        with self.use_presentation(self.presentation.with_notation(selected)):
            yield self

    @property
    def gram(self) -> np.ndarray:
        return cast(np.ndarray, self._numeric.gram)

    def bilinear_form_table(self, full: bool = False) -> BilinearFormTable:
        """Return a notebook-ready labelled metric-pairing table.

        By default show the stored Gram matrix in native vector order.
        With full=True, include scalar 1 and every native exterior blade in
        active display order, pairing rows and columns with
        metric_inner_product(A, B) = <A * ~B>_0, not scalar_product(A, B).
        A full table has 4**n cells and uses the existing extended metric.

        Capture active labels and coefficient precision. Exact zeros render
        in grey (#bbbbbb); tiny nonzeros are never elided. This is a
        presentation snapshot, not a matrix representation of multiplication.
        """
        from ..display import BilinearFormTable
        from ..rendering._build import bilinear_form_tree

        if not isinstance(full, bool):
            raise TypeError("full must be a boolean")
        selected = self.presentation
        if full:
            masks = selected.display_order.masks
            matrix = self.extended_metric_matrix()[np.ix_(masks, masks)]
            tree = bilinear_form_tree(matrix, selected, masks=masks)
        else:
            tree = bilinear_form_tree(self.gram, selected)
        return BilinearFormTable(tree, target=selected.display.target)

    def wedge_product_table(
        self, full: bool = False, *, color: bool = False, colour: bool = False
    ) -> WedgeProductTable:
        """Return a rich-display table of row blade wedged with column blade.

        By default the axes contain native basis vectors. With full=True,
        include scalar 1 and every native exterior blade in the active
        presentation's display order, including preset and user overrides.
        A full table has 4**n result cells.

        Either color=True or colour=True enables LaTeX colouring by result
        grade. Exact zeros always remain grey (#bbbbbb); plain-text targets
        have no colour escapes. Capture the active presentation at creation.
        """
        from ..core._metadata import dimension_metadata
        from ..display import WedgeProductTable
        from ..rendering._build import wedge_product_tree

        for name, flag in (("full", full), ("color", color), ("colour", colour)):
            if not isinstance(flag, bool):
                raise TypeError(f"{name} must be a boolean")
        selected = self.presentation
        masks = selected.display_order.masks if full else tuple(1 << index for index in range(self.n))
        # Reuse the numeric core's exact exterior coefficients. No dense
        # multivector per cell or duplicate sign algorithm is needed.
        factors = dimension_metadata(self.n).wedge_factor
        rows = tuple(tuple(int(factors[left, right]) for right in masks) for left in masks)
        tree = wedge_product_tree(masks, rows, selected, color=color or colour)
        return WedgeProductTable(tree, target=selected.display.target)

    def show_presentation(self, all: bool = False, *, basis: bool = False) -> PresentationTable:
        """Show operation notation with symbolic or basis-blade examples.

        The compact view compares the active notation with the standard
        notation. ``all=True`` includes every expression-producing operation.
        Symbolic A, B, and C are the default; ``basis=True`` uses this
        algebra's basis blades.
        """
        from ..display import _presentation_table

        if not isinstance(all, bool):
            raise TypeError("all must be a boolean")
        if not isinstance(basis, bool):
            raise TypeError("basis must be a boolean")
        return _presentation_table(
            self.presentation,
            Notation.default(),
            self.n,
            show_all=all,
            basis=basis,
        )

    @property
    def signature(self) -> tuple[int, ...]:
        """The ordered signature when the stored metric permits one."""
        return self._numeric.signature

    @property
    def id(self) -> str | None:
        return self._numeric.id

    @property
    def n(self) -> int:
        return self._numeric.n

    @property
    def dim(self) -> int:
        return self._numeric.dim

    @property
    def inertia(self) -> tuple[int, int, int]:
        return self._numeric.inertia

    @property
    def metric_rank(self) -> int:
        return self._numeric.metric_rank

    @property
    def metric_determinant(self) -> float:
        return self._numeric.metric_determinant

    @property
    def is_degenerate(self) -> bool:
        return self._numeric.is_degenerate

    @property
    def is_orthogonal_basis(self) -> bool:
        return self._numeric.is_orthogonal_basis

    @property
    def product_backend(self) -> str:
        return self._numeric.product_backend

    @property
    def packed_product_byte_estimate(self) -> int:
        return self._numeric.packed_product_byte_estimate

    @property
    def product_cache_info(self) -> tuple[int, int, int] | None:
        return self._numeric.product_cache_info

    @property
    def identity(self) -> Multivector:
        return self.scalar(1)

    @property
    def I(self) -> Multivector:  # noqa: E743 - conventional pseudoscalar name
        return self.pseudoscalar()

    def _wrap(
        self,
        value: core.Multivector,
        *,
        name: Name | None = None,
        expr: Expr | None = None,
    ) -> Multivector:
        if not isinstance(value, core.Multivector):
            raise TypeError("facade can only wrap a core.Multivector")
        if value.algebra is not self._numeric:
            raise ValueError("numeric multivector belongs to a different algebra")
        return Multivector(self, value, name=name, expr=expr)

    def multivector(
        self,
        data: Any,
        *,
        name: Name | str | None = None,
        expr: bool | Expr | None = None,
    ) -> Multivector:
        return self._factory_wrap(self._numeric.multivector(data), name=name, expr=expr)

    def scalar(
        self,
        value: Real | float,
        *,
        name: Name | str | None = None,
        expr: bool | Expr | None = None,
    ) -> Multivector:
        return self._factory_wrap(self._numeric.scalar(value), name=name, expr=expr)

    def vector(
        self,
        values: Any,
        *,
        name: Name | str | None = None,
        expr: bool | Expr | None = None,
    ) -> Multivector:
        return self._factory_wrap(self._numeric.vector(values), name=name, expr=expr)

    def blade(
        self,
        blade: int | str | BladeRef | Multivector,
        *,
        name: Name | str | None = None,
        expr: bool | Expr | None = None,
    ) -> Multivector:
        """Construct or literalize one signed unit exterior-basis blade.

        Integer masks, signed references, configured labels, aliases, and
        roles construct the selected blade. A facade multivector must belong
        to this numeric algebra and have exactly one coefficient equal to
        ``+1`` or ``-1``. Its value is preserved while its name and provenance
        are discarded; ``expr=True`` attaches a fresh literal expression.
        """
        if isinstance(blade, Multivector):
            if blade.numeric.algebra is not self._numeric:
                raise ValueError("blade multivector belongs to a different numeric algebra")
            nonzero = np.flatnonzero(blade.data)
            if len(nonzero) != 1:
                raise ValueError("blade multivector must be a signed unit basis blade")
            mask = int(nonzero[0])
            coefficient = float(blade.data[mask])
            if coefficient not in {-1.0, 1.0}:
                raise ValueError("blade multivector must be a signed unit basis blade")
            ref = BladeRef(mask, int(coefficient))
        else:
            ref = self._resolve_blade_ref(blade)
        numeric = self._numeric.blade(ref.mask)
        if ref.orientation == -1:
            numeric = self._numeric.multivector(-numeric.data)
        return self._factory_wrap(numeric, name=name, expr=expr)

    def blades(
        self,
        *blades: int | str | BladeRef | Multivector,
        expr: bool | None = None,
    ) -> tuple[Multivector, ...]:
        """Construct or literalize an ordered batch of basis blades.

        This is the plural form of :meth:`blade`: every input follows the
        singular factory's value, orientation, ownership, and provenance
        rules. The shared ``expr`` flag applies independently to every result.
        """
        expr = self._resolve_expr(expr)
        return tuple(self.blade(blade, expr=expr) for blade in blades)

    def _factory_wrap(
        self,
        value: core.Multivector,
        *,
        name: Name | str | None,
        expr: bool | Expr | None,
    ) -> Multivector:
        normalized_name = _normalize_name(name)
        result = self._wrap(value, name=normalized_name)
        if expr is None:
            expr = self._expr
        if expr is False:
            return result
        if expr is True:
            return result.with_expr()
        if isinstance(expr, Expr):
            return result.with_expr(expr)
        raise TypeError("expr must be a boolean, Expr, or None")

    def blade_label(self, bitmask: int) -> BladeLabel:
        """Return the active convention's canonical label for a native mask."""
        return self.presentation.blades.label(bitmask)

    def locals(self, *, expr: bool | None = None) -> LocalMultivectors:
        """Return read-only local values with a notebook table display."""
        expr = self._resolve_expr(expr)
        presentation = self.presentation
        values = {name: self.blade(ref, name=name, expr=expr) for name, ref in presentation.local_names.entries}
        return LocalMultivectors(
            values,
            presentation=presentation,
        )

    @property
    def display_order(self) -> tuple[int, ...]:
        """Native bitmasks in the active presentation's display order."""
        return self.presentation.display_order.masks

    def _resolve_blade_ref(self, blade: int | str | BladeRef) -> BladeRef:
        if isinstance(blade, str):
            return self.presentation.blades.resolve(blade)
        if isinstance(blade, BladeRef):
            ref = blade
        elif isinstance(blade, Integral) and not isinstance(blade, (bool, np.bool_)):
            ref = BladeRef(int(blade))
        else:
            raise TypeError("blade must be an integer bitmask, BladeRef, or configured name")
        if ref.mask >= self.dim:
            raise ValueError(f"blade mask must be in [0, {self.dim})")
        return ref

    def basis_vectors(self, *, expr: bool | None = None) -> BasisMultivectors:
        expr = self._resolve_expr(expr)
        if self._basis_vectors is None:
            self._basis_vectors = tuple(self._wrap(value) for value in self._numeric.basis_vectors())
        selected = self.presentation
        if not expr:
            cached = self._basis_vector_views.get(selected)
            if cached is None:
                cached = BasisMultivectors(
                    self._basis_vectors,
                    masks=(1 << index for index in range(self.n)),
                    presentation=selected,
                )
                self._basis_vector_views[selected] = cached
            return cached
        return BasisMultivectors(
            (value.with_expr() for value in self._basis_vectors),
            masks=(1 << index for index in range(self.n)),
            presentation=selected,
        )

    def basis_blades(self, value: int, *, expr: bool | None = None) -> BasisMultivectors:
        expr = self._resolve_expr(expr)
        result = tuple(self._wrap(blade) for blade in self._numeric.basis_blades(value))
        values = tuple(blade.with_expr() for blade in result) if expr else result
        return BasisMultivectors(
            values,
            masks=(mask for mask in range(self.dim) if mask.bit_count() == value),
            presentation=self.presentation,
        )

    def pseudoscalar(self, *, expr: bool | None = None) -> Multivector:
        expr = self._resolve_expr(expr)
        result = self._wrap(self._numeric.pseudoscalar())
        return result.with_expr() if expr else result

    def left_action(self, value: Multivector) -> np.ndarray:
        self._check_value(value)
        return cast(np.ndarray, self._numeric.left_action(value.numeric))

    def extended_metric_matrix(self) -> np.ndarray:
        return cast(np.ndarray, self._numeric.extended_metric_matrix())

    def metric_antiexomorphism_matrix(self) -> np.ndarray:
        return cast(np.ndarray, self._numeric.metric_antiexomorphism_matrix())

    def _check_value(self, value: Multivector) -> None:
        if not isinstance(value, Multivector):
            raise TypeError("expected a core facade Multivector")
        if value.numeric.algebra is not self._numeric:
            raise ValueError("multivector belongs to a different numeric algebra")

    def _metric_display(self, *, latex: bool) -> str:
        """Describe the stored metric without losing basis order or Gram entries."""
        try:
            signature = self.signature
        except ValueError:
            precision = self.presentation.display.coefficient_precision
            rows = [[_metric_number(entry, latex=latex, precision=precision) for entry in row] for row in self.gram]
            if latex:
                matrix = r" \\ ".join(" & ".join(row) for row in rows)
                return rf"\mathrm{{gram}}=\left[\begin{{smallmatrix}}{matrix}\end{{smallmatrix}}\right]"
            matrix = ", ".join("[" + ", ".join(row) + "]" for row in rows)
            return f"gram=[{matrix}]"

        p, q, r = signature.count(1), signature.count(-1), signature.count(0)
        if signature == (0,) * r + (1,) * p + (-1,) * q:
            if latex:
                return ", ".join(
                    rf"{{\color{{#bbbbbb}}{name}=0}}" if value == 0 else f"{name}={value}"
                    for name, value in (("p", p), ("q", q), ("r", r))
                )
            return f"p={p}, q={q}, r={r}"
        values = ", ".join(str(value) for value in signature)
        return rf"\mathrm{{sig}}=\left[{values}\right]" if latex else f"sig=[{values}]"

    def _metric_annotations(self) -> tuple[tuple[str, int | bool], ...]:
        annotations: list[tuple[str, int | bool]] = [("n", self.n)]
        if self.is_degenerate:
            annotations.append(("is_degenerate", True))
        if not self.is_orthogonal_basis:
            annotations.append(("non_diagonal", True))
        return tuple(annotations)

    def __repr__(self) -> str:
        annotations = ", ".join(f"{name}={value}" for name, value in self._metric_annotations())
        return f"Algebra({self._metric_display(latex=False)}) [{annotations}]"

    def _repr_latex_(self) -> str:
        metric = self._metric_display(latex=True)
        parts = []
        for name, value in self._metric_annotations():
            label = name.replace("_", r"\_")
            rendered = str(value) if isinstance(value, int) and not isinstance(value, bool) else rf"\mathrm{{{value}}}"
            parts.append(rf"\mathrm{{{label}}}={rendered}")
        annotations = r",\;".join(parts)
        return (
            rf"$\operatorname{{Algebra}}\!\left({metric}\right)"
            rf"\;\left[{annotations}\right]$"
        )


def _metric_number(value: float, *, latex: bool, precision: int) -> str:
    """Format a Gram entry with the active coefficient precision."""
    if value == 0:
        return r"{\color{#bbbbbb}0}" if latex else "0"
    return _number(float(value), "latex" if latex else "ascii", precision)


def _expand_config(value: Any) -> AlgebraConfig:
    if isinstance(value, AlgebraConfig):
        return value
    build = getattr(value, "build", None)
    if build is None or not callable(build):
        raise TypeError("config must be an AlgebraConfig or an object with build()")
    expanded = build()
    if not isinstance(expanded, AlgebraConfig):
        raise TypeError("config.build() must return an AlgebraConfig")
    return expanded


def _numeric_from_definition(definition: AlgebraDefinition) -> core.Algebra:
    keywords = {
        "id": definition.id,
        "product_backend": definition.product_backend,
    }
    if definition.dimension == 0:
        return core.Algebra(0, **keywords)
    return core.Algebra(gram=definition.gram, **keywords)


def _require_presentation(value: Any) -> PresentationConfig:
    if not isinstance(value, PresentationConfig):
        raise TypeError("presentation must be a PresentationConfig")
    return value


def _normalize_name(value: Name | str | None) -> Name | None:
    if value is None or isinstance(value, Name):
        return value
    if isinstance(value, str):
        return Name(value)
    raise TypeError("name must be a Name, string, or None")


def _require_expr_flag(value: Any) -> None:
    if not isinstance(value, bool):
        raise TypeError("expr must be a boolean")


def _override_presentation(
    base: PresentationConfig,
    *,
    blades: Any,
    notation: Any,
    local_names: Any,
    display_order: Any,
    display: Any,
) -> PresentationConfig:
    result = base
    if blades is not None:
        if not isinstance(blades, BladeConvention):
            raise TypeError("blades must be a BladeConvention")
        result = result.with_blades(blades)
    if notation is not None:
        if isinstance(notation, NotationPatch):
            notation = notation.apply(result.notation)
        if not isinstance(notation, Notation):
            raise TypeError("notation must be a Notation or NotationPatch")
        result = result.with_notation(notation)
    if local_names is not None:
        if not isinstance(local_names, LocalNamePolicy):
            raise TypeError("local_names must be a LocalNamePolicy")
        result = result.with_local_names(local_names)
    if display_order is not None:
        if not isinstance(display_order, DisplayOrder):
            raise TypeError("display_order must be a DisplayOrder")
        result = result.with_display_order(display_order)
    if display is not None:
        if not isinstance(display, DisplayPolicy):
            raise TypeError("display must be a DisplayPolicy")
        result = result.with_display(display)
    return result


class Multivector:
    """An immutable facade value containing one concrete core multivector."""

    __slots__ = ("_algebra", "_expr", "_name", "_numeric")

    def __init__(
        self,
        algebra: Algebra,
        numeric: core.Multivector,
        *,
        name: Name | None = None,
        expr: Expr | None = None,
    ) -> None:
        if not isinstance(algebra, Algebra):
            raise TypeError("algebra must be a core facade Algebra")
        if not isinstance(numeric, core.Multivector):
            raise TypeError("numeric must be a core.Multivector")
        if numeric.algebra is not algebra.numeric:
            raise ValueError("numeric multivector belongs to a different algebra")
        if name is not None and not isinstance(name, Name):
            raise TypeError("name must be a Name or None")
        if expr is not None and not isinstance(expr, Expr):
            raise TypeError("expr must be an Expr or None")
        self._algebra = algebra
        self._numeric = numeric
        self._name = name
        self._expr = expr

    @property
    def algebra(self) -> Algebra:
        return self._algebra

    @property
    def numeric(self) -> core.Multivector:
        return self._numeric

    @property
    def name(self) -> Name | None:
        """Optional semantic name, independent of expression tracking."""
        return self._name

    @property
    def expr(self) -> Expr | None:
        """Optional immutable expression provenance."""
        return self._expr

    def named(
        self,
        name: Name | str,
        *,
        unicode: str | None = None,
        latex: str | None = None,
    ) -> Multivector:
        """Return a new wrapper with a semantic name and unchanged provenance."""
        if isinstance(name, Name):
            if unicode is not None or latex is not None:
                raise TypeError("unicode= and latex= cannot override an existing Name")
            selected = name
        elif isinstance(name, str):
            selected = Name(name, unicode=unicode, latex=latex)
        else:
            raise TypeError("name must be a Name or string")
        return Multivector(self._algebra, self._numeric, name=selected, expr=self._expr)

    def unnamed(self) -> Multivector:
        """Return a new wrapper without a name and with unchanged provenance."""
        return Multivector(self._algebra, self._numeric, expr=self._expr)

    def with_expr(self, expression: Expr | None = None) -> Multivector:
        """Return a new wrapper with explicit or inferred provenance."""
        selected = _expression_operand(self) if expression is None else expression
        if not isinstance(selected, Expr):  # pragma: no cover - defensive narrowing
            raise TypeError("expression must be an Expr")
        return Multivector(self._algebra, self._numeric, name=self._name, expr=selected)

    def without_expr(self) -> Multivector:
        """Return a new wrapper without provenance and with its name unchanged."""
        return Multivector(self._algebra, self._numeric, name=self._name)

    def same_expression(self, other: object) -> bool:
        """Whether two facade values carry structurally equal provenance."""
        return isinstance(other, Multivector) and self._expr == other._expr

    @property
    def data(self) -> np.ndarray:
        return cast(np.ndarray, self._numeric.data)

    @property
    def vector_part(self) -> np.ndarray:
        return cast(np.ndarray, self._numeric.vector_part)

    def coefficient(self, bitmask: int) -> float:
        return self._numeric.coefficient(bitmask)

    def homogeneous_grade(self, *, atol: float = 1e-12) -> int | None:
        return self._numeric.homogeneous_grade(atol=atol)

    def almost_equal(self, other: Multivector, *, atol: float = 1e-12) -> bool:
        return (
            isinstance(other, Multivector)
            and self._numeric.algebra is other._numeric.algebra
            and self._numeric.almost_equal(other._numeric, atol=atol)
        )

    def grade(self, value: int) -> Multivector:
        return grade(self, value)

    @property
    def bar(self) -> Multivector:
        """Grade involution; shorthand for ``grade_involution(self)``."""
        return grade_involution(self)

    @property
    def dag(self) -> Multivector:
        """Reverse; shorthand for ``reverse(self)``, not an additional adjoint."""
        return reverse(self)

    @property
    def inv(self) -> Multivector:
        """Inverse with the canonical default tolerance; use ``inverse`` for controls."""
        return inverse(self)

    @property
    def sq(self) -> Multivector:
        """Geometric square; shorthand for ``squared(self)``."""
        return squared(self)

    def _coerce_additive(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Multivector):
            return other
        if isinstance(other, Real):
            return self._algebra.scalar(other, expr=False)
        return NotImplemented

    def __add__(self, other: object) -> Multivector | NotImplementedType:
        converted = self._coerce_additive(other)
        if converted is NotImplemented:
            return NotImplemented
        return add(self, converted)

    def __radd__(self, other: object) -> Multivector | NotImplementedType:
        converted = self._coerce_additive(other)
        if converted is NotImplemented:
            return NotImplemented
        return add(converted, self)

    def __sub__(self, other: object) -> Multivector | NotImplementedType:
        converted = self._coerce_additive(other)
        if converted is NotImplemented:
            return NotImplemented
        return subtract(self, converted)

    def __rsub__(self, other: object) -> Multivector | NotImplementedType:
        converted = self._coerce_additive(other)
        if converted is NotImplemented:
            return NotImplemented
        return subtract(converted, self)

    def __neg__(self) -> Multivector:
        return negate(self)

    def __pos__(self) -> Multivector:
        return self

    def __mul__(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Multivector):
            return geometric_product(self, other)
        if isinstance(other, Real):
            return scalar_multiply(self, other)
        return NotImplemented

    def __rmul__(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Real):
            return scalar_multiply(self, other)
        if isinstance(other, Multivector):
            return geometric_product(other, self)
        return NotImplemented

    def __truediv__(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Real):
            return scalar_divide(self, other)
        if isinstance(other, Multivector):
            return divide(self, other)
        return NotImplemented

    def __rtruediv__(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Real):
            return divide(other, self)
        return NotImplemented

    def __pow__(self, exponent: object) -> Multivector | NotImplementedType:
        if isinstance(exponent, (bool, np.bool_)):
            return NotImplemented
        if not isinstance(exponent, Integral) and (not isinstance(exponent, Real) or np.any(self._algebra.gram)):
            return NotImplemented
        return power(self, exponent)

    def __xor__(self, other: object) -> Multivector | NotImplementedType:
        converted = self._coerce_additive(other)
        if converted is NotImplemented:
            return NotImplemented
        return outer_product(self, converted)

    def __rxor__(self, other: object) -> Multivector | NotImplementedType:
        converted = self._coerce_additive(other)
        if converted is NotImplemented:
            return NotImplemented
        return outer_product(converted, self)

    def __lshift__(self, other: object) -> Multivector | NotImplementedType:
        converted = self._coerce_additive(other)
        if converted is NotImplemented:
            return NotImplemented
        return left_contraction(self, converted)

    def __rlshift__(self, other: object) -> Multivector | NotImplementedType:
        converted = self._coerce_additive(other)
        if converted is NotImplemented:
            return NotImplemented
        return left_contraction(converted, self)

    def __or__(self, other: object) -> Multivector | NotImplementedType:
        converted = self._coerce_additive(other)
        if converted is NotImplemented:
            return NotImplemented
        return doran_lasenby_inner(self, converted)

    def __ror__(self, other: object) -> Multivector | NotImplementedType:
        converted = self._coerce_additive(other)
        if converted is NotImplemented:
            return NotImplemented
        return doran_lasenby_inner(converted, self)

    def __rshift__(self, other: object) -> Multivector | NotImplementedType:
        converted = self._coerce_additive(other)
        if converted is NotImplemented:
            return NotImplemented
        return right_contraction(self, converted)

    def __rrshift__(self, other: object) -> Multivector | NotImplementedType:
        converted = self._coerce_additive(other)
        if converted is NotImplemented:
            return NotImplemented
        return right_contraction(converted, self)

    def __invert__(self) -> Multivector:
        return reverse(self)

    def __getitem__(self, value: int | str) -> Multivector:
        return grade(self, value)

    def __float__(self) -> float:
        return float(self._numeric)

    def __abs__(self) -> float:
        return abs(self._numeric)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Multivector):
            return self._numeric == other._numeric
        if isinstance(other, (Real, np.bool_)):
            return self._numeric == other
        return False

    def __hash__(self) -> int:
        return hash(self._numeric)

    def display(
        self,
        format_spec: str = "",
        *,
        content: str | None = None,
        target: str | None = None,
        presentation: PresentationConfig | None = None,
        notation: Notation | None = None,
    ) -> str:
        """Render through the Galaga 2 semantic-tree pipeline."""
        from ..display import render

        return render(
            self,
            format_spec,
            content=content,
            target=target,
            presentation=presentation,
            notation=notation,
        )

    def ascii(
        self,
        *,
        content: str | None = None,
        presentation: PresentationConfig | None = None,
        notation: Notation | None = None,
    ) -> str:
        """Render as portable plain text."""
        return self.display(content=content, target="ascii", presentation=presentation, notation=notation)

    def unicode(
        self,
        *,
        content: str | None = None,
        presentation: PresentationConfig | None = None,
        notation: Notation | None = None,
    ) -> str:
        """Render as Unicode mathematical text."""
        return self.display(content=content, target="unicode", presentation=presentation, notation=notation)

    def latex(
        self,
        wrap: str | None = None,
        *,
        content: str | None = None,
        presentation: PresentationConfig | None = None,
        notation: Notation | None = None,
    ) -> str:
        """Render as LaTeX, with optional inline or display delimiters."""
        result = self.display(content=content, target="latex", presentation=presentation, notation=notation)
        if wrap is None:
            return result
        if wrap == "$":
            return f"${result}$"
        if wrap == "$$":
            return f"$$\n{result}\n$$"
        raise ValueError("LaTeX wrap must be None, '$', or '$$'")

    def __str__(self) -> str:
        return self.display()

    def __format__(self, format_spec: str) -> str:
        return self.display(format_spec)

    def __repr__(self) -> str:
        return self.display(target="ascii")

    def _repr_pretty_(self, printer: Any, cycle: bool) -> None:
        """Use the selected plain-text target in terminal IPython."""
        printer.text("..." if cycle else self.display())

    def _repr_latex_(self) -> str:
        """Jupyter and Marimo rich-display hook."""
        return self.latex(wrap="$")


@dataclass(frozen=True, slots=True, init=False, eq=False)
class LocalMultivectors(Mapping[str, Multivector]):
    """Read-only local bindings with a presentation-aware notebook table."""

    _presentation: PresentationConfig
    _values: MappingProxyType[str, Multivector]

    def __init__(self, values: Mapping[str, Multivector], *, presentation: PresentationConfig) -> None:
        object.__setattr__(self, "_values", MappingProxyType(dict(values)))
        object.__setattr__(self, "_presentation", presentation)

    def __getitem__(self, key: str) -> Multivector:
        return self._values[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    def _ordered_items(self) -> list[tuple[str, Multivector]]:
        positions = {mask: index for index, mask in enumerate(self._presentation.display_order.masks)}
        masks = {name: ref.mask for name, ref in self._presentation.local_names.entries}

        def display_position(item: tuple[str, Multivector]) -> int:
            mask = masks.get(item[0])
            return positions.get(mask, len(positions)) if mask is not None else len(positions)

        return sorted(self._values.items(), key=display_position)

    def latex(self) -> str:
        """Render Python local names beside their captured basis-blade labels."""
        rows = [r"\text{Python name} & \text{basis blade}"]
        for name, value in self._ordered_items():
            safe_name = name.replace("_", r"\_")
            blade = value.latex(content="value", presentation=self._presentation)
            rows.append(rf"\texttt{{{safe_name}}} & {blade}")
        body = r" \\ ".join(rows)
        return rf"\begin{{array}}{{c|l}}{body}\end{{array}}"

    def _repr_latex_(self) -> str:
        return f"${self.latex()}$"

    def _repr_pretty_(self, printer: Any, cycle: bool) -> None:
        if cycle:
            printer.text("...")
            return
        entries = self._ordered_items()
        width = max((len(name) for name, _ in entries), default=0)
        width = max(width, len("Python name"))
        rows = [f"{'Python name':<{width}} | basis blade"]
        target = self._presentation.display.target
        for name, value in entries:
            blade = value.display(content="value", target=target, presentation=self._presentation)
            rows.append(f"{name:<{width}} | {blade}")
        printer.text("\n".join(rows))

    def __repr__(self) -> str:
        return f"LocalMultivectors({dict(self._values)!r})"


class BasisMultivectors(tuple[Multivector, ...]):
    """Tuple-compatible basis values with a presentation-aware notebook table."""

    _masks: tuple[int, ...]
    _presentation: PresentationConfig

    def __new__(
        cls,
        values: Iterable[Multivector],
        *,
        masks: Iterable[int],
        presentation: PresentationConfig,
    ) -> BasisMultivectors:
        result = super().__new__(cls, values)
        result._masks = tuple(masks)
        if len(result) != len(result._masks):
            raise ValueError("basis values and masks must have equal lengths")
        result._presentation = presentation
        return result

    def _ordered_indices(self) -> list[int]:
        positions = {mask: index for index, mask in enumerate(self._presentation.display_order.masks)}
        return sorted(range(len(self)), key=lambda item: positions[self._masks[item]])

    def latex(self) -> str:
        """Show native sequence indices and blades in captured display order."""
        rows = [r"\text{Index} & \text{basis blade}"]
        for index in self._ordered_indices():
            blade = self[index].latex(content="value", presentation=self._presentation)
            rows.append(rf"\texttt{{[{index}]}} & {blade}")
        body = r" \\ ".join(rows)
        return rf"\begin{{array}}{{c|l}}{body}\end{{array}}"

    def _repr_latex_(self) -> str:
        return f"${self.latex()}$"

    def _repr_pretty_(self, printer: Any, cycle: bool) -> None:
        if cycle:
            printer.text("...")
            return
        indices = self._ordered_indices()
        width = max((len(f"[{index}]") for index in indices), default=0)
        width = max(width, len("Index"))
        rows = [f"{'Index':<{width}} | basis blade"]
        target = self._presentation.display.target
        for index in indices:
            blade = self[index].display(content="value", target=target, presentation=self._presentation)
            rows.append(f"{f'[{index}]':<{width}} | {blade}")
        printer.text("\n".join(rows))


def _literal_expression(value: Multivector) -> Expr:
    data = value.data
    nonzero = np.flatnonzero(data)
    if len(nonzero) == 0:
        return ScalarLiteral(0)
    if len(nonzero) == 1:
        mask = int(nonzero[0])
        coefficient = float(data[mask])
        if mask == 0:
            return ScalarLiteral(coefficient)
        if coefficient in {-1.0, 1.0}:
            return BladeLiteral(mask, int(coefficient))
    return MultivectorLiteral(data)


def _expression_operand(value: Multivector) -> Expr:
    if value.name is not None:
        return Symbol(value.name)
    if value.expr is not None:
        return value.expr
    return _literal_expression(value)


def _invoke(operation_id: str, *args: Any, **kwargs: Any) -> Any:
    operation = get_operation(operation_id)

    owner: Algebra | None = None
    numeric_args: list[Any] = []
    tracking = False
    for argument in args:
        if isinstance(argument, Multivector):
            if owner is None:
                owner = argument.algebra
            elif argument.numeric.algebra is not owner.numeric:
                raise ValueError("cannot mix multivectors from different algebras")
            numeric_args.append(argument.numeric)
            tracking = tracking or argument.name is not None or argument.expr is not None
        else:
            numeric_args.append(argument)

    if isinstance(operation.call_policy, LeftFoldCall):
        if kwargs:
            names = ", ".join(sorted(kwargs))
            raise TypeError(f"{operation.id} does not accept fold keywords: {names}")
        if len(args) < operation.call_policy.min_args:
            raise TypeError(
                f"{operation.id} expects at least {operation.call_policy.min_args} positional argument, got {len(args)}"
            )
        if len(args) == 1 and isinstance(args[0], Multivector):
            return args[0]
        result = numeric_args[0]
        expression: Expr | None = _expression_operand(args[0]) if tracking else None
        for argument, numeric in zip(args[1:], numeric_args[1:], strict=True):
            result = operation.evaluate(result, numeric)
            if expression is not None:
                if not isinstance(argument, Multivector):
                    raise TypeError(f"{operation.id} expression operands must be multivectors")
                expression = Call(operation.id, (expression, _expression_operand(argument)))
    else:
        expression = None
        if tracking:
            expression_values, parameters = operation.bind_expression_call(tuple(args), kwargs)
            if any(not isinstance(value, Multivector) for value in expression_values):
                raise TypeError(f"{operation.id} expression operands must be multivectors")
            expression_arity = operation.expression_arity
            if expression_arity is None:  # pragma: no cover - normalized by OperationSpec
                raise RuntimeError("expression arity was not normalized")
            result = operation.invoke_expression(tuple(numeric_args[:expression_arity]), parameters)
            expression = Call(
                operation.id,
                tuple(_expression_operand(value) for value in expression_values),
                parameters,
            )
        else:
            result = operation.invoke(*numeric_args, **kwargs)
    if isinstance(result, core.Multivector):
        if owner is None:
            raise RuntimeError(f"{operation_id} produced a value without an owner")
        return owner._wrap(result, expr=expression)
    if expression is not None and operation.result_kind == "scalar":
        if owner is None:  # pragma: no cover - scalar operations have a multivector operand
            raise RuntimeError(f"{operation_id} produced a tracked scalar without an owner")
        if not isinstance(result, Real) or isinstance(result, (bool, np.bool_)):
            raise RuntimeError(f"{operation_id} declared a scalar result but produced {type(result).__name__}")
        return owner.scalar(result, expr=expression)
    return result


def _arithmetic_operands(
    operation_id: str, left: Multivector | Real, right: Multivector | Real
) -> tuple[Multivector, Multivector]:
    owner = next((value.algebra for value in (left, right) if isinstance(value, Multivector)), None)
    if owner is None:
        raise TypeError(f"{operation_id} requires at least one Multivector")

    def convert(value: Multivector | Real) -> Multivector:
        if isinstance(value, Multivector):
            return value
        if isinstance(value, Real):
            return owner.scalar(value, expr=False)
        raise TypeError(f"{operation_id} expects Multivectors or real scalars")

    return convert(left), convert(right)


def add(left: Multivector | Real, right: Multivector | Real) -> Multivector:
    """Return ``left + right``, preserving operand order and expression tracking.

    At least one operand must be a multivector. A real scalar is promoted into
    its partner's algebra; multivectors must belong to the same algebra.
    """
    return _invoke("add", *_arithmetic_operands("add", left, right))


def subtract(left: Multivector | Real, right: Multivector | Real) -> Multivector:
    """Return ``left - right``, preserving operand order and expression tracking.

    At least one operand must be a multivector. A real scalar is promoted into
    its partner's algebra; multivectors must belong to the same algebra.
    """
    return _invoke("subtract", *_arithmetic_operands("subtract", left, right))


def divide(left: Multivector | Real, right: Multivector | Real) -> Multivector:
    """Return ``left / right``, using right multiplication by the inverse.

    For a multivector denominator this is ``left * inverse(right)``; an exactly
    scalar denominator uses direct coefficient division. A real denominator
    uses ``scalar_divide``. Zero scalar denominators raise ``ZeroDivisionError``;
    noninvertible multivector denominators raise ``ValueError``.

    At least one operand must be a multivector. A real numerator is promoted
    into the denominator's algebra; multivectors must belong to the same algebra.
    """
    if isinstance(left, Multivector) and isinstance(right, Real):
        return scalar_divide(left, right)
    return _invoke("divide", *_arithmetic_operands("divide", left, right))


def negate(value: Multivector) -> Multivector:
    """Return ``-value``, negating every multivector coefficient."""
    if not isinstance(value, Multivector):
        raise TypeError("negate expects a Multivector")
    return _invoke("negate", value)


def scalar_multiply(value: Multivector, scalar: Real) -> Multivector:
    """Return ``value * scalar`` for a real scalar, preserving expression tracking."""
    if not isinstance(value, Multivector) or not isinstance(scalar, Real):
        raise TypeError("scalar_multiply expects a Multivector and a real scalar")
    return _invoke("scalar_multiply", value, scalar)


def scalar_divide(value: Multivector, scalar: Real) -> Multivector:
    """Return ``value / scalar`` by dividing every coefficient by a real scalar.

    Preserve expression tracking. A zero divisor raises ``ZeroDivisionError``.
    """
    if not isinstance(value, Multivector) or not isinstance(scalar, Real):
        raise TypeError("scalar_divide expects a Multivector and a real scalar")
    return _invoke("scalar_divide", value, scalar)


def power(value: Multivector, exponent: Real) -> Multivector:
    """Return the geometric power ``value ** exponent``.

    Integer exponents work for every metric; negative integers require an
    invertible value. Noninteger real exponents are supported only for an
    all-zero Gram matrix, on the real branches supported by the exterior
    algebra. Positive scalar part gives the principal finite binomial branch.
    Boolean exponents are rejected.
    """
    if not isinstance(value, Multivector):
        raise TypeError("power expects a Multivector")
    if isinstance(exponent, (bool, np.bool_)):
        raise TypeError("power does not accept boolean exponents")
    if not isinstance(exponent, Integral) and (not isinstance(exponent, Real) or np.any(value.algebra.gram)):
        raise TypeError("power requires an integer exponent, or a real exponent in an all-null algebra")
    return _invoke("power", value, exponent)


def geometric_product(*values: Multivector) -> Multivector:
    """Return the Clifford product computed from the native Gram matrix.

    Accept one or more multivectors from the same algebra. Multiple operands
    are combined from left to right; a single operand is returned unchanged.
    """
    return _invoke("geometric_product", *values)


def outer_product(*values: Multivector) -> Multivector:
    """Return the metric-independent exterior product.

    Accept one or more multivectors from the same algebra. Multiple operands
    are combined from left to right; a single operand is returned unchanged.
    """
    return _invoke("outer_product", *values)


def grade(value: Multivector, target: int | str) -> Multivector:
    """Project onto one grade or the combined ``"even"``/``"odd"`` grades."""
    return _invoke("grade", value, target)


def grades(value: Multivector, targets: Iterable[int]) -> Multivector:
    """Project a multivector onto several exterior grades."""
    return _invoke("grades", value, targets)


def even_grades(value: Multivector) -> Multivector:
    """Return all even-grade components."""
    return _invoke("even_grades", value)


def odd_grades(value: Multivector) -> Multivector:
    """Return all odd-grade components."""
    return _invoke("odd_grades", value)


def scalar_part(value: Multivector) -> float:
    """Optional shorthand for ``float(grade(value, 0))``."""
    return float(grade(value, 0))


def scalar_product(left: Multivector, right: Multivector) -> Multivector:
    """Return the scalar part of the geometric product as a multivector."""
    return _invoke("scalar_product", left, right)


def metric_inner_product(left: Multivector, right: Multivector) -> Multivector:
    """Return Lengyel's metric-induced pairing ``<left * ~right>_0``."""
    return _invoke("metric_inner_product", left, right)


def metric_apply(value: Multivector) -> Multivector:
    """Apply the compound-matrix exterior extension of the vector metric."""
    return _invoke("metric_apply", value)


def antimetric_apply(value: Multivector) -> Multivector:
    """Apply the complementary-compound antimetric extension."""
    return _invoke("antimetric_apply", value)


def antidot_product(left: Multivector, right: Multivector) -> Multivector:
    """Return the antimetric pairing as a pseudoscalar-valued product."""
    return _invoke("antidot_product", left, right)


def right_hodge_dual(value: Multivector) -> Multivector:
    """Return the right Hodge dual by applying the metric and right complement.

    Equivalent to ``right_complement(metric_apply(value))``.
    """
    return _invoke("right_hodge_dual", value)


def left_hodge_dual(value: Multivector) -> Multivector:
    """Return the left Hodge dual by applying the metric and left complement.

    Equivalent to ``left_complement(metric_apply(value))``.
    """
    return _invoke("left_hodge_dual", value)


def right_weight_dual(value: Multivector) -> Multivector:
    """Return ``right_complement(antimetric_apply(value))``."""
    return _invoke("right_weight_dual", value)


def left_weight_dual(value: Multivector) -> Multivector:
    """Return ``left_complement(antimetric_apply(value))``."""
    return _invoke("left_weight_dual", value)


def left_contraction(left: Multivector, right: Multivector) -> Multivector:
    """Return ``<A_r B_s>_(s-r)`` for each homogeneous pair with ``r <= s``."""
    return _invoke("left_contraction", left, right)


def right_contraction(left: Multivector, right: Multivector) -> Multivector:
    """Return ``<A_r B_s>_(r-s)`` for each homogeneous pair with ``r >= s``."""
    return _invoke("right_contraction", left, right)


def hestenes_inner(left: Multivector, right: Multivector) -> Multivector:
    """Return the Hestenes grade-difference product, discarding scalar grades."""
    return _invoke("hestenes_inner", left, right)


def doran_lasenby_inner(left: Multivector, right: Multivector) -> Multivector:
    """Return the grade-absolute-difference product, including scalars."""
    return _invoke("doran_lasenby_inner", left, right)


def commutator(left: Multivector, right: Multivector) -> Multivector:
    """Return ``left * right - right * left``."""
    return _invoke("commutator", left, right)


def anticommutator(left: Multivector, right: Multivector) -> Multivector:
    """Return ``left * right + right * left``."""
    return _invoke("anticommutator", left, right)


def half_commutator(left: Multivector, right: Multivector) -> Multivector:
    """Return ``(left * right - right * left) / 2``."""
    return _invoke("half_commutator", left, right)


def half_anticommutator(left: Multivector, right: Multivector) -> Multivector:
    """Return ``(left * right + right * left) / 2``."""
    return _invoke("half_anticommutator", left, right)


def lie_bracket(left: Multivector, right: Multivector) -> Multivector:
    """Return the unscaled Lie bracket ``left * right - right * left``."""
    return _invoke("lie_bracket", left, right)


def jordan_product(left: Multivector, right: Multivector) -> Multivector:
    """Return the unscaled symmetric product ``left * right + right * left``.

    Many Jordan-algebra texts include a factor of one half. Galaga reserves all
    such scaling for :func:`half_anticommutator`, making the function name
    reveal whether normalization occurs.
    """
    return _invoke("jordan_product", left, right)


def reverse(value: Multivector) -> Multivector:
    """Reverse every exterior blade in a multivector."""
    return _invoke("reverse", value)


def grade_involution(value: Multivector) -> Multivector:
    """Apply grade involution, negating every odd grade."""
    return _invoke("grade_involution", value)


def clifford_conjugate(value: Multivector) -> Multivector:
    """Apply Clifford conjugation, the composition of reverse and grade involution."""
    return _invoke("clifford_conjugate", value)


conjugate = clifford_conjugate


def complement(value: Multivector) -> Multivector:
    """Return the metric-independent right complement.

    Every basis blade ``A`` satisfies ``A ^ complement(A) == I``.
    """
    return _invoke("complement", value)


def uncomplement(value: Multivector) -> Multivector:
    """Return the inverse/left complement.

    Every basis blade ``A`` satisfies ``uncomplement(A) ^ A == I``.
    """
    return _invoke("uncomplement", value)


def right_complement(value: Multivector) -> Multivector:
    """Return the metric-independent right complement; equivalent to ``complement(value)``."""
    return _invoke("right_complement", value)


def left_complement(value: Multivector) -> Multivector:
    """Return the metric-independent left complement; equivalent to ``uncomplement(value)``."""
    return _invoke("left_complement", value)


def antireverse(value: Multivector) -> Multivector:
    """Apply reversion by antigrade instead of grade."""
    return _invoke("antireverse", value)


def dual(value: Multivector) -> Multivector:
    """Return the conventional metric dual using the inverse pseudoscalar."""
    return _invoke("dual", value)


def undual(value: Multivector) -> Multivector:
    """Return the inverse of :func:`dual` for a nondegenerate metric."""
    return _invoke("undual", value)


def regressive_product(left: Multivector, right: Multivector) -> Multivector:
    """Return the metric-independent complement-based regressive product."""
    return _invoke("regressive_product", left, right)


def antiwedge(left: Multivector, right: Multivector) -> Multivector:
    """RGA name for :func:`regressive_product`."""
    return _invoke("antiwedge", left, right)


def metric_regressive_product(left: Multivector, right: Multivector) -> Multivector:
    """Return the metric-dual regressive product for nondegenerate metrics."""
    return _invoke("metric_regressive_product", left, right)


def geometric_antiproduct(left: Multivector, right: Multivector) -> Multivector:
    """Return the De Morgan dual of the geometric product."""
    return _invoke("geometric_antiproduct", left, right)


def left_interior_product(left: Multivector, right: Multivector) -> Multivector:
    """Return the RGA left interior product from the left Hodge dual."""
    return _invoke("left_interior_product", left, right)


def right_interior_product(left: Multivector, right: Multivector) -> Multivector:
    """Return the RGA right interior product from the right Hodge dual."""
    return _invoke("right_interior_product", left, right)


def transwedge(left: Multivector, right: Multivector, order: int) -> Multivector:
    """Return Lengyel's order-``order`` transwedge product.

    For homogeneous grades ``r`` and ``s``, this selects grade
    ``r + s - 2*order`` from the geometric product and removes the reversion
    sign used by its geometric-product decomposition.
    """
    return _invoke("transwedge", left, right, order)


def transwedge_antiproduct(left: Multivector, right: Multivector, order: int) -> Multivector:
    """Return the De Morgan dual of the order-``order`` transwedge."""
    return _invoke("transwedge_antiproduct", left, right, order)


def inverse(
    value: Multivector,
    *,
    rtol: float = 1e-10,
    atol: float = 1e-12,
) -> Multivector:
    """Return the general inverse using the left-regular representation.

    The solve is followed by both left- and right-inverse residual checks. This
    makes the implementation basis-neutral and rejects singular or numerically
    unresolved candidates instead of returning an unchecked pseudoinverse.
    """
    parameters: dict[str, float] = {}
    if rtol != 1e-10:
        parameters["rtol"] = rtol
    if atol != 1e-12:
        parameters["atol"] = atol
    return _invoke("inverse", value, **parameters)


def squared(value: Multivector) -> Multivector:
    """Return the geometric square of a multivector."""
    return _invoke("squared", value)


def scalar_sqrt(value: Real | Multivector) -> float | Multivector:
    """Return the nonnegative real square root of a scalar value.

    Plain real numbers produce a ``float``. A scalar multivector produces a
    scalar in the same algebra. Negative values and nonscalar multivectors do
    not have a result in this real numeric API and therefore raise.
    """
    return _invoke("scalar_sqrt", value)


def sqrt(value: Real | Multivector, *, atol: float = 1e-12) -> float | Multivector:
    """Return a principal real square root on the supported algebraic domains.

    A non-scalar multivector must have the form ``a + N`` with scalar ``a``
    and scalar ``N*N``, or belong to an all-null exterior algebra with positive
    scalar part. The latter uses the finite binomial polynomial in ``N``.
    The returned value squares to ``value`` within the numeric tolerance.
    """
    return _invoke("sqrt", value, **({"atol": atol} if atol != 1e-12 else {}))


def norm2(value: Multivector) -> Multivector:
    """Return the scalar squared norm ``<value * ~value>_0``."""
    return _invoke("norm2", value)


def norm(value: Multivector) -> float | Multivector:
    """Return ``sqrt(abs(norm2(value)))`` for any real metric.

    Return a float, or a tracked scalar multivector for a semantic input.
    """
    return _invoke("norm", value)


def unit(value: Multivector, *, atol: float = 1e-15) -> Multivector:
    """Normalize a multivector by :func:`norm`."""
    return _invoke("unit", value, **({"atol": atol} if atol != 1e-15 else {}))


def is_scalar(value: Multivector, *, atol: float = 1e-12) -> bool:
    """Whether all nonscalar coefficients are numerically zero."""
    return _invoke("is_scalar", value, atol=atol)


def is_vector(value: Multivector, *, atol: float = 1e-12) -> bool:
    """Whether only grade-one coefficients are numerically nonzero."""
    return _invoke("is_vector", value, atol=atol)


def is_bivector(value: Multivector, *, atol: float = 1e-12) -> bool:
    """Whether only grade-two coefficients are numerically nonzero."""
    return _invoke("is_bivector", value, atol=atol)


def is_even(value: Multivector, *, atol: float = 1e-12) -> bool:
    """Whether every odd-grade coefficient is numerically zero."""
    return _invoke("is_even", value, atol=atol)


def is_rotor(value: Multivector, *, atol: float = 1e-12) -> bool:
    """Test evenness, full unit reverse product, and native vector preservation.

    ``atol`` is an absolute coefficient tolerance for all three checks in the
    stored basis; large boosts or poorly conditioned metrics may need a larger
    value. No normalization or inverse-sandwich substitution is performed.
    """
    return _invoke("is_rotor", value, atol=atol)


def is_rotor_generator(value: Multivector, *, atol: float = 1e-12) -> bool:
    """Test evenness, reverse skewness, and vector-valued native commutators.

    These are the infinitesimal rotor conditions, checked with absolute
    coefficient tolerance ``atol``; testing ``is_rotor(exp(value))`` alone
    would not validate the generated one-parameter action.
    """
    return _invoke("is_rotor_generator", value, atol=atol)


def is_basis_blade(value: Multivector, *, atol: float = 1e-12) -> bool:
    """Whether exactly one exterior-basis coefficient is numerically nonzero."""
    return _invoke("is_basis_blade", value, atol=atol)


def sandwich(rotor: Multivector, value: Multivector) -> Multivector:
    """Return the sandwich product ``rotor * value * ~rotor``."""
    return _invoke("sandwich", rotor, value)


def exp(value: Multivector) -> Multivector:
    """Return the geometric exponential of a multivector.

    Scalar inputs and elements with scalar square use their closed forms.
    General multivectors use a scaling-and-squaring Taylor evaluation, with
    scaling determined from the backend-neutral left-regular action.
    """
    return _invoke("exp", value)


def log(value: Multivector, *, atol: float = 1e-12) -> Multivector:
    """Return the real principal algebra logarithm; rotorhood is not required.

    Reject singular inputs, the spectral branch cut, and unresolved numerical
    cases. ``atol`` bounds coefficient convergence and the scale-aware native
    exponential residual; no alternative branch or complexification is used.
    See ``rotor_generator`` for the intentionally geometric operation.
    """
    return _invoke("log", value, **({"atol": atol} if atol != 1e-12 else {}))


def rotor_generator(value: Multivector, *, atol: float = 1e-12) -> Multivector:
    """Return a checked geometric generator from a rotor's principal logarithm.

    Raise if the input is not a rotor or this logarithm is not a generator;
    do not normalize, discard grades, or search alternative branches.
    """
    return _invoke("rotor_generator", value, **({"atol": atol} if atol != 1e-12 else {}))


def outerexp(value: Multivector) -> Multivector:
    """Return the exponential series formed with the exterior product."""
    return _invoke("outerexp", value)


def outersin(value: Multivector) -> Multivector:
    """Return the odd-power part of the outer exponential series."""
    return _invoke("outersin", value)


def outercos(value: Multivector) -> Multivector:
    """Return the even-power part of the outer exponential series."""
    return _invoke("outercos", value)


def outertan(value: Multivector) -> Multivector:
    """Return ``outersin(value) * inverse(outercos(value))``."""
    return _invoke("outertan", value)


__all__ = [
    "Algebra",
    "Multivector",
    "add",
    "anticommutator",
    "antidot_product",
    "antimetric_apply",
    "antireverse",
    "antiwedge",
    "commutator",
    "complement",
    "clifford_conjugate",
    "conjugate",
    "doran_lasenby_inner",
    "divide",
    "dual",
    "even_grades",
    "exp",
    "geometric_antiproduct",
    "geometric_product",
    "grade",
    "grade_involution",
    "grades",
    "half_anticommutator",
    "half_commutator",
    "hestenes_inner",
    "inverse",
    "is_basis_blade",
    "is_bivector",
    "is_even",
    "is_rotor",
    "is_rotor_generator",
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
    "negate",
    "norm",
    "norm2",
    "odd_grades",
    "outercos",
    "outerexp",
    "outer_product",
    "outersin",
    "outertan",
    "power",
    "regressive_product",
    "reverse",
    "right_complement",
    "right_contraction",
    "right_hodge_dual",
    "right_interior_product",
    "right_weight_dual",
    "rotor_generator",
    "sandwich",
    "scalar_part",
    "scalar_divide",
    "scalar_multiply",
    "scalar_product",
    "scalar_sqrt",
    "sqrt",
    "squared",
    "subtract",
    "transwedge",
    "transwedge_antiproduct",
    "uncomplement",
    "undual",
    "unit",
]
