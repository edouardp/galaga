---
status: accepted
date: 2026-04-26
deciders: edouard
---

# ADR-004: MatrixRepr as Rendering Wrapper with Algebra Back-Reference

> Superseded in part by
> [ADR-010](010-replace-labels-with-names.md): MatrixRepr's `.label`
> mechanism is replaced by `.name()`. The wrapper, rendering, algebra
> back-reference, and numpy-proxy decisions remain accepted.

## Context and Problem Statement

Matrix representations need to be displayed in notebooks (marimo t-strings,
Jupyter) and converted back to multivectors. The raw `to_matrix` returns a
numpy array, which has no LaTeX rendering and no way to recover the source
algebra.

Options considered:

1. **Return MatrixRepr from to_matrix**: change `to_matrix` to return a
   `MatrixRepr` instead of a raw array. Breaks the simple contract and
   couples the conversion logic to the rendering logic.

2. **Separate wrapper**: keep `to_matrix` returning `np.ndarray`, provide
   `MatrixRepr` as an opt-in wrapper that adds rendering and back-conversion.

## Decision Outcome

Separate wrapper (option 2). `MatrixRepr` is a thin wrapper with:

- `.mat` — the underlying numpy array
- `.name()` — symbolic name for display and expression trees
- `.algebra` — optional back-reference to the source `Algebra`
- `.mode` — the representation mode (`"left-regular"` or `"compact"`)
- `.latex()` / `._repr_latex_()` — LaTeX rendering (galaga_marimo compatible)
- `.__array__()` — NumPy protocol so `np.array(mr)`, `np.trace(mr)` etc. work
- `.mv` — property that calls `from_matrix` using the stored algebra and mode

The algebra and mode are optional — `MatrixRepr` works as a pure rendering
wrapper without them. The `.mv` property raises `ValueError` if no algebra
was provided.

### Consequences

- Good, because `to_matrix` stays simple — returns a plain numpy array
- Good, because `MatrixRepr` is opt-in — users who just want the array
  don't pay for the wrapper
- Good, because `.mv` enables `to_matrix(e1, mode="compact").mv` roundtrip
  without monkey-patching `Multivector`
- Good, because `__array__` makes `MatrixRepr` a drop-in for numpy functions
- Neutral: the algebra back-reference creates a reference cycle
  (MV → Algebra, MatrixRepr → Algebra) but this is harmless in CPython
  with cycle-aware GC
