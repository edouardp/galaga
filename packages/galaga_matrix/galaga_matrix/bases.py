"""Named basis transform matrices for Dirac representations.

Provides unitary similarity transforms between the standard Dirac, Weyl
(chiral), and Majorana bases for 4×4 gamma matrices in Cl(1,3) / Cl(3,1).

All transforms are unitary: S⁻¹ = S†.
"""

from __future__ import annotations

import numpy as np

_I2 = np.eye(2, dtype=complex)
_s2 = np.array([[0, -1j], [1j, 0]], dtype=complex)  # Pauli σ₂
_Z2 = np.zeros((2, 2), dtype=complex)

# Dirac → Weyl: U = (1/√2)(I + γ⁵γ⁰) in Dirac basis
S_DIRAC_TO_WEYL = (1 / np.sqrt(2)) * np.block([[_I2, -_I2], [_I2, _I2]])

# Dirac → Majorana: self-adjoint (S = S†)
S_DIRAC_TO_MAJORANA = (1 / np.sqrt(2)) * np.block([[_I2, _s2], [_s2, -_I2]])

# All pairwise transforms (computed from the two fundamental ones)
TRANSFORMS: dict[tuple[str, str], np.ndarray] = {
    ("dirac", "weyl"): S_DIRAC_TO_WEYL,
    ("dirac", "majorana"): S_DIRAC_TO_MAJORANA,
    ("weyl", "dirac"): S_DIRAC_TO_WEYL.conj().T,
    ("majorana", "dirac"): S_DIRAC_TO_MAJORANA.conj().T,
    ("weyl", "majorana"): S_DIRAC_TO_MAJORANA @ S_DIRAC_TO_WEYL.conj().T,
    ("majorana", "weyl"): S_DIRAC_TO_WEYL @ S_DIRAC_TO_MAJORANA.conj().T,
}

DIRAC_BASES = frozenset({"dirac", "weyl", "majorana"})
PAULI_BASES = frozenset({"pauli"})
