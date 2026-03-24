"""Core algebra and multivector types."""

from __future__ import annotations

import numpy as np
from functools import cached_property


def _sign_of_reorder(a: int, b: int) -> int:
    """Compute sign from sorting the concatenation of two basis blade bitmasks."""
    n = 0
    a = a >> 1
    while a:
        n += bin(a & b).count("1")
        a = a >> 1
    return 1 - 2 * (n & 1)


_LETTER_SUBSCRIPTS = {"x": "ₓ", "y": "ᵧ"}


class Algebra:
    """Immutable Clifford algebra defined by a metric signature.

    Args:
        signature: Tuple of +1, -1, or 0 for each basis vector's square.
    """

    __slots__ = ("_sig", "_dim", "_n", "_mul_index", "_mul_sign", "_grade_masks", "_names")

    # Built-in naming presets: (code_names, unicode_names)
    # code_names are used in repr, unicode_names in str
    PRESETS = {
        "e": None,  # default: e1, e2, ... / e₁, e₂, ...
        "gamma": lambda n: ([f"g{i}" for i in range(n)],
                            [f"γ{str(i).translate(str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉'))}" for i in range(n)]),
        "sigma": lambda n: ([f"s{i+1}" for i in range(n)],
                            [f"σ{str(i+1).translate(str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉'))}" for i in range(n)]),
        "sigma_xyz": lambda n: (
            [c for c in "xyzwvu"[:n]],
            [f"σ{_LETTER_SUBSCRIPTS.get(c, c)}" for c in "xyzwvu"[:n]],
        ),
    }

    def __init__(self, signature: tuple[int, ...], names: str | tuple[list[str], list[str]] | None = None):
        self._sig = tuple(signature)
        self._n = len(signature)
        self._dim = 1 << self._n

        # Resolve naming scheme
        if names is None or names == "e":
            self._names = None  # default e1/e₁ scheme
        elif isinstance(names, str):
            preset = self.PRESETS.get(names)
            if preset is None:
                raise ValueError(f"Unknown naming preset: {names!r}")
            self._names = preset(self._n)
        else:
            code, uni = names
            if len(code) != self._n or len(uni) != self._n:
                raise ValueError(f"Names must have {self._n} entries, got {len(code)}/{len(uni)}")
            self._names = (list(code), list(uni))

        # Precompute multiplication tables
        mul_index = np.empty((self._dim, self._dim), dtype=np.intp)
        mul_sign = np.zeros((self._dim, self._dim), dtype=np.float64)

        for i in range(self._dim):
            for j in range(self._dim):
                result, sign = self._blade_product(i, j)
                mul_index[i, j] = result
                mul_sign[i, j] = sign

        self._mul_index = mul_index
        self._mul_sign = mul_sign

        # Precompute grade masks
        self._grade_masks = {}
        for k in range(self._n + 1):
            self._grade_masks[k] = np.array(
                [bin(i).count("1") == k for i in range(self._dim)], dtype=bool
            )

    def _blade_product(self, a: int, b: int) -> tuple[int, float]:
        """Compute geometric product of two basis blades (bitmask indices)."""
        sign = _sign_of_reorder(a, b)
        result = a ^ b
        # Apply metric: for each shared basis vector, multiply by its signature
        shared = a & b
        metric = 1.0
        for k in range(self._n):
            if shared & (1 << k):
                metric *= self._sig[k]
        if metric == 0:
            return 0, 0.0
        return result, sign * metric

    @property
    def signature(self) -> tuple[int, ...]:
        return self._sig

    @property
    def n(self) -> int:
        return self._n

    @property
    def dim(self) -> int:
        return self._dim

    def basis_vectors(self) -> tuple[Multivector, ...]:
        """Return the n basis 1-vectors."""
        vecs = []
        for k in range(self._n):
            data = np.zeros(self._dim)
            data[1 << k] = 1.0
            vecs.append(Multivector(self, data))
        return tuple(vecs)

    def pseudoscalar(self) -> Multivector:
        """Return the unit pseudoscalar I (𝑰)."""
        data = np.zeros(self._dim)
        data[self._dim - 1] = 1.0
        return Multivector(self, data)

    @property
    def I(self) -> Multivector:
        """Unit pseudoscalar."""
        return self.pseudoscalar()

    @property
    def identity(self) -> Multivector:
        """Scalar identity 𝟙."""
        return self.scalar(1.0)

    def scalar(self, value: float) -> Multivector:
        data = np.zeros(self._dim)
        data[0] = value
        return Multivector(self, data)

    def vector(self, coeffs) -> Multivector:
        """Create a 1-vector from coefficients."""
        data = np.zeros(self._dim)
        for k, c in enumerate(coeffs):
            data[1 << k] = c
        return Multivector(self, data)

    def blade(self, name: str) -> Multivector:
        """Lookup a basis blade by name, e.g. 'e1', 'e12', 'e123', or custom names."""
        if name == "1" or name == "":
            return self.scalar(1.0)
        # Try custom code names first
        if self._names is not None:
            code_names = self._names[0]
            # Try to parse as concatenation of code names (greedy, longest first)
            bitmask = self._parse_blade_name(name, code_names)
            if bitmask is not None:
                data = np.zeros(self._dim)
                data[bitmask] = 1.0
                return Multivector(self, data)
        # Default e-index parsing
        if not name.startswith("e"):
            raise ValueError(f"Invalid blade name: {name!r}")
        indices = [int(ch) for ch in name[1:]]
        bitmask = 0
        for idx in indices:
            if idx < 1 or idx > self._n:
                raise ValueError(f"Basis index {idx} out of range for {self._n}D algebra")
            bitmask |= 1 << (idx - 1)
        data = np.zeros(self._dim)
        data[bitmask] = 1.0
        return Multivector(self, data)

    def _parse_blade_name(self, name: str, code_names: list[str]) -> int | None:
        """Try to parse a blade name as concatenation of code names. Returns bitmask or None."""
        bitmask = 0
        remaining = name
        while remaining:
            matched = False
            # Try longest names first to avoid ambiguity
            for k in sorted(range(self._n), key=lambda k: -len(code_names[k])):
                if remaining.startswith(code_names[k]):
                    bitmask |= 1 << k
                    remaining = remaining[len(code_names[k]):]
                    matched = True
                    break
            if not matched:
                return None
        return bitmask

    def rotor_from_plane_angle(self, B: Multivector, theta: float) -> Multivector:
        """Create a rotor R = cos(θ/2) - sin(θ/2)B for rotation by θ in plane B.

        B should be a unit bivector.
        """
        return self.scalar(np.cos(theta / 2)) - np.sin(theta / 2) * B

    _SUBSCRIPTS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

    def _blade_name(self, index: int, unicode: bool = False) -> str:
        if index == 0:
            return ""
        # Pseudoscalar gets special name
        if index == self._dim - 1:
            return "𝑰" if unicode else "I"
        if self._names is None:
            # Default e1, e₁ scheme
            digits = "".join(str(k + 1) for k in range(self._n) if index & (1 << k))
            if unicode:
                return "e" + digits.translate(self._SUBSCRIPTS)
            return "e" + digits
        # Custom names: concatenate per-vector names for the blade
        src = self._names[1] if unicode else self._names[0]
        parts = [src[k] for k in range(self._n) if index & (1 << k)]
        return "".join(parts)

    def __repr__(self) -> str:
        pos = self._sig.count(1)
        neg = self._sig.count(-1)
        zero = self._sig.count(0)
        parts = [str(pos), str(neg)]
        if zero:
            parts.append(str(zero))
        return f"Cl({','.join(parts)})"


