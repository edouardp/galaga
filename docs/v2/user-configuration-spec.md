# User Configuration Files for Galaga 2

The configuration system is implemented in `galaga.config`. See
[ADR-171](../adrs/171-layered-toml-presentation-preferences.md).

## Purpose

A user should be able to set recurring presentation preferences once, such as
coefficient precision, blade labels, or the LaTeX glyph for a Hodge dual. A
project should be able to override those preferences. Named notations,
presentation recipes, presenters, and algebra configurations should be
reusable from Python without embedding Python code in TOML.

The numeric meaning of an algebra must remain explicit. A default preference
can change how a result is shown; it must not silently change a Gram matrix,
product backend, expression tracking, or the mathematical operation called.

## Files and discovery

The global file is `~/.config/galaga_python/config.toml`. If
`XDG_CONFIG_HOME` is set, use `$XDG_CONFIG_HOME/galaga_python/config.toml`
instead. A local override is a TOML file named `.galaga_python.toml` in the current
working directory or any of its ancestors. The local name is a file, rather
than a directory.

For a working directory `/work/project/notebooks`, read existing files in this
order:

1. The global file.
2. `/.galaga_python.toml`, `/work/.galaga_python.toml`,
   `/work/project/.galaga_python.toml`, then
   `/work/project/notebooks/.galaga_python.toml`.

The closest file has the last word. Discovery uses the process working
directory at the time a configuration snapshot is loaded, not the location of
an imported module or notebook. A missing file contributes nothing. Do not
read or write configuration during `import galaga`.

An explicit `load(start=..., files=...)` Python call can select sources without
changing the process environment. `files` loads exactly the paths supplied;
the `GALAGA_CONFIG` environment variable has no effect on discovery.

For one algebra, pass `user_config_files=False` to `Algebra(...)` or
`Algebra.from_numeric(...)`. This skips file discovery for that construction;
the default is `True`. Explicit presentation arguments still apply. A named
algebra reference in `config="@name"` requires file loading and cannot be
combined with `user_config_files=False`.

Each file must be a TOML document with `version = 1`. Python's standard
library `tomllib` parser rejects malformed TOML and duplicate keys. Galaga
rejects unknown fields and files larger than 1 MiB. Errors include the file
path and field path or parser location. A malformed file fails when loaded;
it is never silently ignored.

## File shape

See the [copyable example](../../examples/galaga-user-config.toml) for a
complete user configuration file.

```toml
version = 1

[defaults.presentation]
notation = "@textbook"

[defaults.presentation.display]
coefficient_precision = 5

[notations.textbook]
reverse = "dagger"

[notations.textbook.rules.right_hodge_dual.latex]
kind = "superscript"
symbol = '\star'

[notations.textbook.rules.left_hodge_dual.latex]
kind = "subscript"
symbol = '\star'

[presentations.article]
notation = "@textbook"

[presentations.article.display]
target = "latex"
content = "full"
coefficient_precision = 7

[presenters.article_value]
presentation = "@article"
display = { content = "value" }

[algebras.spacetime_article]
preset = "sta"
args = { signature = "mostly-minus", sigmas = true }
presentation = "@article"
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

```toml
version = 1

[defaults.presentation]
blades = { preset = "indexed", prefix = "v" }
display_order = "grade-lexicographic"
```

Preset options may sit beside `preset` as above. The earlier
`args = { prefix = "v" }` form remains valid; arguments repeated in both
places are rejected. The loader supplies the algebra dimension to a
dimension-dependent blade factory and validates the resulting convention
against the actual Gram matrix. Fixed-dimension or metric-specific blade
recipes raise a clear error if applied to an incompatible algebra. A blade
override does not silently change Python local names. Use
`local_names = "from_blades"` to derive them from
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
`base = { preset = "hestenes" }` (or another named notation with
`base = "@name"`). Its own rules apply last. Reference cycles are errors.

Common rules can use a compact string. An operation-level string applies to
ASCII, Unicode, and LaTeX, replacing any target-specific preset rules for
that operation. A string under a target key affects only that target:

```toml
[notations.textbook.rules]
half_commutator = "wrapper:1/2[,]"

[notations.textbook.rules.right_hodge_dual]
latex = "superscript:star"

