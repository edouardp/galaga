"""Layered TOML preferences for facade presentation and named recipes."""

from __future__ import annotations

import inspect
import os
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .blades import BladeRef
from .composition import (
    BladeRecipe,
    DisplayOrderRecipe,
    LocalNameRecipe,
    NotationPatch,
    PresentationRecipe,
    compose,
)
from .names import Name
from .presentation import (
    AlgebraConfig,
    AlgebraDefinition,
    DisplayPolicy,
    Notation,
    RenderRule,
    default_presentation,
)
from .presenter import Presenter

_SECTIONS = ("notations", "presentations", "presenters", "algebras")
_PRESETS = frozenset(
    {"euclidean", "oblique_plane", "sta", "pga", "cga", "rga", "lengyel_cga", "complex", "quaternion", "exterior"}
)
_BLADE_PRESETS = frozenset({"indexed", "euclidean", "sta", "pga", "cga", "rga", "complex", "quaternion", "exterior"})
_NOTATION_PRESETS = frozenset(
    {"default", "functional", "functional_short", "doran_lasenby", "hestenes", "lengyel", "lengyel_rga"}
)
_PRESENTATION_FIELDS = frozenset({"blades", "notation", "local_names", "display_order", "display"})
_MAX_BYTES = 1_048_576


class ConfigError(ValueError):
    """A configuration source or reference is invalid."""


def _error(source: Path, where: str, message: str) -> ConfigError:
    return ConfigError(f"{source}: {where}: {message}")


def _mapping(value: Any, source: Path, where: str, allowed: frozenset[str] | None = None) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise _error(source, where, "expected a mapping")
    if any(not isinstance(key, str) for key in value):
        raise _error(source, where, "mapping keys must be strings")
    if allowed is not None:
        unknown = set(value) - allowed
        if unknown:
            raise _error(source, where, f"unknown field(s): {', '.join(sorted(unknown))}")
    return value


def _name(value: Any, source: Path, where: str) -> str:
    if not isinstance(value, str) or not value:
        raise _error(source, where, "expected a non-empty string")
    if value.startswith("@"):
        raise _error(source, where, "names starting with '@' are reserved for references")
    return value


def _reference(value: Any, source: Path, where: str) -> str:
    if not isinstance(value, str) or not value.startswith("@"):
        raise _error(source, where, "expected a reference string such as '@name'")
    return _name(value[1:], source, where)


def _parse(path: Path) -> Mapping[str, Any]:
    try:
        size = path.stat().st_size
    except OSError as error:
        raise ConfigError(f"{path}: {error}") from error
    if size > _MAX_BYTES:
        raise _error(path, "root", "configuration file exceeds 1 MiB")
    try:
        value = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as error:
        raise ConfigError(f"{path}: {error}") from error
    mapping = _mapping(value, path, "root", frozenset({"version", "defaults", *_SECTIONS}))
    if type(mapping.get("version")) is not int or mapping["version"] != 1:
        raise _error(path, "version", "expected version = 1")
    return mapping


def _discover(start: Path | None, files: Sequence[Path] | None) -> tuple[Path, ...]:
    if files is not None:
        selected = tuple(Path(path).expanduser() for path in files)
        for path in selected:
            if not path.is_file():
                raise ConfigError(f"{path}: configuration source must be an existing file")
        return tuple(path.resolve() for path in selected)
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg is not None and not Path(xdg).is_absolute():
        raise ConfigError("XDG_CONFIG_HOME must be an absolute path")
    global_file = (Path(xdg) if xdg else Path.home() / ".config") / "galaga_python" / "config.toml"
    current = (Path.cwd() if start is None else Path(start)).resolve()
    if not current.is_dir():
        raise ConfigError(f"{current}: configuration start must be a directory")
    local = tuple(parent / ".galaga_python.toml" for parent in reversed((current, *current.parents)))
    for path in (global_file, *local):
        if path.exists() and not path.is_file():
            raise ConfigError(f"{path}: configuration source must be a file")
    return tuple(path for path in (global_file, *local) if path.is_file())


@dataclass(frozen=True, slots=True)
class _Entry:
    value: Mapping[str, Any]
    source: Path


