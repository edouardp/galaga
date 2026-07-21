# `galaga_matrix` examples

These notebooks introduce matrix representations as an optional integration
over the Galaga 2 facade. They use only public APIs from `galaga.facade` and
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

The notebooks require Python 3.14 for Marimo t-strings. From the repository
root, open one with:

```shell
uv run --python 3.14 marimo edit examples/matrix/representations_and_roundtrips.py
```

They are included in the executable notebook ledger and are run headlessly by
the test suite.
