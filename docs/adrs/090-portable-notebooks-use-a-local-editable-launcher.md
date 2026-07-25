---
status: accepted
date: 2026-07-25
deciders: edouard
---

# ADR-090: Portable Notebooks Use a Local Editable Launcher

## Context and problem statement

The example Marimo notebooks previously began with a cell that derived the
repository root from `__file__` and inserted local package directories into
`sys.path`. This let a checkout exercise uncommitted Galaga code, but it made
the notebook source dependent on the repository layout. A copied notebook
could not run against released packages without first deleting or changing
that cell.

Runtime path mutation also bypasses normal package installation semantics.
Most notably, source imported through `PYTHONPATH` can be paired accidentally
with distribution metadata from a different installed version.

## Decision drivers

- Keep example notebook source usable inside and outside the repository.
- Exercise uncommitted code during local development.
- Preserve correct distribution metadata and optional-package boundaries.
- Keep repository setup out of Marimo's reactive dependency graph.
- Provide one memorable entry point for the complete example gallery.
- Permit local Marimo integrations that require unauthenticated access.

## Decision outcome

Example notebooks contain ordinary package imports and no repository discovery
or `sys.path` mutation.

From the repository root, `make run-marimo` launches the `examples` gallery
under Python 3.14. The target supplies `galaga`, `galaga_marimo`,
`galaga_matrix`, and `galaga_mermaid` to `uv run` through
`--with-editable`. The imports therefore resolve to the current checkout while
retaining the same installed-package semantics and metadata used by wheels.

The launcher passes `--no-token` to Marimo deliberately. Marimo retains its
default loopback host, so this is intended for local development and automation
only. A developer exposing Marimo on another interface must choose appropriate
authentication and network controls separately.

Outside the repository, the same notebooks run unchanged after their required
packages are installed:

```shell
python -m pip install galaga galaga-marimo
marimo edit notebook.py
```

Repository tests scan every Marimo notebook under `examples`, reject
repository-path cells, validate the launch command, and continue to execute the
maintained gallery headlessly.

## Consequences

- Good, because notebooks become portable teaching artifacts rather than
  repository-bound programs.
- Good, because local execution still uses uncommitted source from every
  companion package.
- Good, because `importlib.metadata` observes the metadata of the selected
  editable package instead of an unrelated installed release.
- Good, because Marimo no longer sees repository bootstrapping as a reactive
  notebook cell.
- Good, because `make run-marimo` is the single local entry point.
- Cost, because the first launch may resolve or build editable companion
  packages.
- Risk, because `--no-token` removes Marimo token authentication; the launcher
  therefore relies on the default loopback binding and is not a public-server
  configuration.