[notations.textbook.rules.left_hodge_dual.latex]
kind = "subscript"
symbol = '\star'
```

The last entry demonstrates the complete rule table, which remains available
for fields such as `precedence`, `argument_order`, and `scalable`. Compact
forms use `kind:symbol` for `prefix`, `postfix`, `infix`, `function`,
`superscript`, `subscript`, `accent`, and `underaccent`; use
`wrapper:opening,closing` for fixed delimiters. Recognized symbol names such
as `star` derive all three spellings through `Name.from_latex`. The `1/2`
wrapper prefix yields `1/2`, `½`, and `\tfrac{1}{2}`. Full rules are needed
for delimiters containing a comma or other specialized settings. Symbol-free
layouts `fraction`, `juxtaposition`, `sandwich`, `metric_regressive`, and
`unit_fraction` can be written as bare strings; `unit_fraction` applies only
to the `unit` operation.

`presentations` entries are dimension-independent `PresentationRecipe`
values. They accept the same slots as `defaults.presentation`, plus
`extends = "@other_presentation"`. The base recipe applies first; supplied
fields apply second. They do not contain a metric.

`presenters` entries resolve to `Presenter` values. They may refer to a named
presentation recipe and then supply additional sparse presentation fields or
`content`. Applying a presenter captures the resulting view as it does today;
it does not mutate the algebra.

`algebras` entries choose one complete preset through `preset` and `args`, or
an explicit `pqr`, `signature`, or `gram` definition. Exactly one numeric
source is required. A named algebra may attach a named or inline presentation
recipe. It resolves to an `AlgebraConfig` whose metric and model come from
the selected numeric source. TOML does not create Python classes or invoke
factories outside an explicit Galaga allowlist. Preset arguments are validated
against the actual factory signature. Named algebras cannot change the metric
through a presentation reference.

Names are unique within each section; the same name may occur in different
sections because references are typed. A string beginning with `@` refers to
the section expected by its field, such as `notation = "@textbook"` or
`presentation = "@article"`. The prefix is reserved in profile names; an
empty `@`, an unmarked name, or a missing or cyclic reference is an error.
The marker has meaning only in reference fields, so ordinary strings such as
`local_names = "from_blades"` remain literal values.

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

# Use built-in presentation defaults for just this construction.
plain_space = Algebra(3, user_config_files=False)

# Explicitly load a snapshot and select named objects.
settings = config.load()
sta = Algebra(config=settings.algebra("spacetime_article"))
# Or select a named algebra directly from the discovered files.
sta_from_files = Algebra(config="@spacetime_article")
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
`Algebra(config="@name")` rereads discovered files and selects the named
`algebras` profile. This can change the metric if the selected profile changes
with the working directory or file contents. Passing a previously resolved
`AlgebraConfig` instead uses that exact snapshot.

## Implementation boundary

The file loader is an adapter over `AlgebraConfig`, `PresentationRecipe`,
`Presenter`, `DisplayPolicy`, `Notation`, and `RenderRule`. `NotationPatch`
supports rule-level overrides, so a sparse TOML setting preserves a preset's
other rules. TOML parsing uses Python 3.11+'s standard library `tomllib`;
the parser adds no runtime dependency. Parsing is deferred until a
configuration source is needed. `galaga.core` remains free of file dependencies.

Version 1 does not support executable expressions, imports, environment
interpolation inside TOML, arbitrary factory calls, or automatic numeric
defaults. Later schema changes require a new `version` value rather than
guessing how to interpret an older file.

## Acceptance criteria

- Global and every ancestor file apply in documented order; the nearest
  override wins. Explicit `files` selection provides a controlled snapshot.
- `Algebra(3)`, `Algebra(config=presets.sta())`, and
  `Algebra.from_numeric(...)` receive sparse defaults as specified, while
  explicit snapshots, `galaga.core`, and existing algebras remain unchanged.
- A LaTeX `\star` override affects the requested operation IDs and target only;
  its products and other notation rules are unchanged.
- Named notation, presentation, presenter, and algebra profiles resolve to the
  existing Python types and compose with the current `|`, `with_*`, and
  `use_*` APIs. `Algebra(config="@name")` resolves a discovered named algebra,
  while `user_config_files=False` rejects that form before file access.
- Invalid TOML, unknown factories/operation IDs, incompatible dimensions,
  ambiguous numeric sources, and reference cycles fail with actionable paths.
- Unit tests cover precedence, explicit overrides, cwd changes, file edits,
  safe parsing, and parallel or scoped use. Documentation examples execute.