class Multivector:
    """A multivector in a Clifford algebra. Lightweight: just algebra ref + dense data."""

    __slots__ = ("algebra", "data")

    def __init__(self, algebra: Algebra, data: np.ndarray):
        self.algebra = algebra
        self.data = np.array(data, dtype=np.float64)

    def _check_same(self, other: Multivector):
        if self.algebra is not other.algebra:
            raise ValueError(
                f"Cannot operate on multivectors from different algebras: "
                f"{self.algebra} vs {other.algebra}"
            )

    # --- Operator overloads ---

    def __add__(self, other):
        if isinstance(other, (int, float)):
            d = self.data.copy()
            d[0] += other
            return Multivector(self.algebra, d)
        self._check_same(other)
        return Multivector(self.algebra, self.data + other.data)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            d = self.data.copy()
            d[0] -= other
            return Multivector(self.algebra, d)
        self._check_same(other)
        return Multivector(self.algebra, self.data - other.data)

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            d = -self.data.copy()
            d[0] += other
            return Multivector(self.algebra, d)
        return NotImplemented

    def __neg__(self):
        return Multivector(self.algebra, -self.data)

    def __mul__(self, other):
        """Geometric product (a * b) or scalar multiplication."""
        if isinstance(other, (int, float)):
            return Multivector(self.algebra, self.data * other)
        self._check_same(other)
        return gp(self, other)

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return Multivector(self.algebra, self.data * other)
        return NotImplemented

    def __xor__(self, other):
        """Outer product (a ^ b)."""
        return op(self, other)

    def __or__(self, other):
        """Left contraction (a | b)."""
        return left_contraction(self, other)

    def __invert__(self):
        """Reverse (~a)."""
        return reverse(self)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Multivector(self.algebra, self.data / other)
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, Multivector):
            self._check_same(other)
            return np.allclose(self.data, other.data)
        if isinstance(other, (int, float)):
            expected = np.zeros(self.algebra.dim)
            expected[0] = other
            return np.allclose(self.data, expected)
        return NotImplemented

    def __getitem__(self, k: int) -> Multivector:
        """Grade projection: x[k] returns grade-k component."""
        return grade(self, k)

    # --- Convenience properties/methods ---

    @property
    def inv(self) -> Multivector:
        """Inverse: x⁻¹"""
        return inverse(self)

    @property
    def dag(self) -> Multivector:
        """Reverse (dagger): x†"""
        return reverse(self)

    @property
    def sq(self) -> Multivector:
        """Squared: x²"""
        return gp(self, self)

    @property
    def scalar_part(self) -> float:
        """Extract grade-0 coefficient as a float."""
        return float(self.data[0])

    @property
    def vector_part(self) -> np.ndarray:
        """Extract grade-1 coefficients as a numpy array."""
        n = self.algebra._n
        return np.array([self.data[1 << i] for i in range(n)])

    def _format(self, unicode: bool = False) -> str:
        alg = self.algebra
        terms = []
        for i in range(alg.dim):
            c = self.data[i]
            if abs(c) < 1e-12:
                continue
            name = alg._blade_name(i, unicode=unicode)
            if name == "":
                terms.append(f"{c:g}")
            elif abs(c) == 1.0:
                terms.append(f"{name}" if c > 0 else f"-{name}")
            else:
                terms.append(f"{c:g}{name}")
        if not terms:
            return "0"
        result = terms[0]
        for t in terms[1:]:
            if t.startswith("-"):
                result += " - " + t[1:]
            else:
                result += " + " + t
        return result

    def __repr__(self) -> str:
        return self._format(unicode=False)

    def __str__(self) -> str:
        return self._format(unicode=True)


