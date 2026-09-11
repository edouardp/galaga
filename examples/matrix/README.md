# `galaga_matrix` examples

These notebooks introduce matrix representations as an optional integration
over the Galaga 2 facade. They use only public APIs from `galaga` and
`galaga_matrix`.

The recommended reading order is:

1. [Representations and round-trips](representations_and_roundtrips.py) —
   compact and left-regular modes, homomorphism, metadata, and general Gram
   matrices.
2. [Pauli and Dirac matrices](pauli_and_dirac.py) — named representations,
   Clifford relations, matrix operations, basis changes, and quaternion mode.
3. [Spinor columns](spinor_columns.py) — convention-dependent even-multivector
   representatives of Pauli and Dirac kets, the density/rotor/Yvon--Takabayasi
   decomposition of a regular STA spinor, bra/ket operations, basis changes,
   and faithful reconstruction.
4. [One spinor, three representations](spinors_ideals_and_chirality.py) —
   ideal elements, matrix columns, and even representatives; left versus right
   projector action; rotations and reflections; real-GA chiral projections
   with Dirac/Weyl column roundtrips and basis-independent Clifford actions,
   with interactive plots and controls.

The notebooks require Python 3.14 for Marimo t-strings. From the repository
root, open the local example gallery with:

```shell
make run-marimo
```

The launcher selects the uncommitted local packages as editable installations;
the notebook files themselves remain portable and also run against released
packages outside the checkout. They are included in the executable notebook
ledger and are run headlessly by the test suite.

When authoring interactive lessons, define controls in an upstream cell without
displaying them there. Render them in the downstream result cell's layout,
next to the matrices or plots they affect. Keep control definitions separate
from reads of their `.value`, but keep the rendered controls and results together.
