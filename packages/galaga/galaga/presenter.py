"""Reusable presentation recipes and immutable, non-arithmetic display views."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from types import NotImplementedType
from typing import TYPE_CHECKING, Literal, cast

from .blades import BladeConvention, BladePatch, DisplayOrder, LocalNamePolicy
from .composition import NotationPatch, PresentationRecipe, _as_recipe, resolve_blades
from .presentation import DisplayPolicy, Notation, PresentationConfig
from .presets._implementation import BladePreset

if TYPE_CHECKING:
    from .facade._numeric import Multivector
    from .rendering import RenderDocument


@dataclass(frozen=True, slots=True, kw_only=True)
class Presenter:
    """Override selected presentation components when applied to a value.

    Unspecified components come from the value's current presentation. Recipes
    in ``config`` are resolved against its actual algebra before explicit
    component keywords, then captured in the returned view. No setting
    propagates through arithmetic or mutates the algebra. ``content`` overrides
    the content in ``display`` when both are supplied. The ``|`` operator
    composes presenters and presentation components in left-to-right order.
    """

    presentation: PresentationConfig | None = None
    config: PresentationRecipe | None = None
    blades: BladeConvention | BladePreset | BladePatch | PresentationRecipe | None = None
    notation: Notation | NotationPatch | None = None
    local_names: LocalNamePolicy | None = None
    display_order: DisplayOrder | Literal["grade-lexicographic", "bitmap"] | None = None
    display: DisplayPolicy | None = None
    content: str | None = None
    _stages: tuple[Presenter | PresentationRecipe, ...] = field(default=(), repr=False)

    def __post_init__(self) -> None:
        for name, expected in (
            ("presentation", PresentationConfig),
            ("config", PresentationRecipe),
            ("blades", (BladeConvention, BladePreset, BladePatch, PresentationRecipe)),
            ("notation", (Notation, NotationPatch)),
            ("local_names", LocalNamePolicy),
            ("display", DisplayPolicy),
        ):
            value = getattr(self, name)
            if value is not None and not isinstance(value, expected):
                raise TypeError(f"invalid presenter {name}: {type(value).__name__}")
        order = self.display_order
        if isinstance(order, str):
            if order not in {"grade-lexicographic", "bitmap"}:
                raise ValueError("display_order must be 'grade-lexicographic', 'bitmap', or a DisplayOrder")
        elif order is not None and not isinstance(order, DisplayOrder):
            raise TypeError("display_order must be a DisplayOrder or an ordering recipe")
        if self.content is not None:
            DisplayPolicy(content=self.content)

    def __or__(self, other: object) -> Presenter | NotImplementedType:
        stage = other if isinstance(other, Presenter) else _as_recipe(other)
        if stage is None:
            return NotImplemented
        return Presenter(
            _stages=(*self._flatten(), *stage._flatten()) if isinstance(stage, Presenter) else (*self._flatten(), stage)
        )

    def __ror__(self, other: object) -> Presenter | NotImplementedType:
        stage = _as_recipe(other)
        if stage is None:
            return NotImplemented
        return Presenter(_stages=(stage, *self._flatten()))

    def _flatten(self) -> tuple[Presenter | PresentationRecipe, ...]:
        return self._stages if self._stages else (self,)

    def __call__(self, value: Multivector | PresentedMultivector) -> PresentedMultivector:
        from .facade._numeric import Multivector

        if isinstance(value, PresentedMultivector):
            base = value.presentation
            value = value.value
        elif isinstance(value, Multivector):
            base = value.algebra.presentation
        else:
            adapter = getattr(value, "__galaga_present__", None)
            if callable(adapter):
                # The adapter owns its concrete view type (for example an
                # annotation view); the presenter contract stays unchanged.
                return cast("PresentedMultivector", adapter(self))
            raise TypeError("Presenter expects a Galaga Multivector or PresentedMultivector")
        if self._stages:
            selected = base
            for stage in self._stages:
                selected = (
                    stage._apply_to(selected, value)
                    if isinstance(stage, Presenter)
                    else stage.apply_to(selected, value.algebra.gram)
                )
        else:
            selected = self._apply_to(base, value)
        return PresentedMultivector(value, selected)

    def _apply_to(self, base: PresentationConfig, value: Multivector) -> PresentationConfig:
        selected = self.presentation if self.presentation is not None else base
        if self.config is not None:
            selected = self.config.apply_to(selected, value.algebra.gram)
        # Resolve all components before validating their common dimension so a
        # complete, consistent set of overrides can replace a supplied base.
        blades = resolve_blades(self.blades, value.algebra.gram, selected.blades)
        order = self.display_order
        if isinstance(order, str):
            n = value.algebra.n
            order = DisplayOrder(n, range(1 << n)) if order == "bitmap" else DisplayOrder(n)
        display = self.display.apply_to(selected.display) if self.display is not None else selected.display
        if self.content is not None:
            display = DisplayPolicy(content=self.content).apply_to(display)
        notation = self.notation
        if isinstance(notation, NotationPatch):
            notation = notation.apply(selected.notation)
        selected = replace(
            selected,
            blades=blades,
            notation=notation if notation is not None else selected.notation,
            local_names=self.local_names if self.local_names is not None else selected.local_names,
            display_order=order if order is not None else selected.display_order,
            display=display,
        )
        return selected


@dataclass(frozen=True, slots=True, repr=False)
class PresentedMultivector:
    """A multivector and a captured presentation, with no arithmetic behavior.

    Use ``value`` for further calculations. Ordinary rendering ignores later
    algebra scopes; explicit per-render overrides remain available.
    """

    value: Multivector
    presentation: PresentationConfig

    def __post_init__(self) -> None:
        from .facade._numeric import Multivector

        if not isinstance(self.value, Multivector):
            raise TypeError("a presented value must be a Galaga Multivector")
        if not isinstance(self.presentation, PresentationConfig):
            raise TypeError("a presented value requires a PresentationConfig")
        self.value.algebra.resolve_presentation(self.presentation)

    def display(
        self,
        format_spec: str = "",
        *,
        content: str | None = None,
        target: str | None = None,
        presentation: PresentationConfig | None = None,
        notation: Notation | None = None,
    ) -> str:
        return self.value.display(
            format_spec,
            content=content,
            target=target,
            presentation=self.presentation if presentation is None else presentation,
            notation=notation,
        )

    def latex(self, *, content: str | None = None) -> str:
        """Raw LaTeX; suitable for direct galaga_marimo interpolation."""
        return self.display(content=content, target="latex")

    def render_document(
        self,
        *,
        content: str | None = None,
        target: str | None = None,
        presentation: PresentationConfig | None = None,
        notation: Notation | None = None,
    ) -> RenderDocument:
        """Build semantic anchors using this view's captured presentation."""
        from .rendering import content_document

        return content_document(self, content=content, target=target, presentation=presentation, notation=notation)

    def unicode(self, *, content: str | None = None) -> str:
        return self.display(content=content, target="unicode")

    def ascii(self, *, content: str | None = None) -> str:
        return self.display(content=content, target="ascii")

    def _repr_latex_(self) -> str:
        return f"${self.latex()}$"

    def __str__(self) -> str:
        return self.display()

    def __repr__(self) -> str:
        return self.ascii()

    def __format__(self, format_spec: str) -> str:
        return self.display(format_spec)