# ============================================================
# Phase 3: Core named operations
# ============================================================


def gp(a: Multivector, b: Multivector) -> Multivector:
    """Geometric product."""
    a._check_same(b)
    alg = a.algebra
    out = np.zeros(alg.dim)
    # Vectorized: for each nonzero coeff in a, accumulate contributions
    for i in np.nonzero(a.data)[0]:
        ai = a.data[i]
        indices = alg._mul_index[i]
        signs = alg._mul_sign[i]
        out[indices] += ai * b.data * signs
    return Multivector(alg, out)


def op(a: Multivector, b: Multivector) -> Multivector:
    """Outer (wedge) product."""
    a._check_same(b)
    alg = a.algebra
    out = np.zeros(alg.dim)
    for i in np.nonzero(a.data)[0]:
        gi = bin(i).count("1")
        ai = a.data[i]
        for j in np.nonzero(b.data)[0]:
            gj = bin(j).count("1")
            target_grade = gi + gj
            k = alg._mul_index[i, j]
            if bin(k).count("1") == target_grade:
                out[k] += ai * b.data[j] * alg._mul_sign[i, j]
    return Multivector(alg, out)


def left_contraction(a: Multivector, b: Multivector) -> Multivector:
    """Left contraction: a ⌋ b. Grade of result = grade(b) - grade(a)."""
    a._check_same(b)
    alg = a.algebra
    out = np.zeros(alg.dim)
    for i in np.nonzero(a.data)[0]:
        gi = bin(i).count("1")
        ai = a.data[i]
        for j in np.nonzero(b.data)[0]:
            gj = bin(j).count("1")
            target_grade = gj - gi
            if target_grade < 0:
                continue
            k = alg._mul_index[i, j]
            if bin(k).count("1") == target_grade:
                out[k] += ai * b.data[j] * alg._mul_sign[i, j]
    return Multivector(alg, out)


