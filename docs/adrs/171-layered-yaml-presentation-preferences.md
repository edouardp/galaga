---
status: accepted
date: 2026-10-04
deciders: edouard
---

# ADR-171: Layered YAML Presentation Preferences

## Context

Galaga's immutable presentation components and right-biased recipes support
local overrides, but users must repeat their usual notation and display
choices in each script or notebook. A user-level preference and closer
project-level overrides should feed the same component model without making
numeric operations depend on files.

## Decision

Load a global YAML file at `$XDG_CONFIG_HOME/galaga_python/config.yaml`, or
`~/.config/galaga_python/config.yaml` when XDG is unset. Then load each
`.galaga_python` file from the filesystem root through the process working
directory. Apply sparse defaults in that order when constructing a new
facade algebra. A complete `AlgebraConfig` or explicit `PresentationConfig`
remains an exact snapshot. The numeric core does not load configuration.

`GALAGA_CONFIG=none` disables discovery. An absolute file path in that
variable selects only that file. `galaga.config.load()` returns a snapshot
with named notation, presentation, presenter, and algebra accessors. A later
file replaces a same-named profile in full; its sparse presentation defaults
compose with earlier defaults. Named algebra profiles choose their numeric
definition explicitly and resolve to ordinary `AlgebraConfig` values.

The file format uses a versioned, allowlisted schema and a safe YAML parser.
YAML aliases, duplicate keys, unknown fields, Python object tags, and files
over 1 MiB are rejected. No configuration is read at import time. Files are
read when a new facade algebra or an explicit settings snapshot is created,
so notebook edits affect new algebras without changing existing ones.
The facade imports the configuration adapter normally; only file discovery
and parsing are deferred. The adapter does not import the facade's numeric
implementation during module initialization.

Extend sparse notation patches from `reverse` alone to target-specific
`RenderRule` replacements. A notation patch retains the base notation's
other rules and changes only the listed operation IDs and targets. File
recipes resolve blades, local names, and display ordering against the actual
algebra dimension and Gram matrix.

## Consequences

The base `galaga` package directly depends on PyYAML; parsing remains lazy.
Presentation can vary by working directory, so reproducible applications and
tests can use `GALAGA_CONFIG=none`, an explicit file, or a captured
`AlgebraConfig`. Explicit constructor and scoped presentation choices keep
their existing precedence. The schema and public entry points are described
in the [user configuration specification](../v2/user-configuration-spec.md).

This extends the immutable configuration and sparse composition decisions in
ADR-076, ADR-161, ADR-162, and ADR-169.
