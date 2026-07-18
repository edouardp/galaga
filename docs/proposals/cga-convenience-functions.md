# Proposal: CGA Convenience Functions

## Summary

Add `up()`, `down()`, and `homo()` as free functions that embed/project points
between Euclidean space and Conformal Geometric Algebra. These work by
inspecting the multivector's algebra and blade convention metadata — no
subclassing, no special Algebra type.

## Motivation

The CGA embedding formula is simple but tedious to re-derive:

```
up(x) = x + ½|x|² e∞ + eo
down(X) = Euclidean part of X / (-e∞ · X)
```

Every CGA notebook re-implements this. Clifford's `ConformalLayout` provides
`up`/`down`/`homo` built-in, and it's one of their most-used features.

## Design

### Free functions, not methods

Since every MV carries a reference to its algebra, free functions can discover
everything they need:

```python
from galaga.cga import up, down, homo

cga = Algebra(4, 1, blades=b_cga())
e1, e2, e3, ep, em = cga.basis_vectors()

p = up(e1 + 2*e2 + 3*e3)     # CGA point
x = down(p)                    # back to Euclidean vector
p_norm = homo(p)               # normalize so -e∞ · X = 1
```

No special algebra subclass. No `cga.up()`. Just functions that inspect
`mv.algebra`.

### Discovery: how functions find eo, e∞, and the Euclidean subspace

Three options were considered:

**Option A: Metadata on BladeConvention** (recommended)

`b_cga()` knows which orthogonal e₊,e₋ vectors span the Minkowski plane
and which vectors are Euclidean. Add fields to `BladeConvention`:

```python
@dataclass
class BladeConvention:
    ...
    euclidean_dim: int | None = None
    minkowski_pair: tuple[int, int] | None = None  # (plus_index, minus_index)
```

`b_cga(euclidean=3)` sets `euclidean_dim=3` and `minkowski_pair=(3, 4)`
(0-indexed positions of e₊ and e₋ in the basis vector list).

The functions read this:

```python
def _null_pair(alg):
    bc = alg._blades_config  # or however the convention is stored
    if bc.minkowski_pair is None:
        raise TypeError("Algebra has no CGA Minkowski pair. Use blades=b_cga().")
    ep = alg.basis_vectors()[bc.minkowski_pair[0]]
    em = alg.basis_vectors()[bc.minkowski_pair[1]]
    return (em - ep) / 2, em + ep

def _euclidean_vectors(alg):
    bc = alg._blades_config
    vecs = alg.basis_vectors()
    return [vecs[i] for i in range(bc.euclidean_dim)]
```

Pros: explicit, no guessing, works with any naming convention.
Cons: requires `b_cga()` — won't work on a bare `Algebra(4,1)`.

**Option B: Detect from metric**

Find an orthogonal +1/-1 pair from the metric, then derive eₒ and e∞. The
Euclidean vectors are the rest.

Pros: works without `b_cga()`.
Cons: ambiguous whenever the algebra contains multiple positive or negative
directions and no metadata identifies the CGA Minkowski plane.

**Option C: Detect from blade names**

Look for blades named `ep`/`em` in the convention and derive the null pair.

Pros: simple.
Cons: breaks if the user chose different names.

### Recommendation: Option A with Option B fallback

```python
def _null_pair(alg):
    # Try metadata first
    if hasattr(alg, '_cga_minkowski_pair') and alg._cga_minkowski_pair is not None:
        i, j = alg._cga_minkowski_pair
        vecs = alg.basis_vectors()
        ep, em = vecs[i], vecs[j]
        return (em - ep) / 2, em + ep
    # Fallback: detect from metric
    return _detect_null_pair(alg)
```

This gives the best of both worlds: fast and explicit when `b_cga()` is used,
still works (with a warning?) for manually constructed CGA algebras.

## Functions

### `up(x) → Multivector`

Embed a Euclidean vector into CGA.

```python
def up(x):
    alg = x.algebra
    eo, ei = _null_pair(alg)
    x_sq = float(gp(x, x))
    return x + 0.5 * x_sq * ei + eo
```

Also accept raw coordinates:

```python
def up(*coords, algebra):
    """up(1, 2, 3, algebra=cga) — embed from coordinates."""
```

### `down(X) → Multivector`

Project a CGA null vector back to a Euclidean vector.

```python
def down(X):
    alg = X.algebra
    eo, ei = _null_pair(alg)
    euclidean = _euclidean_vectors(alg)
    scale = -float(left_contraction(ei, X))
    X_norm = X / scale
    return sum(float(left_contraction(e, X_norm)) * e for e in euclidean)
```

### `homo(X) → Multivector`

Normalize a CGA point so that `-e∞ · X = 1`.

```python
def homo(X):
    alg = X.algebra
    _, ei = _null_pair(alg)
    scale = -float(left_contraction(ei, X))
    return X / scale
```

## Geometric primitives (future)

Once `up` exists, higher-level constructors are straightforward:

```python
def sphere(center, radius, algebra):
    """Dual sphere: S = up(center) - ½r² e∞"""
    c = up(center) if not isinstance(center, Multivector) else center
    _, ei = _null_pair(algebra)
    return c - 0.5 * radius**2 * ei

def plane(normal, offset, algebra):
    """Dual plane: π = n + d·e∞"""
    _, ei = _null_pair(algebra)
    euclidean = _euclidean_vectors(algebra)
    n = sum(c * e for c, e in zip(normal, euclidean))
    return n + offset * ei

def circle(p1, p2, p3):
    """Circle through three points: C = p1 ∧ p2 ∧ p3"""
    return op(op(p1, p2), p3)

def line(p1, p2):
    """Line through two points: L = p1 ∧ p2 ∧ e∞"""
    _, ei = _null_pair(p1.algebra)
    return op(op(p1, p2), ei)

def point_pair(p1, p2):
    """Point pair: P = p1 ∧ p2"""
    return op(p1, p2)
```

## Where it lives

Option A: `galaga.cga` module inside the main galaga package. CGA is
fundamental enough to GA that it belongs in core, not a separate package.

Option B: `galaga_cga` package, like `galaga_matrix`. Keeps core small.

Recommendation: **Option A** (`galaga.cga`). The functions are small, have no
extra dependencies, and CGA is one of the primary use cases for GA libraries.

## Changes required

1. Add `euclidean_dim` and `minkowski_pair` fields to `BladeConvention`
2. Have `b_cga()` populate them
3. Store them on `Algebra` (or read from the stored `BladeConvention`)
4. Implement `up`, `down`, `homo` in `galaga/cga.py`
5. Add geometric primitive constructors
6. Tests against known CGA identities (roundtrip, sphere/plane duality, etc.)
7. Example notebook
