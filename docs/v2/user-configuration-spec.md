# User Configuration Files for Galaga 2

**Status:** Implemented on the Galaga 2 development branch. See
[ADR-171](../adrs/171-layered-yaml-presentation-preferences.md).

## Purpose

A user should be able to set recurring presentation preferences once, such as
coefficient precision, blade labels, or the LaTeX glyph for a Hodge dual. A
project should be able to override those preferences. Named notations,
presentation recipes, presenters, and algebra configurations should be
reusable from Python without embedding Python code in YAML.

The numeric meaning of an algebra must remain explicit. A default preference
can change how a result is shown; it must not silently change a Gram matrix,
product backend, expression tracking, or the mathematical operation called.

## Files and discovery

The global file is `~/.config/galaga_python/config.yaml`. If
`XDG_CONFIG_HOME` is set, use `$XDG_CONFIG_HOME/galaga_python/config.yaml`
instead. A local override is a YAML file named `.galaga_python` in the current
working directory or any of its ancestors. The local name is a file, rather
than a directory.

For a working directory `/work/project/notebooks`, read existing files in this
order:

1. The global file.
2. `/.galaga_python`, `/work/.galaga_python`,
   `/work/project/.galaga_python`, then
   `/work/project/notebooks/.galaga_python`.

The closest file has the last word. Discovery uses the process working
directory at the time a configuration snapshot is loaded, not the location of
an imported module or notebook. A missing file contributes nothing. Do not
read or write configuration during `import galaga`.

`GALAGA_CONFIG=none` disables discovery and uses built-in defaults.
`GALAGA_CONFIG=/absolute/path/to/config.yaml` loads only that file, which makes
scripts and tests independent of a developer's home and working directory.
Relative paths, a missing explicit path, and other special values are errors.
An explicit `load(start=..., files=...)` Python call can select sources without
changing the process environment.

Each file must be a mapping with `version: 1`. Use a safe YAML parser: no
Python object tags, executable constructors, or arbitrary imports. Reject
duplicate keys and unknown fields with the file path and field path or parser
location in the error. The loader rejects files larger than 1 MiB and YAML
aliases. A malformed file fails when loaded; it must not be silently ignored.

## File shape

```yaml
version: 1

defaults:
  presentation:
    notation: {ref: textbook}
    display:
      coefficient_precision: 5

notations:
  textbook:
    reverse: dagger
    rules:
      right_hodge_dual:
        latex: {kind: superscript, symbol: '\star'}
      left_hodge_dual:
        latex: {kind: subscript, symbol: '\star'}

presentations:
  article:
    notation: {ref: textbook}
    display:
      target: latex
      content: full
      coefficient_precision: 7

presenters:
  article_value:
    presentation: {ref: article}
    display: {content: value}

algebras:
  spacetime_article:
    preset: sta
    args: {signature: mostly-minus, sigmas: true}
    presentation: {ref: article}
```

The Hodge example changes only LaTeX rendering of the two named Hodge
operations. It does not redefine `dual`, which has its own operation ID and
may have different mathematical semantics. A user who also wants `dual` to
print with `\star` must set a separate `dual` rule.

### Defaults

`defaults.presentation` is a sparse presentation recipe. It may contain
`blades`, `notation`, `local_names`, `display_order`, and `display`.
Unspecified slots inherit from the algebra's normal presentation, including
the presentation supplied by a complete preset. Display fields merge
individually, following `DisplayPolicy`'s sparse behavior. Notation rules
merge by stable operation ID and optional target; changing one rule preserves
other preset rules. Blade recipes resolve after the Gram matrix is known.

For example, an indexed blade preference can omit the dimension:

```yaml
defaults:
  presentation:
    blades:
      preset: indexed
      args: {prefix: v}
    display_order: grade-lexicographic
```

The loader supplies the algebra dimension to a dimension-dependent blade
factory and validates the resulting convention against the actual Gram
matrix. Fixed-dimension or metric-specific blade recipes raise a clear error
if applied to an incompatible algebra. A blade override does not silently
change Python local names. Use `local_names: from_blades` to derive them from
the selected convention, or supply a complete `entries` mapping from Python
identifiers to `{mask, sign}` blade references. The loader supplies and
validates the algebra dimension. `display_order` accepts
`grade-lexicographic`, `bitmap`, or an explicit list of native blade masks.

### Named objects

`notations` entries are sparse notation patches by default. `reverse` accepts
`tilde` or `dagger`; `rules` accepts operation IDs from the public operation
catalog. Rule keys are `ascii`, `unicode`, `latex`, or `default`, each holding
a `RenderRule` description. `symbol` may be a string or a mapping with
`ascii`, `unicode`, and `latex` fields; strings apply to the selected target.
Rule kinds and their fields use the existing `RenderRule` validation. A
notation may instead start from a built-in preset with
`base: {preset: hestenes}` (or another named notation with
`base: {ref: name}`). Its own rules apply last. Reference cycles are errors.

