# SPEC: Unified Quaternion Mode Storage

## Status

Accepted — implemented.

## Problem

`mode="quaternion"` currently stores data as `_qmat` (a `list[list[Quat]]`)
with `mat = None`. This creates a separate code path: arithmetic operations
raise `TypeError`, basis changes don't work, `from_matrix` can't roundtrip,
and the rendering code has two branches.

Meanwhile, the quaternion-block representation IS a 4×4 complex matrix
internally (each quaternion is embedded as a 2×2 complex block). We already
compute this via `_to_quaternion_block_complex`. We just throw it away and
store only the extracted `Quat` grid.

## Rules

### Rule 1: Always store `self.mat` as a numpy array

`mode="quaternion"` stores the 4×4 (or 2×2 for Cl(0,2)) complex matrix
from the quaternion-block basis in `self.mat`. Never `None`.

### Rule 2: Remove `_qmat` as a storage path

The `_qmat` attribute is removed from `MatrixRepr.__init__`. No constructor
path sets `mat = None`.

### Rule 3: `.quat` property extracts Quat grid on demand

```python
@property
def quat(self) -> list[list[Quat]]:
    """Read the matrix as a quaternion grid (k×k Quat entries).

    Each 2×2 complex block is interpreted as a quaternion.
    Only meaningful when mode='quaternion'.
    """
```

Raises `TypeError` if `mode != "quaternion"` or matrix dimensions are odd.

### Rule 4: Rendering checks mode

The `_body_latex()` and `__repr__` methods check `self.mode == "quaternion"`
and render using the `.quat` property (extracting Quat entries from `self.mat`).

No separate rendering code for `_qmat` — one path through `.quat`.

### Rule 5: Arithmetic works

Since `self.mat` is always a numpy array, all existing arithmetic operations
(matmul, add, inv, etc.) work for quaternion-mode matrices. The result
inherits `mode="quaternion"`.

### Rule 6: `to_matrix(mv, mode="quaternion")` uses quaternion-block basis

Calls `_to_quaternion_block_complex(mv)` and stores the result in `self.mat`.
Sets `mode="quaternion"`. No `_qmat` construction.

### Rule 7: `from_matrix` handles quaternion mode

When `MatrixRepr.mode == "quaternion"`, `from_matrix` uses the quaternion-block
blade matrices for the inverse (via `_build_quaternion_block_blade_matrices`).
Single-argument form works: `from_matrix(M)` where `M.mode == "quaternion"`.

### Rule 8: Construction from list-of-lists of Quat (backward compat)

`MatrixRepr([[Quat(1), Quat(0)], [Quat(0), Quat(-1)]])` still works.
The constructor converts the Quat grid to a complex matrix (via the 2×2
block embedding) and stores it in `self.mat`. Sets `mode="quaternion"`.

### Rule 9: `to_basis` not supported for quaternion mode (initially)

`to_basis("weyl")` on a quaternion-mode matrix raises `TypeError`.
The quaternion-block basis is its own thing — changing to Weyl would
require defining what "Weyl" means in the quaternion-block context.
Future work could add quaternion-to-complex basis conversion.

## Examples

```python
sta = Algebra(1, 3)
g0, g1 = sta.basis_vectors()[:2]

# Create in quaternion mode
M = to_matrix(g0, mode="quaternion")
M.mat           # 4×4 complex numpy array (always present)
M.quat          # [[Quat(1,0,0,0), Quat(0,0,0,0)],
                #  [Quat(0,0,0,0), Quat(-1,0,0,0)]]
M.mode          # "quaternion"

# Arithmetic works
M2 = M @ M      # identity (γ₀² = +I)
M2.mode         # "quaternion"
M2.quat         # [[Quat(1), Quat(0)], [Quat(0), Quat(1)]]

# Inverse works
M_inv = M.inv()
M_inv.quat      # same as M.quat (γ₀ is its own inverse)

# Trace works
M.trace()       # 0 (traceless)

# Roundtrip
from_matrix(M)  # recovers g0

# Product of gamma matrices
M01 = to_matrix(g0 * g1, mode="quaternion")
M01.quat        # quaternion representation of γ₀γ₁

# Backward compat: construct from Quat list
from galaga_matrix.matrix import Quat
M_manual = MatrixRepr([[Quat(1, 0, 0, 0), Quat(0, 1, 0, 0)],
                       [Quat(0, 1, 0, 0), Quat(-1, 0, 0, 0)]])
M_manual.mat    # 4×4 complex (converted from Quat grid)
M_manual.mode   # "quaternion"
```

## Edge Cases

- `MatrixRepr(np.eye(4), mode="quaternion")` — allowed, `.quat` reads the
  blocks. Identity reads as `[[Quat(1), Quat(0)], [Quat(0), Quat(1)]]`.
- `.quat` on a matrix with odd dimensions — raises `TypeError`.
- `.quat` on `mode != "quaternion"` — raises `TypeError` (could relax later,
  but for now keeps semantics clear).
- `to_basis("weyl")` on quaternion mode — raises `TypeError`.

## Impact

- Removed: `self._qmat` attribute, all `if self._qmat is not None` branches.
- Modified: `__init__` — Quat list input converts to complex matrix.
- Added: `.quat` property.
- Modified: `_body_latex()`, `__repr__` — use `.quat` instead of `_qmat`.
- Modified: `_require_mat()` — no longer needed to guard against None.
- Modified: `__array__` — no longer raises for quaternion mode (returns complex backing).
- Modified: `from_matrix` — dispatches to quaternion-block inverse when mode is quaternion.
- Tests: quaternion arithmetic, roundtrip, rendering, backward compat construction.