def right_contraction(a: Multivector, b: Multivector) -> Multivector:
    """Right contraction: a ⌊ b. Grade of result = grade(a) - grade(b)."""
    a._check_same(b)
    alg = a.algebra
    out = np.zeros(alg.dim)
    for i in np.nonzero(a.data)[0]:
        gi = bin(i).count("1")
        ai = a.data[i]
        for j in np.nonzero(b.data)[0]:
            gj = bin(j).count("1")
            target_grade = gi - gj
            if target_grade < 0:
                continue
            k = alg._mul_index[i, j]
            if bin(k).count("1") == target_grade:
                out[k] += ai * b.data[j] * alg._mul_sign[i, j]
    return Multivector(alg, out)


def hestenes_inner(a: Multivector, b: Multivector) -> Multivector:
    """Hestenes inner product: like left contraction but zero if either is scalar."""
    a._check_same(b)
    alg = a.algebra
    out = np.zeros(alg.dim)
    for i in np.nonzero(a.data)[0]:
        gi = bin(i).count("1")
        if gi == 0:
            continue
        ai = a.data[i]
        for j in np.nonzero(b.data)[0]:
            gj = bin(j).count("1")
            if gj == 0:
                continue
            target_grade = abs(gi - gj)
            k = alg._mul_index[i, j]
            if bin(k).count("1") == target_grade:
                out[k] += ai * b.data[j] * alg._mul_sign[i, j]
    return Multivector(alg, out)


def scalar_product(a: Multivector, b: Multivector) -> Multivector:
    """Scalar product: grade-0 part of the geometric product."""
    return grade(gp(a, b), 0)


def commutator(a: Multivector, b: Multivector) -> Multivector:
    """Commutator product: (ab - ba) / 2."""
    return (gp(a, b) - gp(b, a)) * 0.5


def anticommutator(a: Multivector, b: Multivector) -> Multivector:
    """Anticommutator product: (ab + ba) / 2."""
    return (gp(a, b) + gp(b, a)) * 0.5


# --- Unary operations ---


