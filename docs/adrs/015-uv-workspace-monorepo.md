---
status: accepted
date: 2026-03-25
deciders: edouard
---

# ADR-015: uv Workspace for Monorepo

## Context and Problem Statement

The project has two packages (`galaga` for the core GA library, `galaga-marimo`
for the notebook helper). How should they be organized?

## Decision Drivers

* The two packages have different dependencies (galaga: NumPy only; gamo: marimo)
* They should be developed together in one repository
* `uv` is already used for dependency management
* The notebook helper depends on the core library

## Decision Outcome

Use a uv workspace with the core library as a workspace member and the
notebook helper excluded (installed separately):

```toml
[tool.uv.workspace]
members = ["packages/galaga"]
exclude = ["packages/galaga_marimo"]
```

The core library lives at `packages/galaga/`, the notebook helper at
`packages/galaga_marimo/`. Development dependencies (marimo, pytest, matplotlib)
are in the root `pyproject.toml`.

### Consequences

* Good, because both packages live in one repo with shared git history
* Good, because `uv sync` sets up the development environment
* Good, because packages can be published independently
* Bad, because `gamo` is excluded from the workspace (can't use workspace source)
