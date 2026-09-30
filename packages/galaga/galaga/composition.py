"""Immutable right-biased composition of presentation components and presets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .blades import BladeConvention, DisplayOrder, LocalNamePolicy
    from .presentation import AlgebraConfig, DisplayPolicy, Notation
    from .presets import BladePreset, Preset


class PresentationComposable:
    """Provide ``|`` without coupling component modules to one another."""

    def __or__(self, other: object) -> Any:
        return compose(self, other)

    def __ror__(self, other: object) -> Any:
        return compose(other, self)


@dataclass(frozen=True, slots=True)
class PresentationRecipe(PresentationComposable):
    """Optional presentation slots resolved against a complete algebra config."""

    blades: BladeConvention | BladePreset | None = None
    notation: Notation | None = None
    local_names: LocalNamePolicy | None = None
    display_order: DisplayOrder | None = None
    display: DisplayPolicy | None = None

    def __post_init__(self) -> None:
        from .blades import BladeConvention, DisplayOrder, LocalNamePolicy
        from .presentation import DisplayPolicy, Notation
        from .presets import BladePreset

        expected = (
            ("blades", self.blades, (BladeConvention, BladePreset)),
            ("notation", self.notation, (Notation,)),
            ("local_names", self.local_names, (LocalNamePolicy,)),
            ("display_order", self.display_order, (DisplayOrder,)),
            ("display", self.display, (DisplayPolicy,)),
        )
        for name, value, types in expected:
            if value is not None and not isinstance(value, types):
                raise TypeError(f"presentation recipe {name} has an unsupported component type")

    def apply(self, config: AlgebraConfig) -> AlgebraConfig:
        """Return a config with supplied slots replaced and its metric intact."""
        from .blades import BladeConvention
        from .presentation import AlgebraConfig

        if not isinstance(config, AlgebraConfig):
            raise TypeError("presentation recipe requires an AlgebraConfig")
        presentation = config.presentation
        if self.blades is not None:
            blades = self.blades
            if not isinstance(blades, BladeConvention):
                blades = blades.resolve(config.definition.gram)
            presentation = presentation.with_blades(blades)
        if self.notation is not None:
            presentation = presentation.with_notation(self.notation)
        if self.local_names is not None:
            presentation = presentation.with_local_names(self.local_names)
        if self.display_order is not None:
            presentation = presentation.with_display_order(self.display_order)
        if self.display is not None:
            presentation = presentation.with_display(self.display)
        return config.with_presentation(presentation)


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
    from .presentation import AlgebraConfig, Notation

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

    right_recipe = _as_recipe(right)
    if right_recipe is None:
        return NotImplemented
    left_recipe = _as_recipe(left)
    if left_recipe is not None:
        return PresentationRecipe(
            blades=right_recipe.blades if right_recipe.blades is not None else left_recipe.blades,
            notation=right_recipe.notation if right_recipe.notation is not None else left_recipe.notation,
            local_names=right_recipe.local_names if right_recipe.local_names is not None else left_recipe.local_names,
            display_order=(
                right_recipe.display_order if right_recipe.display_order is not None else left_recipe.display_order
            ),
            display=right_recipe.display if right_recipe.display is not None else left_recipe.display,
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
    if isinstance(value, LocalNamePolicy):
        return PresentationRecipe(local_names=value)
    if isinstance(value, DisplayOrder):
        return PresentationRecipe(display_order=value)
    if isinstance(value, DisplayPolicy):
        return PresentationRecipe(display=value)
    return None


__all__ = ["ConfiguredPreset", "PresentationRecipe"]
