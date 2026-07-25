# Pyrefly Type-Checking Status

Pyrefly runs from `make lint` but remains advisory:

```bash
uv run pyrefly check
```

The repository configuration checks `packages/galaga/galaga/**/*.py`.
`scripts/lint.sh` reports the tail of its output and does not fail the lint
command when type errors remain.

## Current snapshot

On 2026-07-25, Pyrefly reported 298 errors. This number is diagnostic, not a
stable test contract. Measure the current tree rather than copying the count
into release notes.

The largest groups are:

- legacy Galaga 1 expression/rendering narrowing failures;
- old mutable blade-convention dictionary inference;
- `numbers.Real` versus built-in and NumPy scalar typing;
- optional values that runtime validation narrows more precisely than the type
  checker;
- semantic-renderer local-variable inference; and
- remaining legacy `symbolic_core` node narrowing.

Phase 9 deletion of the table-backed engine should remove a substantial part
of the first, second, and last groups. Current Galaga 2 modules still have real
issues of their own, so deleting legacy code is not equivalent to completing
the typing work.

## Release policy

For the 2.0 prerelease line:

- Pyrefly output must remain visible in `make lint`;
- new Galaga 2 code should not add avoidable errors;
- runtime tests, Ruff, package builds, and supported-version execution remain
  blocking; and
- no README or classifier should claim that the package is fully statically
  checked.

Before making Pyrefly a blocking gate, first narrow the configured project to
the post-Phase-9 source tree, establish a checked baseline, and then reduce it
to zero without broad ignores. When that policy changes, update
`scripts/lint.sh`, the release process, and this document together.
