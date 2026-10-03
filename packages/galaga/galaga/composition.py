"""Immutable right-biased composition of presentation components and presets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from .blades import BladeConvention, DisplayOrder, LocalNamePolicy
    from .presentation import AlgebraConfig, DisplayPolicy, Notation, PresentationConfig, RenderRule
    from .presets import BladePreset, Preset


class PresentationComposable:
    """Provide ``|`` without coupling component modules to one another."""

    def __or__(self, other: object) -> Any:
        return compose(self, other)

    def __ror__(self, other: object) -> Any:
        return compose(other, self)


@dataclass(frozen=True, slots=True)
class NotationPatch(PresentationComposable):
    """A small change to an existing notation, resolved when it is applied."""

    reverse: Literal["tilde", "dagger"] | None = None
    rules: tuple[tuple[str, str | None, RenderRule], ...] = ()

    def __post_init__(self) -> None:
        if self.reverse not in (None, "tilde", "dagger"):
            raise ValueError("reverse must be 'tilde' or 'dagger'")
        from .presentation import RenderRule

        seen: set[tuple[str, str | None]] = set()
        for operation_id, target, rule in self.rules:
            if not isinstance(operation_id, str) or not operation_id:
                raise ValueError("notation patch operation IDs must be non-empty strings")
            if target not in (None, "ascii", "unicode", "latex"):
                raise ValueError("notation patch target must be ascii, unicode, or latex")
            if not isinstance(rule, RenderRule):
                raise TypeError("notation patch rules must be RenderRule values")
            key = (operation_id, target)
            if key in seen:
                raise ValueError(f"duplicate notation patch rule for {key!r}")
            seen.add(key)

    def apply(self, notation: Notation) -> Notation:
        """Change only requested operation rules, including target overrides."""
        from .presentation import Notation

        if not isinstance(notation, Notation):
            raise TypeError("notation patch requires a Notation")
        rules = {(operation_id, target): rule for operation_id, target, rule in notation.rules}
        if self.reverse is not None:
            source = Notation.hestenes() if self.reverse == "dagger" else Notation.default()
            reverse_rules = {(operation_id, target): rule for operation_id, target, rule in source.rules}
            rules[("reverse", None)] = reverse_rules[("reverse", None)]
            if self.reverse == "dagger":
                rules.pop(("reverse", "latex"), None)
            else:
                rules[("reverse", "latex")] = reverse_rules[("reverse", "latex")]
        rules.update({(operation_id, target): rule for operation_id, target, rule in self.rules})
        encoded = {
            operation_id if target is None else (operation_id, target): rule
            for (operation_id, target), rule in rules.items()
        }
        return Notation(notation.id, notation.tokens, rules=encoded)


@dataclass(frozen=True, slots=True)
class BladeRecipe(PresentationComposable):
    """A blade preset whose dimension is inferred from the target algebra."""

    preset: str
    args: tuple[tuple[str, Any], ...] = ()

    def resolve(self, gram: Any) -> BladeConvention:
        from .presets import blades

        dimension = len(gram)
        factory = getattr(blades, self.preset)
        kwargs = dict(self.args)
        if self.preset in {"indexed", "euclidean", "exterior"}:
            value = factory(dimension, **kwargs)
        elif self.preset == "pga":
            value = factory(dimension - 1, **kwargs)
        elif self.preset == "cga":
            value = factory(dimension - 2, **kwargs)
        else:
            value = factory(**kwargs)
        return value.resolve(gram)


@dataclass(frozen=True, slots=True)
class LocalNameRecipe(PresentationComposable):
    """Dimension-independent local-name selection."""

    from_blades: bool = False
    entries: tuple[tuple[str, Any], ...] = ()

    def resolve(self, blades: BladeConvention) -> LocalNamePolicy:
        from .blades import LocalNamePolicy

        if self.from_blades:
            return LocalNamePolicy.from_convention(blades)
        return LocalNamePolicy(blades.dimension, dict(self.entries))


@dataclass(frozen=True, slots=True)
class DisplayOrderRecipe(PresentationComposable):
    """Dimension-independent ordering selection."""

    kind: str
    masks: tuple[int, ...] = ()

    def resolve(self, dimension: int) -> DisplayOrder:
        from .blades import DisplayOrder

        if self.kind == "grade-lexicographic":
            return DisplayOrder(dimension)
        if self.kind == "bitmap":
            return DisplayOrder(dimension, range(1 << dimension))
        if self.kind == "explicit":
            return DisplayOrder(dimension, self.masks)
        raise ValueError(f"unknown display order {self.kind!r}")


@dataclass(frozen=True, slots=True)
class PresentationRecipe(PresentationComposable):
    """Optional presentation slots resolved against a complete algebra config."""

    blades: BladeConvention | BladePreset | BladeRecipe | None = None
    notation: Notation | NotationPatch | None = None
    local_names: LocalNamePolicy | LocalNameRecipe | None = None
    display_order: DisplayOrder | DisplayOrderRecipe | None = None
    display: DisplayPolicy | None = None

    def __post_init__(self) -> None:
        from .blades import BladeConvention, DisplayOrder, LocalNamePolicy
        from .presentation import DisplayPolicy, Notation
        from .presets import BladePreset

        expected = (
            ("blades", self.blades, (BladeConvention, BladePreset, BladeRecipe)),
            ("notation", self.notation, (Notation, NotationPatch)),
            ("local_names", self.local_names, (LocalNamePolicy, LocalNameRecipe)),
            ("display_order", self.display_order, (DisplayOrder, DisplayOrderRecipe)),
            ("display", self.display, (DisplayPolicy,)),
        )
        for name, value, types in expected:
            if value is not None and not isinstance(value, types):
                raise TypeError(f"presentation recipe {name} has an unsupported component type")

    def apply(self, config: AlgebraConfig) -> AlgebraConfig:
        """Return a config with supplied slots replaced and its metric intact."""
        from .presentation import AlgebraConfig

        if not isinstance(config, AlgebraConfig):
            raise TypeError("presentation recipe requires an AlgebraConfig")
        return config.with_presentation(self.apply_to(config.presentation, config.definition.gram))

    def apply_to(self, presentation: PresentationConfig, gram: Any) -> PresentationConfig:
        """Resolve optional slots against an existing presentation and Gram matrix."""
        from .blades import BladeConvention
        from .presentation import PresentationConfig

        if not isinstance(presentation, PresentationConfig):
            raise TypeError("presentation recipe requires a PresentationConfig")
        if self.blades is not None:
            blades = self.blades
            if not isinstance(blades, BladeConvention):
                blades = blades.resolve(gram)
            presentation = presentation.with_blades(blades)
        if self.notation is not None:
            notation = (
                self.notation.apply(presentation.notation)
                if isinstance(self.notation, NotationPatch)
                else self.notation
            )
            presentation = presentation.with_notation(notation)
        if self.local_names is not None:
            local_names = self.local_names
            if isinstance(local_names, LocalNameRecipe):
                local_names = local_names.resolve(presentation.blades)
            presentation = presentation.with_local_names(local_names)
        if self.display_order is not None:
            order = self.display_order
            if isinstance(order, DisplayOrderRecipe):
                order = order.resolve(presentation.dimension)
            presentation = presentation.with_display_order(order)
        if self.display is not None:
            presentation = presentation.with_display(self.display)
        return presentation


@dataclass(frozen=True, slots=True)
class ConfiguredPreset(PresentationComposable):
    """A complete preset plus presentation overrides, expanded on ``build``."""

    base: Preset | AlgebraConfig
    presentation: PresentationRecipe

    def __post_init__(self) -> None:
        from .presentation import AlgebraConfig

        if not isinstance(self.base, AlgebraConfig) and not callable(getattr(self.base, "build", None)):
            raise TypeError("configured preset base must be a complete algebra preset or config")
        if not isinstance(self.presentation, PresentationRecipe):
            raise TypeError("configured preset presentation must be a PresentationRecipe")

    def build(self) -> AlgebraConfig:
        from .presentation import AlgebraConfig

        config = self.base if isinstance(self.base, AlgebraConfig) else self.base.build()
        if not isinstance(config, AlgebraConfig):
            raise TypeError("complete preset build() must return an AlgebraConfig")
        return self.presentation.apply(config)


def compose(left: object, right: object) -> Any:
    """Merge rule maps or presentation slots with right-hand precedence."""
    from .presentation import AlgebraConfig, DisplayPolicy, Notation

    if isinstance(left, NotationPatch) and isinstance(right, NotationPatch):
        reverse = right.reverse if right.reverse is not None else left.reverse
        rules = {(operation_id, target): rule for operation_id, target, rule in left.rules}
        if right.reverse is not None:
            rules.pop(("reverse", None), None)
            rules.pop(("reverse", "latex"), None)
        rules.update({(operation_id, target): rule for operation_id, target, rule in right.rules})
        return NotationPatch(reverse=reverse, rules=tuple((op, target, rule) for (op, target), rule in rules.items()))
    if isinstance(left, Notation) and isinstance(right, NotationPatch):
        return right.apply(left)
    if isinstance(left, NotationPatch) and isinstance(right, Notation):
        return right
    if isinstance(left, Notation) and isinstance(right, Notation):
        tokens = dict(left.tokens) | dict(right.tokens)
        rules = {
            (operation_id if target is None else (operation_id, target)): rule
            for operation_id, target, rule in left.rules
        }
        rules.update(
            {
                (operation_id if target is None else (operation_id, target)): rule
                for operation_id, target, rule in right.rules
            }
        )
        return Notation(right.id, tokens, rules=rules)
    if isinstance(left, DisplayPolicy) and isinstance(right, DisplayPolicy):
        return left.merge(right)

    right_recipe = _as_recipe(right)
    if right_recipe is None:
        return NotImplemented
    left_recipe = _as_recipe(left)
    if left_recipe is not None:
        notation = right_recipe.notation if right_recipe.notation is not None else left_recipe.notation
        if isinstance(notation, NotationPatch) and left_recipe.notation is not None:
            notation = compose(left_recipe.notation, notation)
        return PresentationRecipe(
            blades=right_recipe.blades if right_recipe.blades is not None else left_recipe.blades,
            notation=notation,
            local_names=right_recipe.local_names if right_recipe.local_names is not None else left_recipe.local_names,
            display_order=(
                right_recipe.display_order if right_recipe.display_order is not None else left_recipe.display_order
            ),
            display=(
                left_recipe.display.merge(right_recipe.display)
                if left_recipe.display is not None and right_recipe.display is not None
                else right_recipe.display
                if right_recipe.display is not None
                else left_recipe.display
            ),
        )
    if isinstance(left, ConfiguredPreset):
        return ConfiguredPreset(left.base, compose(left.presentation, right_recipe))
    if isinstance(left, AlgebraConfig) or callable(getattr(left, "build", None)):
        return ConfiguredPreset(left, right_recipe)
    return NotImplemented


def _as_recipe(value: object) -> PresentationRecipe | None:
    from .blades import BladeConvention, DisplayOrder, LocalNamePolicy
    from .presentation import DisplayPolicy, Notation
    from .presets import BladePreset

    if isinstance(value, PresentationRecipe):
        return value
    if isinstance(value, (BladeConvention, BladePreset)):
        return PresentationRecipe(blades=value)
    if isinstance(value, Notation):
        return PresentationRecipe(notation=value)
    if isinstance(value, NotationPatch):
        return PresentationRecipe(notation=value)
    if isinstance(value, LocalNamePolicy):
        return PresentationRecipe(local_names=value)
    if isinstance(value, DisplayOrder):
        return PresentationRecipe(display_order=value)
    if isinstance(value, DisplayPolicy):
        return PresentationRecipe(display=value)
    return None


__all__ = ["ConfiguredPreset", "NotationPatch", "PresentationRecipe"]
