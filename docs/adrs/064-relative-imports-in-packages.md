---
status: accepted
date: 2026-04-12
deciders: edouard
---

# ADR-064: Use Relative Imports Within Packages

## Context and Problem Statement

The `galaga` and `galaga_mermaid` packages used absolute imports internally
(e.g. `from galaga.algebra import ...`). This works when the package is
installed via `pip install` or `pip install -e .`, because the package name
is registered in `sys.modules`.

However, when importing via a filesystem path — as Marimo notebooks do with
`from packages.galaga.galaga import ...` — Python sees the package under a
different module path. The absolute imports then fail because `galaga` is not
in `sys.modules`; only `packages.galaga.galaga` is.

This caused two classes of failure:
1. `ModuleNotFoundError` on import (galaga_mermaid).
2. `isinstance` checks failing with "got BladeConvention" because the same
   class was loaded from two different module paths, producing two distinct
   class objects (galaga).

## Decision

Use relative imports (e.g. `from .algebra import ...`, `from . import expr`)
for all intra-package references in library source code.

Test files continue to use absolute imports since they run with the package
installed.

## Consequences

- Packages work correctly whether installed via pip or imported by path.
- No impact on PyPI users — relative imports are the standard mechanism
  (PEP 328) and resolve identically to absolute imports when installed.
- `isinstance` checks no longer break due to dual module identity.
