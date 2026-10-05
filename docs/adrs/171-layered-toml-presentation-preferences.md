---
status: accepted
date: 2026-10-04
amended: 2026-10-05
deciders: edouard
---

# ADR-171: Layered TOML Presentation Preferences

## Context

Galaga's immutable presentation components and right-biased recipes support
local overrides, but users must repeat their usual notation and display
choices in each script or notebook. A user-level preference and closer
project-level overrides should feed the same component model without making
numeric operations depend on files.

TOML is available through `tomllib` on every supported Python version. It
keeps Galaga's direct runtime dependencies limited to NumPy while providing
unambiguous tables, strings, and duplicate-key errors for this schema.

## Decision

Load a global TOML file at `$XDG_CONFIG_HOME/galaga_python/config.toml`, or
`~/.config/galaga_python/config.toml` when XDG is unset. Then load each
`.galaga_python.toml` file from the filesystem root through the process working
directory. Apply sparse defaults in that order when constructing a new
facade algebra. A complete `AlgebraConfig` or explicit `PresentationConfig`
remains an exact snapshot. The numeric core does not load configuration.

The loader does not consult `GALAGA_CONFIG`; an environment variable must not
redirect Galaga to an arbitrary configuration file.
`galaga.config.load(files=...)` selects files explicitly and returns a
snapshot with named notation, presentation, presenter, and algebra accessors. A later
file replaces a same-named profile in full; its sparse presentation defaults
compose with earlier defaults. Named algebra profiles choose their numeric
definition explicitly and resolve to ordinary `AlgebraConfig` values.

Named references use an `@`-prefixed TOML string in fields that expect a
reference, for example `notation = "@textbook"` and
`extends = "@base"`. The field determines the referenced section. Profile
names may not begin with `@`, and an empty reference is invalid. Inline
presentation and notation settings remain tables; a built-in notation base
uses `{ preset = "hestenes" }`. This keeps references distinct from literal
strings and removes the extra `{ ref = "name" }` wrapper.

The facade constructor also accepts `Algebra(config="@name")`. It resolves
that name from the discovered `algebras` profiles and uses the resulting
complete `AlgebraConfig` snapshot, including file defaults. The `@` marks an
explicit file lookup that can determine the metric. Bare names are invalid,
and `user_config_files=False` rejects this form before reading files.

The file format uses a versioned, allowlisted schema and Python's standard
library `tomllib` parser. Duplicate keys, unknown fields, malformed TOML,
and files over 1 MiB are rejected. No configuration is read at import time.
Files are read when a new facade algebra or an explicit settings snapshot is created,
so notebook edits affect new algebras without changing existing ones.
The facade imports the configuration adapter normally; only file discovery
and parsing are deferred. The adapter does not import the facade's numeric
implementation during module initialization.

`Algebra(..., user_config_files=False)` and
`Algebra.from_numeric(..., user_config_files=False)` skip ambient file
discovery for that construction. The default is `True`. This provides a
per-algebra opt out while retaining explicitly supplied presentation settings.

Extend sparse notation patches from `reverse` alone to target-specific
`RenderRule` replacements. A notation patch retains the base notation's
other rules and changes only the listed operation IDs and targets. File
recipes resolve blades, local names, and display ordering against the actual
algebra dimension and Gram matrix.

Blade preset arguments may appear beside `preset`, as in
`blades = { preset = "indexed", prefix = "v" }`. The original nested `args`
table remains valid for existing files. Duplicate arguments across the two
forms are rejected.

Notation rules in TOML accept both complete `RenderRule` tables and concise
strings. An operation-level string applies to ASCII, Unicode, and LaTeX;
one under an `ascii`, `unicode`, or `latex` key applies only to that target.
The complete table form remains available for precedence, argument order,
and other options outside the shorthand.

## Consequences

The base `galaga` package retains NumPy as its only direct runtime dependency.
Presentation can vary by working directory, so reproducible applications and
tests can use an explicit file selection or a captured `AlgebraConfig`.
Explicit constructor and scoped presentation choices keep
their existing precedence. The schema and public entry points are described
in the [user configuration specification](../v2/user-configuration-spec.md).

This extends the immutable configuration and sparse composition decisions in
ADR-076, ADR-161, ADR-162, and ADR-169.
