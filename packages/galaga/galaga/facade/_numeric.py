"""Composition facade over :mod:`galaga.core`.

Facade values remain eager numeric wrappers. Facade algebras additionally own
immutable presentation configuration and context-local selection. Optional
expression provenance records how an eager value was obtained without changing
numeric evaluation.
"""

from __future__ import annotations

from collections.abc import Generator, Iterable
from contextlib import contextmanager
from contextvars import ContextVar
from numbers import Integral, Real
from types import MappingProxyType, NotImplementedType
from typing import TYPE_CHECKING, Any, cast

import numpy as np

from .. import core
from ..blades import BladeConvention, BladeLabel, BladeRef, DisplayOrder, LocalNamePolicy
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
from .catalog import LeftFoldCall, get_operation

if TYPE_CHECKING:
    from ..presets import Preset


class Algebra:
    """An immutable numeric algebra with a cheap configurable presentation."""

    __slots__ = (
        "_basis_vectors",
        "_default_presentation",
        "_model",
        "_numeric",
        "_presentation_override",
    )

    def __init__(
        self,
        *args: Any,
        config: AlgebraConfig | Preset | None = None,
        presentation: PresentationConfig | None = None,
        blades: BladeConvention | None = None,
        notation: Notation | None = None,
        local_names: LocalNamePolicy | None = None,
        display_order: DisplayOrder | None = None,
        display: DisplayPolicy | None = None,
        **kwargs: Any,
    ) -> None:
        if config is not None:
            if args or kwargs:
                conflicting = [repr(value) for value in args]
                conflicting.extend(f"{name}=" for name in sorted(kwargs))
                details = ", ".join(conflicting)
                raise TypeError(f"config= defines the numeric algebra and cannot be combined with {details}")
            expanded = _expand_config(config)
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
            self._model = None

        if presentation is not None:
            base_presentation = _require_presentation(presentation)
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
    ) -> Algebra:
        """Create a facade over an existing numeric algebra."""
        if not isinstance(numeric, core.Algebra):
            raise TypeError("numeric must be a core.Algebra")
        selected = default_presentation(numeric.n) if presentation is None else _require_presentation(presentation)
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
        instance._basis_vectors = None
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

    def with_presentation(self, presentation: PresentationConfig) -> Algebra:
        """Return a cheap view sharing numeric identity with a new presentation."""
        return Algebra.from_numeric(
            self._numeric,
            presentation=self.resolve_presentation(presentation),
            model=self._model,
        )

    def with_blades(self, blades: BladeConvention) -> Algebra:
        return self.with_presentation(self.presentation.with_blades(blades))

    def with_notation(self, notation: Notation) -> Algebra:
        return self.with_presentation(self.presentation.with_notation(notation))

    def with_local_names(self, local_names: LocalNamePolicy) -> Algebra:
        return self.with_presentation(self.presentation.with_local_names(local_names))

    def with_display_order(self, display_order: DisplayOrder) -> Algebra:
        return self.with_presentation(self.presentation.with_display_order(display_order))

    def with_display(self, display: DisplayPolicy) -> Algebra:
        return self.with_presentation(self.presentation.with_display(display))

    @contextmanager
    def use_presentation(self, presentation: PresentationConfig) -> Generator[Algebra, None, None]:
        """Temporarily override presentation in the current thread or async task."""
        selected = self.resolve_presentation(presentation)
        token = self._presentation_override.set(selected)
        try:
            yield self
        finally:
            self._presentation_override.reset(token)

    @property
    def gram(self) -> np.ndarray:
        return cast(np.ndarray, self._numeric.gram)

    @property
    def basis_squares(self) -> np.ndarray:
        return cast(np.ndarray, self._numeric.basis_squares)

    @property
    def signature(self) -> tuple[int, ...]:
        """The legacy ordered signature when the stored metric permits one."""
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
        return self._wrap(self._numeric.identity)

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
        expr: bool | Expr = False,
    ) -> Multivector:
        return self._factory_wrap(self._numeric.multivector(data), name=name, expr=expr)

    def scalar(
        self,
        value: Real,
        *,
        name: Name | str | None = None,
        expr: bool | Expr = False,
    ) -> Multivector:
        return self._factory_wrap(self._numeric.scalar(value), name=name, expr=expr)

    def vector(
        self,
        values: Any,
        *,
        name: Name | str | None = None,
        expr: bool | Expr = False,
    ) -> Multivector:
        return self._factory_wrap(self._numeric.vector(values), name=name, expr=expr)

    def blade(
        self,
        blade: int | str | BladeRef,
        *,
        name: Name | str | None = None,
        expr: bool | Expr = False,
    ) -> Multivector:
        """Construct a blade by native mask, signed reference, label, alias, or role."""
        ref = self._resolve_blade_ref(blade)
        numeric = self._numeric.blade(ref.mask)
        if ref.orientation == -1:
            numeric = self._numeric.multivector(-numeric.data)
        return self._factory_wrap(numeric, name=name, expr=expr)

    def _factory_wrap(
        self,
        value: core.Multivector,
        *,
        name: Name | str | None,
        expr: bool | Expr,
    ) -> Multivector:
        normalized_name = _normalize_name(name)
        result = self._wrap(value, name=normalized_name)
        if expr is False:
            return result
        if expr is True:
            return result.with_expr()
        if isinstance(expr, Expr):
            return result.with_expr(expr)
        raise TypeError("expr must be a boolean or Expr")

    def blade_label(self, bitmask: int) -> BladeLabel:
        """Return the active convention's canonical label for a native mask."""
        return self.presentation.blades.label(bitmask)

    def locals(self, *, expr: bool = False) -> MappingProxyType[str, Multivector]:
        """Return a read-only mapping of configured Python names to values."""
        _require_expr_flag(expr)
        return MappingProxyType(
            {name: self.blade(ref, name=name, expr=expr) for name, ref in self.presentation.local_names.entries}
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

    def basis_vectors(self, *, expr: bool = False) -> tuple[Multivector, ...]:
        _require_expr_flag(expr)
        if self._basis_vectors is None:
            self._basis_vectors = tuple(self._wrap(value) for value in self._numeric.basis_vectors())
        if not expr:
            return self._basis_vectors
        return tuple(value.with_expr() for value in self._basis_vectors)

    def basis_blades(self, value: int, *, expr: bool = False) -> tuple[Multivector, ...]:
        _require_expr_flag(expr)
        result = tuple(self._wrap(blade) for blade in self._numeric.basis_blades(value))
        if not expr:
            return result
        return tuple(blade.with_expr() for blade in result)

    def pseudoscalar(self, *, expr: bool = False) -> Multivector:
        _require_expr_flag(expr)
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

    def __repr__(self) -> str:
        return f"Algebra(numeric={self._numeric!r})"


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
        if not isinstance(notation, Notation):
            raise TypeError("notation must be a Notation")
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

    def _coerce_additive(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Multivector):
            return other
        if isinstance(other, Real):
            return self._algebra.scalar(other)
        return NotImplemented

    def __add__(self, other: object) -> Multivector | NotImplementedType:
        converted = self._coerce_additive(other)
        if converted is NotImplemented:
            return NotImplemented
        return _invoke("add", self, converted)

    def __radd__(self, other: object) -> Multivector | NotImplementedType:
        return self.__add__(other)

    def __sub__(self, other: object) -> Multivector | NotImplementedType:
        converted = self._coerce_additive(other)
        if converted is NotImplemented:
            return NotImplemented
        return _invoke("subtract", self, converted)

    def __rsub__(self, other: object) -> Multivector | NotImplementedType:
        converted = self._coerce_additive(other)
        if converted is NotImplemented:
            return NotImplemented
        return _invoke("subtract", converted, self)

    def __neg__(self) -> Multivector:
        return _invoke("negate", self)

    def __pos__(self) -> Multivector:
        return self

    def __mul__(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Multivector):
            return geometric_product(self, other)
        if isinstance(other, Real):
            return _invoke("scalar_multiply", self, other)
        return NotImplemented

    def __rmul__(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Real):
            return _invoke("scalar_multiply", self, other)
        if isinstance(other, Multivector):
            return geometric_product(other, self)
        return NotImplemented

    def __truediv__(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Real):
            return _invoke("scalar_divide", self, other)
        if isinstance(other, Multivector):
            if other.numeric.algebra is not self._numeric.algebra:
                raise ValueError("cannot mix multivectors from different algebras")
            if is_scalar(other):
                divisor = other.coefficient(0)
                if divisor == 0:
                    raise ZeroDivisionError("cannot divide by a zero scalar multivector")
                return _invoke("scalar_divide", self, divisor)
            return geometric_product(self, inverse(other))
        return NotImplemented

    def __rtruediv__(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Real):
            return geometric_product(self._algebra.scalar(other), inverse(self))
        return NotImplemented

    def __pow__(self, exponent: object) -> Multivector | NotImplementedType:
        if not isinstance(exponent, Integral) or isinstance(exponent, (bool, np.bool_)):
            return NotImplemented
        return _invoke("power", self, exponent)

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
        if isinstance(other, Real):
            return self._numeric == other
        return False

    def __hash__(self) -> int:
        return hash(self._numeric)

    def __repr__(self) -> str:
        metadata = ""
        if self._name is not None:
            metadata += f", name={self._name!r}"
        if self._expr is not None:
            metadata += f", expr={self._expr!r}"
        return f"Multivector(numeric={self._numeric!r}{metadata})"


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
            tracking = tracking or argument.expr is not None
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
    return result


def geometric_product(*values: Multivector) -> Multivector:
    return _invoke("geometric_product", *values)


def outer_product(*values: Multivector) -> Multivector:
    return _invoke("outer_product", *values)


def grade(value: Multivector, target: int | str) -> Multivector:
    return _invoke("grade", value, target)


def grades(value: Multivector, targets: Iterable[int]) -> Multivector:
    return _invoke("grades", value, targets)


def even_grades(value: Multivector) -> Multivector:
    return _invoke("even_grades", value)


def odd_grades(value: Multivector) -> Multivector:
    return _invoke("odd_grades", value)


def scalar_part(value: Multivector) -> float:
    """Optional shorthand for ``float(grade(value, 0))``."""
    return float(grade(value, 0))


def scalar_product(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("scalar_product", left, right)


def metric_inner_product(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("metric_inner_product", left, right)


def metric_apply(value: Multivector) -> Multivector:
    return _invoke("metric_apply", value)


def antimetric_apply(value: Multivector) -> Multivector:
    return _invoke("antimetric_apply", value)


def antidot_product(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("antidot_product", left, right)


def bulk_part(value: Multivector) -> Multivector:
    return _invoke("bulk_part", value)


def weight_part(value: Multivector) -> Multivector:
    return _invoke("weight_part", value)


def right_hodge_dual(value: Multivector) -> Multivector:
    return _invoke("right_hodge_dual", value)


def left_hodge_dual(value: Multivector) -> Multivector:
    return _invoke("left_hodge_dual", value)


def right_weight_dual(value: Multivector) -> Multivector:
    return _invoke("right_weight_dual", value)


def left_weight_dual(value: Multivector) -> Multivector:
    return _invoke("left_weight_dual", value)


def left_contraction(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("left_contraction", left, right)


def right_contraction(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("right_contraction", left, right)


def hestenes_inner(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("hestenes_inner", left, right)


def doran_lasenby_inner(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("doran_lasenby_inner", left, right)


def commutator(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("commutator", left, right)


def anticommutator(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("anticommutator", left, right)


def half_commutator(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("half_commutator", left, right)


def half_anticommutator(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("half_anticommutator", left, right)


def lie_bracket(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("lie_bracket", left, right)


def jordan_product(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("jordan_product", left, right)


def reverse(value: Multivector) -> Multivector:
    return _invoke("reverse", value)


def grade_involution(value: Multivector) -> Multivector:
    return _invoke("grade_involution", value)


involute = grade_involution


def conjugate(value: Multivector) -> Multivector:
    return _invoke("conjugate", value)


def complement(value: Multivector) -> Multivector:
    return _invoke("complement", value)


def uncomplement(value: Multivector) -> Multivector:
    return _invoke("uncomplement", value)


def right_complement(value: Multivector) -> Multivector:
    return _invoke("right_complement", value)


def left_complement(value: Multivector) -> Multivector:
    return _invoke("left_complement", value)


def antireverse(value: Multivector) -> Multivector:
    return _invoke("antireverse", value)


def dual(value: Multivector) -> Multivector:
    return _invoke("dual", value)


def undual(value: Multivector) -> Multivector:
    return _invoke("undual", value)


def regressive_product(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("regressive_product", left, right)


def antiwedge(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("antiwedge", left, right)


def metric_regressive_product(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("metric_regressive_product", left, right)


def geometric_antiproduct(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("geometric_antiproduct", left, right)


def left_interior_product(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("left_interior_product", left, right)


def right_interior_product(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("right_interior_product", left, right)


def transwedge(left: Multivector, right: Multivector, order: int) -> Multivector:
    return _invoke("transwedge", left, right, order)


def transwedge_antiproduct(left: Multivector, right: Multivector, order: int) -> Multivector:
    return _invoke("transwedge_antiproduct", left, right, order)


def inverse(
    value: Multivector,
    *,
    rtol: float = 1e-10,
    atol: float = 1e-12,
) -> Multivector:
    return _invoke("inverse", value, rtol=rtol, atol=atol)


def squared(value: Multivector) -> Multivector:
    return _invoke("squared", value)


def scalar_sqrt(value: Real | Multivector) -> float | Multivector:
    return _invoke("scalar_sqrt", value)


def sqrt(value: Real | Multivector, *, atol: float = 1e-12) -> float | Multivector:
    return _invoke("sqrt", value, atol=atol)


def norm2(value: Multivector) -> Multivector:
    return _invoke("norm2", value)


def norm(value: Multivector) -> float:
    return _invoke("norm", value)


def unit(value: Multivector, *, atol: float = 1e-15) -> Multivector:
    return _invoke("unit", value, atol=atol)


def is_scalar(value: Multivector, *, atol: float = 1e-12) -> bool:
    return _invoke("is_scalar", value, atol=atol)


def is_vector(value: Multivector, *, atol: float = 1e-12) -> bool:
    return _invoke("is_vector", value, atol=atol)


def is_bivector(value: Multivector, *, atol: float = 1e-12) -> bool:
    return _invoke("is_bivector", value, atol=atol)


def is_even(value: Multivector, *, atol: float = 1e-12) -> bool:
    return _invoke("is_even", value, atol=atol)


def is_rotor(value: Multivector, *, atol: float = 1e-12) -> bool:
    return _invoke("is_rotor", value, atol=atol)


def is_basis_blade(value: Multivector, *, atol: float = 1e-12) -> bool:
    return _invoke("is_basis_blade", value, atol=atol)


def sandwich(rotor: Multivector, value: Multivector) -> Multivector:
    return _invoke("sandwich", rotor, value)


def exp(value: Multivector) -> Multivector:
    return _invoke("exp", value)


def log(value: Multivector, *, atol: float = 1e-12) -> Multivector:
    return _invoke("log", value, atol=atol)


def outerexp(value: Multivector) -> Multivector:
    return _invoke("outerexp", value)


def outersin(value: Multivector) -> Multivector:
    return _invoke("outersin", value)


def outercos(value: Multivector) -> Multivector:
    return _invoke("outercos", value)


def outertan(value: Multivector) -> Multivector:
    return _invoke("outertan", value)


__all__ = [
    "Algebra",
    "Multivector",
    "anticommutator",
    "antidot_product",
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
    "half_anticommutator",
    "half_commutator",
    "hestenes_inner",
    "inverse",
    "involute",
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
    "outercos",
    "outerexp",
    "outer_product",
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
    "scalar_part",
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
]
