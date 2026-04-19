---
status: accepted
date: 2026-04-19
deciders: edouard
---

# ADR-068: Recognize Known Multivectors in Rendering

## Context and Problem Statement

In physics notebooks (quantum mechanics, electromagnetism), computed results
are often numerically equal to named states or constants. For example,
`g₊(↓)` evaluates to `scalar(1.0)` which is the same as the spin-up state
`↑`. The display pipeline shows `1` but the user wants to see that this
*is* the up state.

The algebra itself doesn't know that `scalar(1.0)` means "spin up" — that's
a physics-level interpretation. Recognition belongs in the rendering layer.

## Decision

Add a `recognize=` parameter to `galaga_marimo.md()` and `Doc.md()`.

```python
knowns = [u, d]
gm.md(t"Result: {result}", recognize=knowns)
# → Result: $1 \quad (\equiv \uparrow)$
```

### Design choices

- **Per-call, not global state.** The `recognize` collection is passed
  explicitly. `Doc` accepts it at construction (applies to all `d.md()`
  calls) or per-call (overrides the constructor default).

- **Labels from the MV itself.** The annotation uses the known MV's own
  `_name_latex` (or `_name` fallback). No need to duplicate labels in a
  dict key — just pass a list of named MVs. Dicts are also accepted
  (values are iterated, keys ignored).

- **Rendering layer only.** Recognition lives in `galaga_marimo.renderer`,
  not in the algebra or Multivector. The algebra is unaware of it.

- **Numeric tolerance matching.** Uses `np.allclose(atol=1e-10)` to handle
  floating-point noise from GA arithmetic.

- **Self-match suppression.** If the rendered MV's own `_name_latex` matches
  the recognition label, no annotation is added (avoids `↑ (≡ ↑)`).

- **Unnamed knowns skipped.** If a known MV has no name, it cannot produce
  a label and is silently skipped.

- **Annotation format.** `\quad (\equiv label)` appended inside the LaTeX
  delimiters. Works for both inline `$...$` and block `$$...$$`.

- **Type safety.** Both the rendered value and the known must have a numpy
  ndarray `.data` attribute with matching shape. Non-MV values are silently
  skipped.

## Consequences

- Users can identify computed results as named states without modifying
  the algebra or the computation.
- No global state or monkey-patching — purely opt-in per render call.
- Works with any MV, not just basis vectors (eigenstates, projectors, etc.).
- Labels are raw LaTeX strings — the user controls the display format.
