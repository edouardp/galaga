---
status: accepted
date: 2026-03-29
deciders: edouard
---

# ADR-040: Pyrefly for Type Checking

> The choice of Pyrefly remains accepted. The original non-blocking policy
> below is superseded by [ADR-131](131-local-only-stable-release-validation.md):
> type errors now fail local validation. Historical counts describe adoption,
> not the current source tree.

## Context and Problem Statement

The codebase uses dynamic patterns (isinstance dispatch, optional fields,
union parameters) that work correctly at runtime but have no static type
verification. Type errors could be introduced silently.

## Decision Outcome

Use Pyrefly (Meta's Rust-based type checker) as a non-blocking warning.
At adoption it reported 138 errors, mostly from untyped Expr/LNode subclass
dispatch. The living [Pyrefly status](../PYREFLY_STATUS.md) records how to
measure the current tree; an ADR does not carry a mutable error count.

### Why Pyrefly over Mypy

- Faster (Rust-based)
- Better error messages
- Active development by Meta
- Used in the reference project (hello_world_api_lambda_container)

### Path to Zero Errors

See `docs/PYREFLY_STATUS.md` for the current breakdown and release policy.

### Consequences

- Good, because it surfaces real type safety issues
- Good, because non-blocking means it doesn't slow development
- Bad, because the reported errors remain technical debt until addressed
- Goal: make blocking once errors reach zero
