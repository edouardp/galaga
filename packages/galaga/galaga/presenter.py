"""Reusable presentation recipes and immutable, non-arithmetic display views."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Literal, cast

from .blades import BladeConvention, DisplayOrder, LocalNamePolicy
from .presentation import DisplayPolicy, Notation, PresentationConfig
from .presets._implementation import BladePreset

if TYPE_CHECKING:
    from .facade._numeric import Multivector
    from .rendering import RenderDocument


@dataclass(frozen=True, slots=True, kw_only=True)
class Presenter:
    """Override selected presentation components when applied to a value.

    Unspecified components come from the value's current presentation. Recipes
    are resolved against its actual algebra, then captured in the returned
    view. No setting propagates through arithmetic or mutates the algebra.
    ``content`` overrides the content in ``display`` when both are supplied.
    """

    presentation: PresentationConfig | None = None
    blades: BladeConvention | BladePreset | None = None
    notation: Notation | None = None
    local_names: LocalNamePolicy | None = None
    display_order: DisplayOrder | Literal["grade-lexicographic", "bitmap"] | None = None
    display: DisplayPolicy | None = None
    content: str | None = None

    def __post_init__(self) -> None:
        for field, expected in (
            ("presentation", PresentationConfig),
            ("blades", (BladeConvention, BladePreset)),
            ("notation", Notation),
            ("local_names", LocalNamePolicy),
            ("display", DisplayPolicy),
        ):
            value = getattr(self, field)
            if value is not None and not isinstance(value, expected):
                raise TypeError(f"invalid presenter {field}: {type(value).__name__}")
        order = self.display_order
        if isinstance(order, str):
            if order not in {"grade-lexicographic", "bitmap"}:
                raise ValueError("display_order must be 'grade-lexicographic', 'bitmap', or a DisplayOrder")
        elif order is not None and not isinstance(order, DisplayOrder):
            raise TypeError("display_order must be a DisplayOrder or an ordering recipe")
        if self.content is not None:
            DisplayPolicy(content=self.content)

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
        selected = self.presentation if self.presentation is not None else base
        # Resolve all components before validating their common dimension so a
        # complete, consistent set of overrides can replace a supplied base.
        blades = self.blades
        if isinstance(blades, BladePreset):
            blades = blades.resolve(value.algebra.gram.tolist())
        order = self.display_order
        if isinstance(order, str):
            n = value.algebra.n
            order = DisplayOrder(n, range(1 << n)) if order == "bitmap" else DisplayOrder(n)
        display = self.display if self.display is not None else selected.display
        if self.content is not None:
            display = replace(display, content=self.content)
        selected = replace(
            selected,
            blades=blades if blades is not None else selected.blades,
            notation=self.notation if self.notation is not None else selected.notation,
            local_names=self.local_names if self.local_names is not None else selected.local_names,
            display_order=order if order is not None else selected.display_order,
            display=display,
        )
        return PresentedMultivector(value, selected)


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