@dataclass(frozen=True, slots=True)
class Settings:
    """An immutable set of parsed sources and resolved named recipes."""

    sources: tuple[Path, ...]
    _defaults: tuple[_Entry, ...]
    _names: Mapping[str, Mapping[str, _Entry]]

    def __post_init__(self) -> None:
        # Resolve every name now so invalid references fail at load time.
        for section in _SECTIONS:
            for name in self._names[section]:
                getattr(self, section[:-1] if section != "algebras" else "algebra")(name)
        self.default_recipe()

    def _entry(self, section: str, name: str) -> _Entry:
        try:
            return self._names[section][name]
        except KeyError as error:
            sources = ", ".join(str(path) for path in self.sources) or "no configuration files"
            raise ConfigError(f"unknown {section} name {name!r}; searched {sources}") from error

    def _notation(self, name: str, stack: tuple[str, ...]) -> Notation | NotationPatch:
        if name in stack:
            raise ConfigError(f"notation reference cycle: {' -> '.join((*stack, name))}")
        entry = self._entry("notations", name)
        data = _mapping(entry.value, entry.source, f"notations.{name}", frozenset({"base", "reverse", "rules"}))
        base: Notation | NotationPatch = NotationPatch()
        if "base" in data:
            selection = data["base"]
            if isinstance(selection, str):
                base = self._notation(_reference(selection, entry.source, f"notations.{name}.base"), (*stack, name))
            else:
                source = _mapping(selection, entry.source, f"notations.{name}.base", frozenset({"preset"}))
                if set(source) != {"preset"}:
                    raise _error(entry.source, f"notations.{name}.base", "expected '@name' or {preset = 'name'}")
                preset_name = _name(source["preset"], entry.source, f"notations.{name}.base.preset")
                if preset_name not in _NOTATION_PRESETS:
                    raise _error(entry.source, f"notations.{name}.base", f"unknown notation preset {preset_name!r}")
                from . import presets

                base = getattr(presets.notation, preset_name)()
        reverse = data.get("reverse")
        rules = self._rules(data.get("rules", {}), entry.source, f"notations.{name}.rules")
        try:
            patch = NotationPatch(reverse=reverse, rules=rules)
        except (TypeError, ValueError) as error:
            raise _error(entry.source, f"notations.{name}", str(error)) from error
        return compose(base, patch)

    @staticmethod
    def _rules(value: Any, source: Path, where: str) -> tuple[tuple[str, str | None, RenderRule], ...]:
        from .facade.catalog import OPERATIONS

        data = _mapping(value, source, where)
        result: list[tuple[str, str | None, RenderRule]] = []
        fields = frozenset(inspect.signature(RenderRule).parameters) - {"kind"}
        for operation_id, targets in data.items():
            if operation_id not in OPERATIONS:
                raise _error(source, where, f"unknown operation ID {operation_id!r}")
            target_map = _mapping(
                targets, source, f"{where}.{operation_id}", frozenset({"default", "ascii", "unicode", "latex"})
            )
            for target, specification in target_map.items():
                rule_map = _mapping(specification, source, f"{where}.{operation_id}.{target}", fields | {"kind"})
                if "kind" not in rule_map:
                    raise _error(source, where, "render rule requires kind")
                kwargs = dict(rule_map)
                for key in ("symbol", "opening", "closing", "numerator_closing", "denominator_closing"):
                    if isinstance(kwargs.get(key), Mapping):
                        spelling = _mapping(
                            kwargs[key], source, f"{where}.{key}", frozenset({"ascii", "unicode", "latex"})
                        )
                        if "ascii" not in spelling:
                            raise _error(source, where, f"{key} requires an ascii spelling")
                        try:
                            kwargs[key] = Name(**spelling)
                        except (TypeError, ValueError) as error:
                            raise _error(source, f"{where}.{operation_id}.{target}.{key}", str(error)) from error
                try:
                    rule = RenderRule(**kwargs)
                except (TypeError, ValueError) as error:
                    raise _error(source, f"{where}.{operation_id}.{target}", str(error)) from error
                if rule.kind == "unit_fraction" and operation_id != "unit":
                    raise _error(source, f"{where}.{operation_id}.{target}", "unit_fraction is only valid for unit")
                result.append((operation_id, None if target == "default" else target, rule))
        return tuple(result)

    def notation(self, name: str) -> Notation | NotationPatch:
        """Return one named complete notation or sparse patch."""
        return self._notation(name, ())

    def _presentation(self, name: str, stack: tuple[str, ...]) -> PresentationRecipe:
        if name in stack:
            raise ConfigError(f"presentation reference cycle: {' -> '.join((*stack, name))}")
        entry = self._entry("presentations", name)
        data = _mapping(entry.value, entry.source, f"presentations.{name}", _PRESENTATION_FIELDS | {"extends"})
        base = PresentationRecipe()
        if "extends" in data:
            ref = _reference(data["extends"], entry.source, f"presentations.{name}.extends")
            base = self._presentation(ref, (*stack, name))
        own = self._recipe({key: value for key, value in data.items() if key != "extends"}, entry.source)
        return compose(base, own)

    def presentation(self, name: str) -> PresentationRecipe:
        """Return one named dimension-independent presentation recipe."""
        return self._presentation(name, ())

    def _recipe(self, value: Any, source: Path) -> PresentationRecipe:
        data = _mapping(value, source, "presentation", _PRESENTATION_FIELDS)
        blades: BladeRecipe | None = None
        if "blades" in data:
            setting = _mapping(data["blades"], source, "presentation.blades", frozenset({"preset", "args"}))
            preset = _name(setting.get("preset"), source, "presentation.blades.preset")
            if preset not in _BLADE_PRESETS:
                raise _error(source, "presentation.blades", f"unknown blade preset {preset!r}")
            args = _mapping(setting.get("args", {}), source, "presentation.blades.args")
            blades = BladeRecipe(preset, tuple(args.items()))
        notation: Notation | NotationPatch | None = None
        if "notation" in data:
            selection = data["notation"]
            if isinstance(selection, str):
                notation = self.notation(_reference(selection, source, "presentation.notation"))
            else:
                inline = _mapping(selection, source, "presentation.notation", frozenset({"reverse", "rules", "base"}))
                if "base" in inline:
                    raise _error(
                        source, "presentation.notation", "inline notation cannot use base; define a named notation"
                    )
                try:
                    notation = NotationPatch(
                        reverse=inline.get("reverse"),
                        rules=self._rules(inline.get("rules", {}), source, "presentation.notation.rules"),
                    )
                except (TypeError, ValueError) as error:
                    raise _error(source, "presentation.notation", str(error)) from error
        local_names: LocalNameRecipe | None = None
        if "local_names" in data:
            selection = data["local_names"]
            if selection == "from_blades":
                local_names = LocalNameRecipe(from_blades=True)
            else:
                setting = _mapping(selection, source, "presentation.local_names", frozenset({"entries"}))
                entries = _mapping(setting.get("entries"), source, "presentation.local_names.entries")
                refs: list[tuple[str, BladeRef]] = []
                for key, value in entries.items():
                    spec = _mapping(
                        value, source, f"presentation.local_names.entries.{key}", frozenset({"mask", "sign"})
                    )
                    if "mask" not in spec:
                        raise _error(source, "presentation.local_names", "blade reference requires mask")
                    try:
                        refs.append((key, BladeRef(spec["mask"], spec.get("sign", 1))))
                    except (TypeError, ValueError) as error:
                        raise _error(source, f"presentation.local_names.entries.{key}", str(error)) from error
                local_names = LocalNameRecipe(entries=tuple(refs))
        order: DisplayOrderRecipe | None = None
        if "display_order" in data:
            selection = data["display_order"]
            if isinstance(selection, str):
                if selection not in {"grade-lexicographic", "bitmap"}:
                    raise _error(source, "presentation.display_order", "unknown display order")
                order = DisplayOrderRecipe(selection)
            elif isinstance(selection, list):
                if any(type(mask) is not int for mask in selection):
                    raise _error(source, "presentation.display_order", "mask list must contain integers")
                order = DisplayOrderRecipe("explicit", tuple(selection))
            else:
                raise _error(source, "presentation.display_order", "expected a named order or mask list")
        display: DisplayPolicy | None = None
        if "display" in data:
            setting = _mapping(
                data["display"],
                source,
                "presentation.display",
                frozenset({"content", "target", "zero_tolerance", "coefficient_precision"}),
            )
            try:
                display = DisplayPolicy(**setting)
            except (TypeError, ValueError) as error:
                raise _error(source, "presentation.display", str(error)) from error
        return PresentationRecipe(
            blades=blades,
            notation=notation,
            local_names=local_names,
            display_order=order,
            display=display,
        )

    def default_recipe(self) -> PresentationRecipe:
        """Combine sparse presentation defaults from every discovered file."""
        result = PresentationRecipe()
        for entry in self._defaults:
            setting = _mapping(entry.value, entry.source, "defaults", frozenset({"presentation"}))
            if "presentation" in setting:
                result = compose(result, self._recipe(setting["presentation"], entry.source))
        return result

    def presenter(self, name: str) -> Presenter:
        """Return a reusable named presenter."""
        entry = self._entry("presenters", name)
        data = _mapping(
            entry.value, entry.source, f"presenters.{name}", _PRESENTATION_FIELDS | {"presentation", "content"}
        )
        recipe = PresentationRecipe()
        if "presentation" in data:
            recipe = self.presentation(
                _reference(data["presentation"], entry.source, f"presenters.{name}.presentation")
            )
        own = self._recipe({key: value for key, value in data.items() if key in _PRESENTATION_FIELDS}, entry.source)
        recipe = compose(recipe, own)
        content = data.get("content")
        return Presenter(config=recipe, content=content)

    def algebra(self, name: str) -> AlgebraConfig:
        """Return a complete named algebra snapshot with defaults applied."""
        from . import presets

        entry = self._entry("algebras", name)
        data = _mapping(
            entry.value,
            entry.source,
            f"algebras.{name}",
            frozenset({"preset", "args", "pqr", "signature", "gram", "presentation"}),
        )
        sources = set(data) & {"preset", "pqr", "signature", "gram"}
        if len(sources) != 1:
            raise _error(entry.source, f"algebras.{name}", "choose exactly one of preset, pqr, signature, or gram")
        if "preset" in data:
            preset_name = _name(data["preset"], entry.source, f"algebras.{name}.preset")
            if preset_name not in _PRESETS:
                raise _error(entry.source, f"algebras.{name}", f"unknown algebra preset {preset_name!r}")
            factory = getattr(presets, preset_name)
            args = _mapping(data.get("args", {}), entry.source, f"algebras.{name}.args")
            try:
                inspect.signature(factory).bind(**args)
                base = factory(**args).build()
            except (TypeError, ValueError) as error:
                raise _error(entry.source, f"algebras.{name}.args", str(error)) from error
        else:
            if "args" in data:
                raise _error(entry.source, f"algebras.{name}", "args requires preset")
            try:
                if "pqr" in data:
                    counts = _mapping(data["pqr"], entry.source, f"algebras.{name}.pqr", frozenset({"p", "q", "r"}))
                    definition = AlgebraDefinition.from_pqr(**counts)
                elif "signature" in data:
                    definition = AlgebraDefinition.from_signature(data["signature"])
                else:
                    definition = AlgebraDefinition(data["gram"])
            except (TypeError, ValueError) as error:
                raise _error(entry.source, f"algebras.{name}", str(error)) from error
            base = AlgebraConfig(definition, default_presentation(definition.dimension))
        selected = self.default_recipe().apply(base)
        if "presentation" in data:
            selection = data["presentation"]
            recipe = (
                self.presentation(_reference(selection, entry.source, f"algebras.{name}.presentation"))
                if isinstance(selection, str)
                else self._recipe(selection, entry.source)
            )
            selected = recipe.apply(selected)
        return selected


def load(*, start: Path | None = None, files: Sequence[Path] | None = None) -> Settings:
    """Read and validate global and ancestor TOML configuration files."""
    sources = _discover(start, files)
    defaults: list[_Entry] = []
    names: dict[str, dict[str, _Entry]] = {section: {} for section in _SECTIONS}
    for path in sources:
        data = _parse(path)
        if "defaults" in data:
            defaults.append(_Entry(_mapping(data["defaults"], path, "defaults"), path))
        for section in _SECTIONS:
            section_map = _mapping(data.get(section, {}), path, section)
            for name, value in section_map.items():
                _name(name, path, section)
                names[section][name] = _Entry(_mapping(value, path, f"{section}.{name}"), path)
    return Settings(
        sources=sources,
        _defaults=tuple(defaults),
        _names=MappingProxyType({section: MappingProxyType(entries) for section, entries in names.items()}),
    )


def reload() -> Settings:
    """Read a fresh snapshot; the loader does not retain a process cache."""
    return load()


def apply_defaults(presentation: Any, gram: Any) -> Any:
    """Apply current file defaults to a newly constructed facade algebra."""
    return load().default_recipe().apply_to(presentation, gram)


__all__ = ["ConfigError", "Settings", "load", "reload"]