`presentations` entries are dimension-independent `PresentationRecipe`
values. They accept the same slots as `defaults.presentation`, plus
`extends: {ref: other_presentation}`. The base recipe applies first; supplied
fields apply second. They do not contain a metric.

`presenters` entries resolve to `Presenter` values. They may refer to a named
presentation recipe and then supply additional sparse presentation fields or
`content`. Applying a presenter captures the resulting view as it does today;
it does not mutate the algebra.

`algebras` entries choose one complete preset through `preset` and `args`, or
an explicit `pqr`, `signature`, or `gram` definition. Exactly one numeric
source is required. A named algebra may attach a named or inline presentation
recipe. It resolves to an `AlgebraConfig` whose metric and model come from
the selected numeric source. YAML does not create Python classes or invoke
factories outside an explicit Galaga allowlist. Preset arguments are validated
against the actual factory signature. Named algebras cannot change the metric
through a presentation reference.

Names are unique within each section; the same name may occur in different
sections because references are typed. `{ref: ...}` always refers to the
section expected by its field. A missing or cyclic reference is an error.

## Layering and precedence

The global file and ancestor files are merged from least to most local.
`defaults.presentation` merges sparsely, using the same right-biased slot and
rule behavior as Python's `|` composition. A later file's definition of a
named notation, presentation, presenter, or algebra replaces that entire
named definition. This avoids implicit deep merging of a profile's numeric
definition or inheritance graph; `extends` is the explicit reuse mechanism.

For facade algebra construction, presentation precedence is:

1. Galaga's built-in presentation or the complete preset's presentation.
2. Resolved user and local `defaults.presentation`.
3. A selected named algebra's presentation recipe.
4. Explicit constructor `presentation=`, `blades=`, `notation=`,
   `local_names=`, `display_order=`, and `display=` arguments.
5. Later `with_*` and scoped `use_*` overrides.
6. An explicit per-render override or an applied `Presenter`.

An explicitly constructed `AlgebraConfig` or `PresentationConfig` is an exact
snapshot and bypasses ambient file defaults. A named algebra is resolved with
the file defaults before it becomes such a snapshot. `galaga.core` and the
pure `default_presentation(n)` factory never consult files. `Algebra.from_numeric`
uses file defaults only when no explicit presentation is supplied. Existing
algebras and captured presenter views do not change if a file is edited.

## Python API

```python
from galaga import Algebra, config, presets

# File defaults apply automatically to new facade algebras.
space = Algebra(config=presets.euclidean(3))

# Explicitly load a snapshot and select named objects.
settings = config.load()
sta = Algebra(config=settings.algebra("spacetime_article"))
article_value = settings.presenter("article_value")
rendered = article_value(sta.basis_vectors()[0])

# Named notation and presentation recipes also work with existing APIs.
other = space.with_notation(settings.notation("textbook"))
with space.use_presentation(settings.presentation("article")):
    shown = space.basis_vectors()[0].display()
```

`config.load()` returns an immutable snapshot with `sources`, `notation(name)`,
`presentation(name)`, `presenter(name)`, and `algebra(name)` accessors. A
resolved name returns existing Galaga configuration types, not a new parallel
object model. An unknown name reports the section and searched sources.
Automatic construction rereads configuration, so changes to a file are
visible on the next new algebra without restarting a notebook.
`config.reload()` explicitly reads a fresh snapshot. Each algebra keeps the
resolved presentation it had at construction time.

## Implementation boundary

The file loader is an adapter over `AlgebraConfig`, `PresentationRecipe`,
`Presenter`, `DisplayPolicy`, `Notation`, and `RenderRule`. `NotationPatch`
supports rule-level overrides, so a sparse YAML setting preserves a preset's
other rules. The YAML parser is a direct dependency of `galaga` because
default loading is automatic, but parsing is deferred until a configuration
source is needed. `galaga.core` remains free of file and YAML dependencies.

Version 1 does not support executable expressions, imports, environment
interpolation inside YAML, arbitrary factory calls, or automatic numeric
defaults. Later schema changes require a new `version` value rather than
guessing how to interpret an older file.

## Acceptance criteria

- Global and every ancestor file apply in documented order; the nearest
  override wins. The environment controls provide hermetic behavior.
- `Algebra(3)`, `Algebra(config=presets.sta())`, and
  `Algebra.from_numeric(...)` receive sparse defaults as specified, while
  explicit snapshots, `galaga.core`, and existing algebras remain unchanged.
- A LaTeX `\star` override affects the requested operation IDs and target only;
  its products and other notation rules are unchanged.
- Named notation, presentation, presenter, and algebra profiles resolve to the
  existing Python types and compose with the current `|`, `with_*`, and
  `use_*` APIs.
- Invalid YAML, unknown factories/operation IDs, incompatible dimensions,
  ambiguous numeric sources, and reference cycles fail with actionable paths.
- Unit tests cover precedence, explicit overrides, cwd changes, file edits,
  safe parsing, and parallel or scoped use. Documentation examples execute.
