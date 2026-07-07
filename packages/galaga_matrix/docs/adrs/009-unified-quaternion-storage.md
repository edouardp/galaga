---
status: accepted
date: 2026-07-08
deciders: edouard
---

# ADR-009: Unified Quaternion Storage — Always Numpy-Backed

## Context and Problem Statement

`mode="quaternion"` previously stored a `list[list[Quat]]` in `_qmat` with
`mat = None`. This created a parallel code path where arithmetic, basis
changes, `from_matrix`, `__array__`, and most operations were blocked with
`TypeError`. Users had to switch to compact mode for any computation.

The quaternion-block representation IS a complex matrix internally — each
quaternion embeds as a 2×2 complex block. We were computing this internally
then throwing it away.

## Decision Outcome

Always store `self.mat` as a numpy array. The quaternion form is a **view** —
extracted on demand via the `.quat` property.

### Changes

- `_qmat` removed entirely
- `self.mat` is never None (for any mode)
- `mode="quaternion"` uses `_to_quaternion_block_complex` for storage
- `.quat` property extracts the Quat grid from `self.mat` on access
- Rendering checks `mode == "quaternion"` and uses `.quat` for display
- Constructing from `list[list[Quat]]` converts to complex on init
- `from_matrix` handles quaternion mode (uses quaternion-block inverse)
- All arithmetic, `.inv()`, `.trace()`, etc. work

### Consequences

- Good, because quaternion matrices now support full arithmetic
- Good, because `from_matrix(to_matrix(v, mode="quaternion"))` roundtrips
- Good, because `np.array(M)` works (returns the complex backing)
- Good, because one code path (no `if _qmat is not None` branches)
- Good, because backward compat maintained (Quat list constructor still works)
- Neutral, because `.quat` computes on every access (no caching) — fast for
  small matrices (2×2 or 4×4)