def reverse(x: Multivector) -> Multivector:
    """Reverse: reverses the order of basis vectors in each blade.
    Grade-k component is multiplied by (-1)^(k(k-1)/2).
    """
    alg = x.algebra
    out = x.data.copy()
    for k in range(alg.n + 1):
        sign = (-1) ** (k * (k - 1) // 2)
        if sign == -1:
            out[alg._grade_masks[k]] *= -1
    return Multivector(alg, out)


def involute(x: Multivector) -> Multivector:
    """Grade involution: grade-k component is multiplied by (-1)^k."""
    alg = x.algebra
    out = x.data.copy()
    for k in range(alg.n + 1):
        if k % 2 == 1:
            out[alg._grade_masks[k]] *= -1
    return Multivector(alg, out)


def conjugate(x: Multivector) -> Multivector:
    """Clifford conjugate: reverse composed with involute."""
    return involute(reverse(x))


def grade(x: Multivector, k: int | str) -> Multivector:
    """Extract grade-k component, or 'even'/'odd' for parity selection."""
    if k == "even":
        return even_grades(x)
    if k == "odd":
        return odd_grades(x)
    alg = x.algebra
    if k < 0 or k > alg.n:
        return Multivector(alg, np.zeros(alg.dim))
    out = np.zeros(alg.dim)
    mask = alg._grade_masks[k]
    out[mask] = x.data[mask]
    return Multivector(alg, out)


def grades(x: Multivector, ks: list[int]) -> Multivector:
    """Extract multiple grade components."""
    alg = x.algebra
    out = np.zeros(alg.dim)
    for k in ks:
        if 0 <= k <= alg.n:
            mask = alg._grade_masks[k]
            out[mask] = x.data[mask]
    return Multivector(alg, out)


def scalar(x: Multivector) -> float:
    """Extract the scalar (grade-0) coefficient."""
    return float(x.data[0])


def dual(x: Multivector) -> Multivector:
    """Dual: left contraction with the inverse pseudoscalar."""
    I_inv = inverse(x.algebra.pseudoscalar())
    return left_contraction(x, I_inv)


def undual(x: Multivector) -> Multivector:
    """Undual: left contraction with the pseudoscalar."""
    I = x.algebra.pseudoscalar()
    return left_contraction(x, I)


def norm2(x: Multivector) -> float:
    """Squared norm: scalar part of x * ~x."""
    return scalar(gp(x, reverse(x)))


def norm(x: Multivector) -> float:
    """Norm: sqrt(|norm2(x)|)."""
    return float(np.sqrt(abs(norm2(x))))


def unit(x: Multivector) -> Multivector:
    """Normalize to unit multivector."""
    n = norm(x)
    if n < 1e-15:
        raise ValueError("Cannot normalize near-zero multivector")
    return x / n


def inverse(x: Multivector) -> Multivector:
    """Inverse via x_rev / (x * x_rev) for versors."""
    x_rev = reverse(x)
    denom = scalar(gp(x, x_rev))
    if abs(denom) < 1e-15:
        raise ValueError("Multivector is not invertible")
    return x_rev / denom


# --- Predicates ---


def is_scalar(x: Multivector) -> bool:
    return np.allclose(x.data[1:], 0)


def is_vector(x: Multivector) -> bool:
    return x == grade(x, 1)


def is_bivector(x: Multivector) -> bool:
    return x == grade(x, 2)


def is_even(x: Multivector) -> bool:
    alg = x.algebra
    for k in range(alg.n + 1):
        if k % 2 == 1 and np.any(np.abs(x.data[alg._grade_masks[k]]) > 1e-12):
            return False
    return True


def is_rotor(x: Multivector) -> bool:
    """True if x is a rotor: even-graded and x * ~x ≈ 1."""
    return is_even(x) and np.isclose(scalar(gp(x, reverse(x))), 1.0)


def even_grades(x: Multivector) -> Multivector:
    """Extract even-grade components."""
    alg = x.algebra
    return grades(x, [k for k in range(0, alg.n + 1, 2)])


def odd_grades(x: Multivector) -> Multivector:
    """Extract odd-grade components."""
    alg = x.algebra
    return grades(x, [k for k in range(1, alg.n + 1, 2)])


def squared(x: Multivector) -> Multivector:
    """Geometric product of x with itself: x²."""
    return gp(x, x)


def sandwich(r: Multivector, x: Multivector) -> Multivector:
    """Sandwich product: r x r̃."""
    return gp(gp(r, x), reverse(r))


sw = sandwich


# --- Aliases ---

geometric_product = gp
wedge = op
outer_product = op
rev = reverse
normalize = unit
normalise = unit
norm_squared = norm2
even = even_grades
odd = odd_grades


def ip(a: Multivector, b: Multivector, mode: str = "hestenes") -> Multivector:
    """Unified inner product dispatcher.

    Modes:
        "hestenes" — Hestenes inner product (default)
        "left"     — left contraction (a ⌋ b)
        "right"    — right contraction (a ⌊ b)
        "scalar"   — scalar product (grade-0 of gp)
    """
    match mode:
        case "hestenes":
            return hestenes_inner(a, b)
        case "left":
            return left_contraction(a, b)
        case "right":
            return right_contraction(a, b)
        case "scalar":
            return scalar_product(a, b)
        case _:
            raise ValueError(
                f"Unknown inner product mode: {mode!r}. "
                f"Use 'hestenes', 'left', 'right', or 'scalar'."
            )


inner_product = ip
