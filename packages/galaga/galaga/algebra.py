"""Core algebra and multivector types.

This module is the numeric engine of the ``ga`` library. It contains:

1. ``Algebra`` — An immutable Clifford algebra factory, parameterised by a
   metric signature. On construction it precomputes the full multiplication
   table (sign and index arrays), so that all subsequent products are
   table lookups, not recomputation.

2. ``Multivector`` — A lightweight value type: just an ``Algebra`` reference
   and a dense NumPy array of ``2^n`` coefficients (one per basis blade).
   Operator overloads (``*``, ``^``, ``|``, ``~``) delegate to the named
   functions below.

3. Named operations — Every GA product and transformation is a module-level
   function (``gp``, ``op``, ``left_contraction``, ``grade``, ``reverse``,
   etc.). These are the stable public API; operators are convenience sugar.

Representation choices
----------------------
- **Basis blades as bitmasks.** A blade like e₁₃ is the integer ``0b101``
  (bits 0 and 2 set). This makes the geometric product a XOR of bitmasks
  (for the resulting blade) plus a sign computation (for reordering).

- **Dense coefficient arrays.** A multivector in Cl(n) stores ``2^n`` floats,
  one per blade, regardless of sparsity. This is simple and fast for small n
  (≤8 or so). The index into the array *is* the bitmask.

- **Precomputed multiplication tables.** ``_mul_index[i,j]`` gives the
  result bitmask and ``_mul_sign[i,j]`` gives the sign+metric factor for
  the product of basis blades i and j. This turns the geometric product
  into a sparse scatter-add over nonzero coefficients.

- **Precomputed grade masks.** ``_grade_masks[k]`` is a boolean array that
  selects all blade indices of grade k. Grade projection is a single
  masked copy.
"""

from __future__ import annotations

import numpy as np


def _sign_of_reorder(a: int, b: int) -> int:
    """Compute the sign incurred by concatenating two basis blade bitmasks.

    When we multiply basis blades e_A and e_B, the result blade is e_{A^B}
    but we need to count how many transpositions are required to move the
    basis vectors of B past those of A into canonical (sorted) order.

    Algorithm: for each bit in A (from high to low), count how many bits
    in B are *below* it. Each such pair is one transposition → one sign flip.
    The total parity (even/odd) gives the sign: +1 or -1.

    This is the standard "canonical reordering sign" from Clifford algebra
    implementations. It runs in O(n²) where n is the number of basis vectors,
    which is fine for n ≤ 16.
    """
    n = 0
    a = a >> 1
    while a:
        n += bin(a & b).count("1")
        a = a >> 1
    return 1 - 2 * (n & 1)


_LETTER_SUBSCRIPTS = {"x": "ₓ", "y": "ᵧ"}


import galaga.expr as _sym
import galaga.render as _render
from galaga.basis_blade import BasisBlade
from galaga.latex_symbols import LatexSymbols
from galaga.lazy import lazy_binary, lazy_unary
from galaga.notation import Notation


class Algebra:
    """Immutable Clifford algebra Cl(p,q,r) defined by a metric signature.

    The signature tuple defines each basis vector's square:
    - ``+1`` for positive-definite (Euclidean) directions
    - ``-1`` for negative-definite (e.g. timelike in STA)
    - ``0``  for degenerate/null directions (e.g. projective GA)

    On construction, the algebra precomputes:
    - ``_mul_index[i,j]``: the bitmask of the result blade for basis blades i*j
    - ``_mul_sign[i,j]``:  the scalar factor (reordering sign × metric) for i*j
    - ``_grade_masks[k]``: boolean mask selecting all grade-k blade indices

    These tables make all subsequent products O(s) where s is the number of
    nonzero coefficients, with no per-product sign/metric computation.

    Args:
        signature: Tuple of +1, -1, or 0 for each basis vector's square.
                   Length n defines the algebra dimension 2^n.
        names: Display naming scheme. Can be:
               - None or "e": default e₁, e₂, ... notation
               - "gamma": γ₀, γ₁, ... (for spacetime algebra)
               - "sigma": σ₁, σ₂, ... (for Pauli algebra)
               - "sigma_xyz": σₓ, σᵧ, σz
               - (code_names, unicode_names): custom per-vector names
        repr_unicode: If True, ``repr()`` uses Unicode (same as ``str()``).
                      If False (default), ``repr()`` uses ASCII for copy-paste.
    """

    __slots__ = (
        "_sig",
        "_dim",
        "_n",
        "_mul_index",
        "_mul_sign",
        "_grade_masks",
        "_names",
        "_latex_names",
        "_repr_unicode",
        "_complement_sign",
        "_blades",
        "_notation",
    )

    # Built-in naming presets: (code_names, unicode_names, latex_names)
    # code_names  → used in repr() (ASCII-safe)
    # unicode_names → used in str() (pretty terminal output)
    # latex_names → used in .latex() (notebook rendering)
    PRESETS = {
        "e": None,  # default: e1, e2, ... / e₁, e₂, ...
        "gamma": lambda n: (
            [f"g{i}" for i in range(n)],
            [f"γ{str(i).translate(str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉'))}" for i in range(n)],
            [f"\\gamma_{i}" for i in range(n)],
        ),
        "sigma": lambda n: (
            [f"s{i + 1}" for i in range(n)],
            [f"σ{str(i + 1).translate(str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉'))}" for i in range(n)],
            [f"\\sigma_{i + 1}" for i in range(n)],
        ),
        "sigma_xyz": lambda n: (
            [c for c in "xyzwvu"[:n]],
            [f"σ{_LETTER_SUBSCRIPTS.get(c, c)}" for c in "xyzwvu"[:n]],
            [f"\\sigma_{c}" for c in "xyzwvu"[:n]],
        ),
    }

    def __init__(
        self,
        signature: tuple[int, ...],
        names: str | tuple[list[str], list[str]] | None = None,
        repr_unicode: bool = False,
        notation: Notation | None = None,
    ):
        self._notation = notation or Notation()
        """Create a Clifford algebra from a metric signature.

        Args:
            signature: Tuple of +1, -1, or 0 for each basis vector's square.
                ``(1,1,1)`` → Cl(3,0), ``(1,-1,-1,-1)`` → Cl(1,3), ``(1,1,1,0)`` → PGA.
            names: Basis vector naming scheme. ``None`` or ``"e"`` for default
                (e1, e2, …). Presets: ``"gamma"``, ``"sigma"``, ``"sigma_xyz"``.
                Or a ``(code_names, unicode_names)`` tuple for custom names.
            repr_unicode: If True, ``repr()`` on multivectors uses Unicode
                (matching ``str()``). Useful in IPython/REPL.
        """
        self._sig = tuple(signature)
        self._n = len(signature)
        self._dim = 1 << self._n
        self._repr_unicode = repr_unicode

        # Resolve naming scheme
        if names is None or names == "e":
            self._names = None  # default e1/e₁ scheme
            self._latex_names = None
        elif isinstance(names, str):
            preset = self.PRESETS.get(names)
            if preset is None:
                raise ValueError(f"Unknown naming preset: {names!r}")
            result = preset(self._n)
            self._names = (result[0], result[1])
            self._latex_names = result[2] if len(result) > 2 else None
        else:
            code, uni = names
            if len(code) != self._n or len(uni) != self._n:
                raise ValueError(f"Names must have {self._n} entries, got {len(code)}/{len(uni)}")
            self._names = (list(code), list(uni))
            self._latex_names = None

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
            self._grade_masks[k] = np.array([bin(i).count("1") == k for i in range(self._dim)], dtype=bool)

        # Precompute complement signs: complement(e_S) = sign[S] * e_{S^c}
        # The complement is metric-independent — it maps grade-k to grade-(n-k)
        # by index set complement, with the sign chosen so that
        # e_S * complement(e_S) = pseudoscalar for all basis blades.
        full = self._dim - 1
        comp_sign = np.zeros(self._dim)
        for s in range(self._dim):
            sc = full ^ s
            # Count swaps: for each bit in S^c, count bits in S above it
            swaps = 0
            for i in range(self._n):
                if sc & (1 << i):
                    swaps += bin(s >> (i + 1)).count("1")
            comp_sign[s] = (-1) ** swaps
        self._complement_sign = comp_sign

        # Build BasisBlade objects for every blade in the algebra
        _SUBS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
        self._blades = {}
        for idx in range(self._dim):
            if idx == 0:
                a, u, l = "1", "1", "1"
            else:
                if self._names is None:
                    digits = "".join(str(k + 1) for k in range(self._n) if idx & (1 << k))
                    a = "e" + digits
                    u = "e" + digits.translate(_SUBS)
                    l = f"e_{{{digits}}}"
                else:
                    code, uni = self._names
                    a = "".join(code[k] for k in range(self._n) if idx & (1 << k))
                    u = "".join(uni[k] for k in range(self._n) if idx & (1 << k))
                    if self._latex_names is not None:
                        l = " ".join(self._latex_names[k] for k in range(self._n) if idx & (1 << k))
                    else:
                        l = " ".join(code[k] for k in range(self._n) if idx & (1 << k))
            self._blades[idx] = BasisBlade(idx, a, u, l)

    def _blade_product(self, a: int, b: int) -> tuple[int, float]:
        """Compute the geometric product of two basis blades given as bitmask indices.

        The geometric product of e_A * e_B involves three steps:
        1. Reordering sign: count transpositions to merge the two index sets.
        2. Result blade: XOR the bitmasks (shared indices cancel out).
        3. Metric factor: each shared basis vector contributes its signature
           value (the square of that basis vector: +1, -1, or 0).

        If any shared basis vector is degenerate (signature 0), the entire
        product vanishes — this is how null/projective dimensions work.

        Returns:
            (result_bitmask, sign * metric_factor)
        """
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

    @property
    def notation(self):
        """The Notation object controlling symbolic rendering."""
        return self._notation

    def basis_vectors(self, lazy: bool = False) -> tuple[Multivector, ...]:
        """Return the n basis 1-vectors (named + eager by default).

        Args:
            lazy: If True, return named + lazy blades that build expression
                  trees when used in arithmetic.
        """
        vecs = []
        for k in range(self._n):
            bitmask = 1 << k
            data = np.zeros(self._dim)
            data[bitmask] = 1.0
            mv = Multivector(self, data)
            mv._is_lazy = lazy
            vecs.append(mv)
        return tuple(vecs)

    def pseudoscalar(self, lazy: bool = False) -> Multivector:
        """Return the unit pseudoscalar I (𝑰)."""
        data = np.zeros(self._dim)
        data[self._dim - 1] = 1.0
        mv = Multivector(self, data)
        if lazy:
            mv._is_lazy = True
        return mv

    @property
    def I(self) -> Multivector:
        """Unit pseudoscalar."""
        return self.pseudoscalar()

    @property
    def identity(self) -> Multivector:
        """Scalar identity 𝟙."""
        return self.scalar(1.0)

    def scalar(self, value: float) -> Multivector:
        """Create a scalar multivector (grade-0) with the given value."""
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
        """Lookup a basis blade by name, e.g. 'e1', 'e12', 'e123', or custom names.

        For the default 'e' naming scheme, indices are parsed digit-by-digit
        (e.g. 'e12' means e₁∧e₂). This is ambiguous for algebras with more
        than 9 dimensions — use custom names in that case.
        """
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
        # Default e-index parsing (digit-by-digit, only valid for n <= 9)
        if not name.startswith("e"):
            raise ValueError(f"Invalid blade name: {name!r}")
        if self._n > 9:
            raise ValueError(
                f"Digit-by-digit blade parsing is ambiguous for {self._n}D algebras. "
                f"Use custom names: Algebra(sig, names=(code_names, unicode_names))"
            )
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
                    remaining = remaining[len(code_names[k]) :]
                    matched = True
                    break
            if not matched:
                return None
        return bitmask

    def rotor(self, B: Multivector, radians: float | None = None, degrees: float | None = None) -> Multivector:
        """Create a rotor R = cos(θ/2) - sin(θ/2)B̂ for rotation by θ in plane B.

        B must be an even multivector (scalar, bivector, pseudoscalar in even
        dimensions, or any combination). It does not need to be unit — it is
        normalized automatically. This allows bivectors (spatial rotations),
        scalars (identity), and pseudoscalars like I in STA (U(1) phase).

        Args:
            B: Even multivector defining the rotation generator (normalized internally).
            radians: Rotation angle in radians.
            degrees: Rotation angle in degrees (converted internally).

        Raises:
            ValueError: If B has any odd-grade components.
        """
        if radians is not None and degrees is not None:
            raise ValueError("Specify radians= or degrees=, not both")
        if radians is None and degrees is None:
            raise ValueError("Specify radians= or degrees=")
        if not is_even(B):
            odd = [k for k in range(self._n + 1) if k % 2 == 1 and not np.allclose(grade(B, k).data, 0)]
            raise ValueError(f"B must be an even multivector, but has odd-grade components: {odd}")
        # Reject pure scalars — need at least a grade-2 component to define a rotation plane
        if is_scalar(B):
            raise ValueError("B must contain a bivector (grade-2) component to define a rotation plane")
        theta = radians if radians is not None else np.radians(degrees)
        B_hat = unit(B)
        return self.scalar(np.cos(theta / 2)) - np.sin(theta / 2) * B_hat

    # Aliases
    rotor_from_bivector = rotor
    rotor_from_plane_angle = rotor

    _SUBSCRIPTS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

    def _blade_name(self, index: int, unicode: bool = False) -> str:
        if index == 0:
            return ""
        bb = self._blades[index]
        return bb.unicode_name if unicode else bb.ascii_name

    def _blade_latex(self, index: int) -> str:
        if index == 0:
            return ""
        return self._blades[index].latex_name

    def get_basis_blade(self, mv_or_index) -> BasisBlade:
        """Look up a BasisBlade by multivector or bitmask index.

        Returns the BasisBlade object, which can be renamed::

            alg.get_basis_blade(e1 ^ e2).rename(latex=r"e_{12}")
            alg.get_basis_blade(0b011).rename(ascii="B12")

        Args:
            mv_or_index: A Multivector (must be a basis blade) or an int bitmask.
        """
        if isinstance(mv_or_index, int):
            return self._blades[mv_or_index]
        mv = mv_or_index
        if hasattr(mv, "data"):
            nonzero = np.nonzero(np.abs(mv.data) > 1e-12)[0]
            if len(nonzero) != 1:
                raise ValueError("Not a basis blade — has multiple nonzero components")
            return self._blades[int(nonzero[0])]
        raise TypeError(f"Expected Multivector or int, got {type(mv_or_index)}")

    def __repr__(self) -> str:
        """Short signature notation, e.g. ``Cl(3,0)`` or ``Cl(1,3)``."""
        pos = self._sig.count(1)
        neg = self._sig.count(-1)
        zero = self._sig.count(0)
        parts = [str(pos), str(neg)]
        if zero:
            parts.append(str(zero))
        return f"Cl({','.join(parts)})"


class _DisplayResult:
    """Wrapper so display() output is auto-detected as LaTeX by galaga_marimo."""

    __slots__ = ("_parts", "_sep", "_eval_mv")

    def __init__(self, parts: list[str], sep: str, eval_mv):
        self._parts = parts
        self._sep = sep
        self._eval_mv = eval_mv

    def _render(self, coeff_format: str | None = None) -> str:
        if coeff_format is None or self._eval_mv is None:
            return self._sep.join(self._parts)
        # Re-render with coeff_format on the eval (last) part only
        formatted_eval = self._eval_mv.latex(coeff_format=coeff_format)
        parts = list(self._parts)
        # Replace the last part (eval) if it's present
        if parts and parts[-1] == self._eval_mv.latex():
            parts[-1] = formatted_eval
        return self._sep.join(parts)

    def latex(self, coeff_format: str | None = None) -> str:
        return self._render(coeff_format)

    def _repr_latex_(self) -> str:
        return f"${self._render()}$"

    def __str__(self) -> str:
        return self._render()

    def __repr__(self) -> str:
        return self._render()


class Multivector:
    """A multivector in a Clifford algebra.

    This is a lightweight value type: just an algebra reference plus a dense
    NumPy array of 2^n float64 coefficients. The array index *is* the blade
    bitmask, so ``data[0]`` is the scalar part, ``data[0b001]`` is the e₁
    coefficient, ``data[0b011]`` is the e₁₂ coefficient, etc.

    Operator overloads map to the named functions:
    - ``a * b``  → ``gp(a, b)``     (geometric product)
    - ``a ^ b``  → ``op(a, b)``     (outer/wedge product)
    - ``a | b``  → ``doran_lasenby_inner(a, b)``
    - ``~a``     → ``reverse(a)``
    - ``a[k]``   → ``grade(a, k)``  (grade projection)

    Scalar arithmetic (``3 * v``, ``v + 2``, ``v / 5``) is also supported
    and operates on the coefficient array directly.

    Attributes:
        algebra: The parent ``Algebra`` instance (shared, not copied).
        data: Dense NumPy float64 array of length ``algebra.dim``.
    """

    __slots__ = ("algebra", "data", "_name", "_name_latex", "_name_unicode", "_is_lazy", "_expr", "_grade")

    def __init__(self, algebra: Algebra, data: np.ndarray):
        """Wrap a coefficient array as a multivector in the given algebra.

        Users should not call this directly — use ``Algebra.scalar()``,
        ``Algebra.vector()``, ``Algebra.blade()``, or arithmetic on
        basis vectors instead.
        """
        self.algebra = algebra
        self.data = np.array(data, dtype=np.float64)
        self._name = None
        self._name_latex = None
        self._name_unicode = None
        self._is_lazy = False
        self._expr = None
        self._grade = None

    def _check_same(self, other: Multivector):
        if self.algebra is not other.algebra:
            raise ValueError(
                f"Cannot operate on multivectors from different algebras: {self.algebra} vs {other.algebra}"
            )

    def _copy_with(self, **overrides) -> Multivector:
        """Return a copy with selected fields overridden."""
        mv = Multivector.__new__(Multivector)
        mv.algebra = self.algebra
        mv.data = self.data
        mv._name = overrides.get("_name", self._name)
        mv._name_latex = overrides.get("_name_latex", self._name_latex)
        mv._name_unicode = overrides.get("_name_unicode", self._name_unicode)
        mv._is_lazy = overrides.get("_is_lazy", self._is_lazy)
        mv._expr = overrides.get("_expr", self._expr)
        mv._grade = overrides.get("_grade", self._grade)
        return mv

    def name(
        self,
        label: str | None = None,
        *,
        latex: str | None = None,
        unicode: str | None = None,
        ascii: str | None = None,
    ) -> Multivector:
        """Assign a display name in-place. Sets lazy. Returns self.

        At least one of ``label`` or ``latex`` must be provided. If ``latex``
        is given, ``unicode`` and ``ascii`` are auto-derived from it unless
        explicitly overridden.

        Args:
            label: Default name used for all formats unless overridden. Optional
                   if ``latex`` is provided.
            latex: LaTeX-specific name. Also used to derive unicode/ascii.
            unicode: Unicode-specific name override.
            ascii: ASCII-specific name override.
        """
        if label is None and latex is None:
            raise ValueError("At least one of label or latex must be provided")
        # Auto-derive unicode/ascii from latex if not explicitly given
        if latex is not None and (unicode is None or ascii is None):
            result = LatexSymbols().lookup(latex)
            if result is not None:
                uni_derived, asc_derived = result
                if unicode is None:
                    unicode = uni_derived
                if ascii is None:
                    ascii = asc_derived
        self._name = ascii or label or latex
        self._name_latex = latex or label
        self._name_unicode = unicode or label or self._name
        self._is_lazy = True
        # Auto-detect grade if homogeneous
        if self._grade is None:
            self._grade = self.homogeneous_grade()
        # Build a Sym expr so .anon() can reveal the name-based tree
        if self._expr is None:
            self._expr = _sym.Sym(self, self._name_unicode, name_latex=self._name_latex, name_ascii=self._name)
        return self

    def anon(self) -> Multivector:
        """Remove the display name in-place. Preserves lazy/eager. Returns self."""
        if isinstance(self._expr, _sym.Sym) and self._expr._name == (self._name_unicode or self._name):
            self._expr = None
        self._name = None
        self._name_latex = None
        self._name_unicode = None
        return self

    def lazy(self) -> Multivector:
        """Set lazy mode in-place. Returns self."""
        self._is_lazy = True
        return self

    def eager(self, name: str | None = None) -> Multivector:
        """Force eager evaluation in-place. Strips name unless one is given.

        Args:
            name: If provided, set this as the display name (named eager).
                  If omitted, the name is cleared (anonymous eager).
        """
        self._is_lazy = False
        self._expr = None
        if name is not None:
            self._name = name
            self._name_latex = name
            self._name_unicode = name
        else:
            self._name = None
            self._name_latex = None
            self._name_unicode = None
        return self

    def eval(self) -> Multivector:
        """Return a new anonymous eager copy — the concrete numeric result."""
        return self._copy_with(
            _is_lazy=False,
            _expr=None,
            _name=None,
            _name_latex=None,
            _name_unicode=None,
        )

    def reveal(self) -> Multivector:
        """Return a new anonymous copy with the same lazy/eager state.

        Like eval() but preserves laziness. Useful for displaying the
        underlying value of a named MV without mutating it.
        """
        return self._copy_with(
            _name=None,
            _name_latex=None,
            _name_unicode=None,
        )

    def copy_as(
        self,
        label: str | None = None,
        *,
        latex: str | None = None,
        unicode: str | None = None,
        ascii: str | None = None,
    ) -> Multivector:
        """Return a named copy. Like .name() but non-mutating."""
        return self._copy_with().name(label, latex=latex, unicode=unicode, ascii=ascii)

    def display(self, compact: bool = False) -> _DisplayResult:
        """Return a LaTeX-renderable object showing name = expression = value, omitting duplicates."""
        parts = []
        eval_mv = self.eval()
        name_latex = self.latex() if self._name is not None else None
        eval_latex = eval_mv.latex()

        reveal_latex = None
        if self._is_lazy and self._expr is not None:
            r_latex = self.reveal().latex()
            if r_latex != name_latex and r_latex != eval_latex:
                reveal_latex = r_latex

        if name_latex is not None:
            parts.append(name_latex)
        if reveal_latex is not None:
            parts.append(reveal_latex)
        if eval_latex not in parts:
            parts.append(eval_latex)

        sep = " = " if compact else " \\quad = \\quad "
        return _DisplayResult(parts, sep, eval_mv)

    def _to_expr(self):
        """Convert this MV to an Expr node for use in expression trees.

        Named MVs become Sym nodes (so they appear by name in trees).
        Anonymous lazy MVs use their stored expr tree.
        Anonymous eager MVs become Sym nodes with their string representation,
        using the algebra's LaTeX name for single basis blades.
        """
        if self._name is not None:
            return _sym.Sym(self, self._name_unicode or self._name, name_latex=self._name_latex, name_ascii=self._name)
        if self._expr is not None:
            return self._expr
        display = str(self)
        return _sym.Sym(self, display, name_latex=self.latex())

    # --- Operator overloads ---

    def _is_any_lazy(self, other=None) -> bool:
        if self._is_lazy:
            return True
        if isinstance(other, Multivector) and other._is_lazy:
            return True
        return False

    def _lazy_result(self, data: np.ndarray, expr) -> Multivector:
        """Build a lazy MV with computed data and an expression tree."""
        mv = Multivector.__new__(Multivector)
        mv.algebra = self.algebra
        mv.data = np.array(data, dtype=np.float64)
        mv._name = None
        mv._name_latex = None
        mv._name_unicode = None
        mv._is_lazy = True
        mv._expr = expr
        mv._grade = None
        return mv

    def __add__(self, other):
        if isinstance(other, _sym.Expr):
            return _sym.Add(self._to_expr(), other)
        if isinstance(other, (int, float)):
            d = self.data.copy()
            d[0] += other
            if self._is_lazy:
                return self._lazy_result(d, _sym.Add(self._to_expr(), _sym.Scalar(other)))
            return Multivector(self.algebra, d)
        self._check_same(other)
        if self._is_any_lazy(other):
            return self._lazy_result(
                self.data + other.data,
                _sym.Add(self._to_expr(), other._to_expr()),
            )
        return Multivector(self.algebra, self.data + other.data)

    def __radd__(self, other):
        if isinstance(other, (int, float)) and self._is_lazy:
            d = self.data.copy()
            d[0] += other
            return self._lazy_result(d, _sym.Add(_sym.Scalar(other), self._to_expr()))
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, _sym.Expr):
            return _sym.Sub(self._to_expr(), other)
        if isinstance(other, (int, float)):
            d = self.data.copy()
            d[0] -= other
            if self._is_lazy:
                return self._lazy_result(d, _sym.Sub(self._to_expr(), _sym.Scalar(other)))
            return Multivector(self.algebra, d)
        self._check_same(other)
        if self._is_any_lazy(other):
            return self._lazy_result(
                self.data - other.data,
                _sym.Sub(self._to_expr(), other._to_expr()),
            )
        return Multivector(self.algebra, self.data - other.data)

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            d = -self.data.copy()
            d[0] += other
            if self._is_lazy:
                return self._lazy_result(d, _sym.Sub(_sym.Scalar(other), self._to_expr()))
            return Multivector(self.algebra, d)
        return NotImplemented

    def __neg__(self):
        if self._is_lazy:
            return self._lazy_result(-self.data, _sym.Neg(self._to_expr()))
        return Multivector(self.algebra, -self.data)

    def __mul__(self, other):
        """Geometric product (a * b) or scalar multiplication."""
        if isinstance(other, (int, float)):
            if self._is_lazy:
                return self._lazy_result(
                    self.data * other,
                    _sym.ScalarMul(other, self._to_expr()),
                )
            return Multivector(self.algebra, self.data * other)
        # Handle Expr operands (e.g. _sym.Scalar(1) from symbolic module)
        if isinstance(other, _sym.Expr):
            return _sym.Gp(self._to_expr(), other)
        self._check_same(other)
        if self._is_any_lazy(other):
            return self._lazy_result(
                gp(Multivector(self.algebra, self.data), Multivector(other.algebra, other.data)).data,
                _sym.Gp(self._to_expr(), other._to_expr()),
            )
        return gp(self, other)

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            if self._is_lazy:
                return self._lazy_result(
                    self.data * other,
                    _sym.ScalarMul(other, self._to_expr()),
                )
            return Multivector(self.algebra, self.data * other)
        if isinstance(other, Multivector):
            return other.__mul__(self)
        return NotImplemented

    def __xor__(self, other):
        """Outer product (a ^ b)."""
        if isinstance(other, _sym.Expr):
            return _sym.Op(self._to_expr(), other)
        if isinstance(other, Multivector) and self._is_any_lazy(other):
            result = op(Multivector(self.algebra, self.data), Multivector(other.algebra, other.data))
            return self._lazy_result(
                result.data,
                _sym.Op(self._to_expr(), other._to_expr()),
            )
        return op(self, other)

    def __or__(self, other):
        """Doran–Lasenby inner product (a | b)."""
        if isinstance(other, _sym.Expr):
            return _sym.Dli(self._to_expr(), other)
        if isinstance(other, Multivector) and self._is_any_lazy(other):
            result = doran_lasenby_inner(Multivector(self.algebra, self.data), Multivector(other.algebra, other.data))
            return self._lazy_result(
                result.data,
                _sym.Dli(self._to_expr(), other._to_expr()),
            )
        return doran_lasenby_inner(self, other)

    def __invert__(self):
        """Reverse (~a)."""
        if self._is_lazy:
            result = reverse(Multivector(self.algebra, self.data))
            return self._lazy_result(result.data, _sym.Reverse(self._to_expr()))
        return reverse(self)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            if self._is_lazy:
                return self._lazy_result(
                    self.data / other,
                    _sym.ScalarDiv(self._to_expr(), other),
                )
            return Multivector(self.algebra, self.data / other)
        if isinstance(other, Multivector):
            self._check_same(other)
            if is_scalar(other):
                s = other.data[0]
                if abs(s) < 1e-300:
                    raise ZeroDivisionError("Division by zero scalar multivector")
                # If either side is lazy, build a Div tree
                if self._is_any_lazy(other):
                    return self._lazy_result(
                        self.data / s,
                        _sym.Div(self._to_expr(), other._to_expr()),
                    )
                return Multivector(self.algebra, self.data / s)
            return self * inverse(other)
        return NotImplemented

    def __rtruediv__(self, other):
        """Support scalar / multivector: k / x = k * x⁻¹."""
        if isinstance(other, (int, float)):
            return other * inverse(self)
        return NotImplemented

    def __pow__(self, n):
        if not isinstance(n, int):
            return NotImplemented
        if n == 0:
            return self.algebra.scalar(1.0)
        if n == 2:
            return squared(self)
        if n < 0:
            return inverse(self) ** (-n)
        result = self
        for _ in range(n - 1):
            result = result * self
        return result

    def __eq__(self, other):
        """Approximate equality using ``np.allclose``.

        Supports comparison with other Multivectors (must be from the same
        algebra) and with scalars (int/float), which are compared against
        the scalar part with all other components expected to be zero.

        Note: uses ``np.allclose`` (atol=1e-8, rtol=1e-5) rather than exact
        equality, because floating-point products accumulate rounding errors.
        """
        if isinstance(other, Multivector):
            self._check_same(other)
            return np.allclose(self.data, other.data)
        if isinstance(other, (int, float)):
            expected = np.zeros(self.algebra.dim)
            expected[0] = other
            return np.allclose(self.data, expected)
        return NotImplemented

    def __hash__(self):
        """Hash based on raw coefficient bytes.

        Required because we define ``__eq__`` — without this, Multivector
        would be unhashable, which breaks marimo's cell dependency tracking
        and prevents use in sets/dicts.

        Note: this is consistent with ``__eq__`` for *exact* byte equality,
        but two multivectors that are ``__eq__`` (via ``allclose``) may have
        different hashes if their floats differ in the last bits. This is an
        acceptable trade-off — hash collisions are harmless, and the
        alternative (quantising floats) adds complexity for little benefit.
        """
        return hash(self.data.tobytes())

    def __getitem__(self, k: int) -> Multivector:
        """Grade projection: x[k] returns grade-k component."""
        return grade(self, k)

    # --- Convenience properties/methods ---

    @property
    def inv(self) -> Multivector:
        """Inverse: x⁻¹"""
        if self._is_lazy:
            result = inverse(Multivector(self.algebra, self.data))
            return self._lazy_result(result.data, _sym.Inverse(self._to_expr()))
        return inverse(self)

    @property
    def dag(self) -> Multivector:
        """Reverse (dagger): x†"""
        return ~self

    @property
    def sq(self) -> Multivector:
        """Squared: x²"""
        if self._is_lazy:
            result = gp(Multivector(self.algebra, self.data), Multivector(self.algebra, self.data))
            return self._lazy_result(result.data, _sym.Squared(self._to_expr()))
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

    def homogeneous_grade(self) -> int | None:
        """Return the grade if this MV is homogeneous, or None if mixed.

        A multivector is homogeneous if all its nonzero coefficients belong
        to the same grade. Returns that grade, or None if multiple grades
        are present or the MV is zero.
        """
        alg = self.algebra
        found = None
        for k in range(alg.n + 1):
            if np.any(np.abs(self.data[alg._grade_masks[k]]) > 1e-12):
                if found is not None:
                    return None  # multiple grades
                found = k
        return found

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
            elif np.isclose(abs(c), 1.0):
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
        """Unicode representation (same as str)."""
        return self.__str__()

    def __str__(self) -> str:
        """Unicode representation, e.g. ``3 + 2e₁ - e₃``."""
        if self._name_unicode is not None:
            return self._name_unicode
        if self._name is not None:
            return self._name
        if self._is_lazy and self._expr is not None:
            return _render.render(self._expr, self.algebra._notation)
        return self._format(unicode=True)

    def __format__(self, spec: str) -> str:
        """Support format specs: numeric specs (e.g. '.3f') format coefficients,
        'latex'/'unicode'/'ascii' select representation mode."""
        if spec in ("", "s"):
            return str(self)
        if spec == "latex":
            return self.latex()
        if spec in ("unicode", "u"):
            if self._name_unicode is not None:
                return self._name_unicode
            if self._is_lazy and self._expr is not None:
                return _render.render(self._expr, self.algebra._notation)
            return self._format(unicode=True)
        if spec in ("ascii", "a"):
            if self._name is not None:
                return self._name
            if self._is_lazy and self._expr is not None:
                return _render.render(self._expr, self.algebra._notation)
            return self._format(unicode=False)
        # Numeric format spec — apply to each coefficient, no threshold
        alg = self.algebra
        terms = []
        for i in range(alg.dim):
            c = self.data[i]
            if c == 0.0:
                continue
            name = alg._blade_name(i, unicode=True)
            formatted_c = format(c, spec)
            if name == "":
                terms.append(formatted_c)
            else:
                terms.append(f"{formatted_c}{name}")
        if not terms:
            return format(0.0, spec)
        result = terms[0]
        for t in terms[1:]:
            if t.startswith("-"):
                result += " - " + t[1:]
            else:
                result += " + " + t
        return result

    def latex(self, wrap: str | None = None, coeff_format: str | None = None) -> str:
        """Return LaTeX representation of this multivector.

        Args:
            wrap: Optional delimiter — '$' for inline, '$$' for display block.
            coeff_format: Optional format spec for coefficients (e.g. '.3f').
                         When set, all coefficients are shown explicitly
                         (the drop-1 convention is disabled).
        """
        # Named → return name
        if self._name_latex is not None and coeff_format is None:
            raw = self._name_latex
        elif self._name is not None and coeff_format is None:
            raw = self._name
        # Anonymous lazy → delegate to renderer
        elif self._is_lazy and self._expr is not None and coeff_format is None:
            raw = _render.render_latex(self._expr, self.algebra._notation)
        else:
            # Eager anonymous → existing coefficient rendering
            alg = self.algebra
            terms = []
            for i in range(alg.dim):
                c = self.data[i]
                if coeff_format:
                    if c == 0.0:
                        continue
                else:
                    if abs(c) < 1e-12:
                        continue
                name = alg._blade_latex(i)
                if coeff_format:
                    formatted_c = format(c, coeff_format)
                    if name == "":
                        terms.append(formatted_c)
                    else:
                        terms.append(f"{formatted_c} {name}")
                else:
                    if name == "":
                        terms.append(f"{c:g}")
                    elif np.isclose(abs(c), 1.0):
                        terms.append(name if c > 0 else f"-{name}")
                    else:
                        terms.append(f"{c:g} {name}")
            if not terms:
                raw = format(0.0, coeff_format) if coeff_format else "0"
            else:
                raw = terms[0]
                for t in terms[1:]:
                    if t.startswith("-"):
                        raw += " - " + t[1:]
                    else:
                        raw += " + " + t
        if wrap == "$":
            return f"${raw}$"
        if wrap == "$$":
            return f"$$\n{raw}\n$$"
        return raw

    def _repr_latex_(self) -> str:
        """Jupyter/Marimo notebook integration."""
        return f"${self.latex()}$"


# ============================================================
# Core named operations
# ============================================================
#
# Every GA product is a module-level function. This is the stable public API.
# Operators on Multivector (*, ^, |, ~) are convenience sugar that delegate here.
#
# Implementation pattern: all products iterate over nonzero coefficients of the
# operands and accumulate into an output array using the precomputed multiplication
# tables. The differences between products are *which grade combinations survive*:
#
#   gp:                  all grades (full geometric product)
#   op:                  grade(a) + grade(b) only (wedge)
#   left_contraction:    grade(b) - grade(a) only, must be ≥ 0
#   right_contraction:   grade(a) - grade(b) only, must be ≥ 0
#   doran_lasenby_inner: |grade(a) - grade(b)|, including scalars (the | operator)
#   hestenes_inner:      |grade(a) - grade(b)|, but zero if either is grade-0
#   scalar_product:      grade-0 only (just the scalar part of gp)
# ============================================================


@lazy_binary("Gp")
def gp(a: Multivector, b: Multivector) -> Multivector:
    """Geometric product — the fundamental product of Clifford algebra.

    Computes a*b using the precomputed multiplication tables. For each nonzero
    coefficient in ``a``, we vectorise the scatter-add across all of ``b``'s
    coefficients at once (using NumPy fancy indexing), which is significantly
    faster than a double Python loop for dense multivectors.
    """
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


@lazy_binary("Op")
def op(a: Multivector, b: Multivector) -> Multivector:
    """Outer (wedge) product — keeps only the grade-raising part of gp.

    For homogeneous blades of grade r and s, the outer product is the
    grade-(r+s) part of the geometric product. For mixed-grade multivectors,
    it's applied component-wise: each (grade_i, grade_j) pair contributes
    only if the result lands on grade i+j.

    Key property: a ∧ a = 0 for any vector a (antisymmetry).
    """
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


@lazy_binary("Lc")
def left_contraction(a: Multivector, b: Multivector) -> Multivector:
    """Left contraction: a ⌋ b.

    Keeps only the grade-(s-r) part of gp(a, b), where r = grade(a) and
    s = grade(b). If r > s, the result is zero — you can't "remove" more
    grade than is present.

    This is the most common inner product in GA literature. It answers:
    "project out the part of b that contains a". For example,
    ``left_contraction(e1, e12)`` = e₂ — the e₁ "factor" is removed.

    Key difference from Hestenes inner: left contraction allows scalars
    to pass through (scalar ⌋ x = scalar * x), while Hestenes kills them.
    """
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


@lazy_binary("Rc")
def right_contraction(a: Multivector, b: Multivector) -> Multivector:
    """Right contraction: a ⌊ b.

    Mirror of left contraction: keeps grade-(r-s) part of gp(a, b).
    If r < s, the result is zero.

    Satisfies: right_contraction(a, b) = reverse(left_contraction(reverse(b), reverse(a)))
    """
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


@lazy_binary("Hi")
def hestenes_inner(a: Multivector, b: Multivector) -> Multivector:
    """Hestenes inner product.

    Like left contraction but with two key differences:
    1. Uses |grade(a) - grade(b)| instead of grade(b) - grade(a), so it's
       nonzero in both directions (e.g. bivector · vector ≠ 0).
    2. Kills scalars: if either operand is grade-0, the result is zero.

    For vector-on-vector, all inner products agree. The differences only show
    up with mixed grades — see the README comparison table for examples.
    """
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


@lazy_binary("Dli")
def doran_lasenby_inner(a: Multivector, b: Multivector) -> Multivector:
    """Doran–Lasenby inner product: grade-|r-s| part of gp(a,b), including scalars.

    Like Hestenes inner but does NOT kill scalars. When either operand is
    grade-0, the result is the scalar times the other operand (grade
    difference = the other operand's grade).

    This is the ``|`` operator on Multivector, and the convention used by
    Doran & Lasenby ("Geometric Algebra for Physicists") and Dorst et al.
    ("Geometric Algebra for Computer Science").
    """
    a._check_same(b)
    alg = a.algebra
    out = np.zeros(alg.dim)
    for i in np.nonzero(a.data)[0]:
        gi = bin(i).count("1")
        ai = a.data[i]
        for j in np.nonzero(b.data)[0]:
            gj = bin(j).count("1")
            target_grade = abs(gi - gj)
            k = alg._mul_index[i, j]
            if bin(k).count("1") == target_grade:
                out[k] += ai * b.data[j] * alg._mul_sign[i, j]
    return Multivector(alg, out)


dorst_inner = doran_lasenby_inner


@lazy_binary("Sp")
def scalar_product(a: Multivector, b: Multivector) -> Multivector:
    """Scalar product: grade-0 part of the geometric product."""
    return grade(gp(a, b), 0)


def commutator(a: Multivector, b: Multivector) -> Multivector:
    """Commutator: ab - ba."""
    if a._is_lazy or b._is_lazy:
        result = gp(Multivector(a.algebra, a.data), Multivector(b.algebra, b.data)) - gp(
            Multivector(b.algebra, b.data), Multivector(a.algebra, a.data)
        )
        return a._lazy_result(result.data, _sym.Commutator(a._to_expr(), b._to_expr()))
    return gp(a, b) - gp(b, a)


def anticommutator(a: Multivector, b: Multivector) -> Multivector:
    """Anticommutator: ab + ba."""
    if a._is_lazy or b._is_lazy:
        result = gp(Multivector(a.algebra, a.data), Multivector(b.algebra, b.data)) + gp(
            Multivector(b.algebra, b.data), Multivector(a.algebra, a.data)
        )
        return a._lazy_result(result.data, _sym.Anticommutator(a._to_expr(), b._to_expr()))
    return gp(a, b) + gp(b, a)


def lie_bracket(a: Multivector, b: Multivector) -> Multivector:
    """Lie bracket: ½(ab - ba).

    The half-scaled commutator under which bivectors form a Lie algebra
    with clean structure constants: [Bᵢ, Bⱼ] = εᵢⱼₖ Bₖ.
    """
    if a._is_lazy or b._is_lazy:
        result = commutator(Multivector(a.algebra, a.data), Multivector(b.algebra, b.data)) * 0.5
        return a._lazy_result(result.data, _sym.LieBracket(a._to_expr(), b._to_expr()))
    return commutator(a, b) * 0.5


def jordan_product(a: Multivector, b: Multivector) -> Multivector:
    """Jordan product: ½(ab + ba).

    The symmetric part of the geometric product. For vectors,
    this equals the inner product: a ∘ b = a · b.
    """
    if a._is_lazy or b._is_lazy:
        result = anticommutator(Multivector(a.algebra, a.data), Multivector(b.algebra, b.data)) * 0.5
        return a._lazy_result(result.data, _sym.JordanProduct(a._to_expr(), b._to_expr()))
    return anticommutator(a, b) * 0.5


# --- Unary operations ---


def reverse(x: Multivector) -> Multivector:
    """Reverse (†, tilde): reverses the order of basis vectors in each blade.

    The grade-k component is multiplied by (-1)^(k(k-1)/2):
    - grade 0, 1: unchanged  (sign = +1)
    - grade 2, 3: negated    (sign = -1)
    - grade 4, 5: unchanged  (sign = +1)
    - ...and so on in a period-4 cycle.

    Why this matters: the reverse is the natural "adjoint" in GA. For a
    versor (product of vectors) V = v₁v₂...vₖ, the reverse is
    ~V = vₖ...v₂v₁. The sandwich product R x ~R uses the reverse to
    apply rotations/boosts, and V~V gives the squared norm.
    """
    if x._is_lazy:
        return ~x
    alg = x.algebra
    out = x.data.copy()
    for k in range(alg.n + 1):
        sign = (-1) ** (k * (k - 1) // 2)
        if sign == -1:
            out[alg._grade_masks[k]] *= -1
    return Multivector(alg, out)


@lazy_unary("Involute")
def involute(x: Multivector) -> Multivector:
    """Grade involution (hat): grade-k component is multiplied by (-1)^k.

    Even grades are unchanged, odd grades are negated. This is the
    automorphism that distinguishes the even and odd sub-algebras.
    """
    alg = x.algebra
    out = x.data.copy()
    for k in range(alg.n + 1):
        if k % 2 == 1:
            out[alg._grade_masks[k]] *= -1
    return Multivector(alg, out)


@lazy_unary("Conjugate")
def conjugate(x: Multivector) -> Multivector:
    """Clifford conjugate: reverse composed with grade involution.

    Combines both sign-flip patterns. The grade-k component is multiplied
    by (-1)^(k(k+1)/2). This is the composition ``involute(reverse(x))``.
    """
    return involute(reverse(x))


def grade(x: Multivector, k: int | str) -> Multivector:
    """Extract grade-k component, or 'even'/'odd' for parity selection."""
    if x._is_lazy:
        if k == "even":
            result = even_grades(Multivector(x.algebra, x.data))
            return x._lazy_result(result.data, _sym.Even(x._to_expr()))
        if k == "odd":
            result = odd_grades(Multivector(x.algebra, x.data))
            return x._lazy_result(result.data, _sym.Odd(x._to_expr()))
        result = grade(Multivector(x.algebra, x.data), k)
        return x._lazy_result(result.data, _sym.Grade(x._to_expr(), k))
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


def scalar_sqrt(x) -> Multivector:
    """Square root of a scalar multivector or number.

    Accepts a Multivector or a plain number (int/float). Numbers are
    coerced to scalar MVs if possible, otherwise np.sqrt is used.
    """
    if isinstance(x, (int, float)):
        if x < 0:
            raise ValueError(f"scalar_sqrt of negative value {x}")
        # No algebra context — but if we got here from a plain number,
        # just return a float. The user can wrap it if needed.
        return x.__class__(np.sqrt(x))
    if not isinstance(x, Multivector):
        raise TypeError(f"scalar_sqrt expects a Multivector or number, got {type(x).__name__}")
    # Lazy path
    if x._is_lazy:
        import galaga.expr as _expr_mod

        result = scalar_sqrt(Multivector(x.algebra, x.data))
        return x._lazy_result(result.data, _expr_mod.Sqrt(x._to_expr()))
    # Eager path
    if not is_scalar(x):
        raise ValueError("scalar_sqrt requires a pure scalar multivector")
    s = float(x.data[0])
    if s < 0:
        raise ValueError(f"scalar_sqrt of negative value {s}")
    return x.algebra.scalar(np.sqrt(s))


@lazy_unary("Dual")
def dual(x: Multivector) -> Multivector:
    """Dual: left-contract x into the inverse pseudoscalar.

    Maps a grade-k blade to a grade-(n-k) blade. In 3D Euclidean space,
    dual(e₁ ∧ e₂) = e₃. This is the standard Hodge-like duality in GA.

    Implementation: ``left_contraction(x, I⁻¹)`` where I is the unit
    pseudoscalar. We use left contraction (not geometric product with I⁻¹)
    because it gives the correct grade mapping for all signatures.
    """
    I_inv = inverse(x.algebra.pseudoscalar())
    return left_contraction(x, I_inv)


@lazy_unary("Undual")
def undual(x: Multivector) -> Multivector:
    """Undual: left-contract x into the pseudoscalar (inverse of dual).

    ``undual(dual(x)) = x`` for all x.
    """
    I = x.algebra.pseudoscalar()
    return left_contraction(x, I)


@lazy_unary("Complement")
def complement(x: Multivector) -> Multivector:
    """Right complement: metric-independent duality.

    Maps grade-k to grade-(n-k) by replacing each basis blade's index set
    with its complement, with a sign chosen so that
    ``x * complement(x)`` is proportional to the pseudoscalar.

    Unlike ``dual()``, this works in **all** signatures including degenerate
    algebras (PGA). It is purely combinatorial — no metric is used.
    """
    alg = x.algebra
    full = alg.dim - 1
    out = np.zeros(alg.dim)
    for i in range(alg.dim):
        if x.data[i] != 0:
            out[full ^ i] += alg._complement_sign[i] * x.data[i]
    return Multivector(alg, out)


@lazy_unary("Uncomplement")
def uncomplement(x: Multivector) -> Multivector:
    """Inverse of complement: ``uncomplement(complement(x)) = x`` for all x."""
    alg = x.algebra
    full = alg.dim - 1
    out = np.zeros(alg.dim)
    for i in range(alg.dim):
        if x.data[i] != 0:
            # Inverse sign: complement_sign[S^c] since we're going backwards
            j = full ^ i
            out[j] += alg._complement_sign[j] * x.data[i]
    return Multivector(alg, out)


@lazy_binary("Regressive")
def regressive_product(a: Multivector, b: Multivector) -> Multivector:
    """Regressive product (meet): complement-based, works in all signatures.

    Computes the intersection of the subspaces represented by blades a and b.
    Uses the complement operator (metric-independent), so it works in
    degenerate algebras like PGA where the pseudoscalar is not invertible.

    Definition: a ∨ b = uncomplement(complement(a) ∧ complement(b))
    """
    return uncomplement(op(complement(a), complement(b)))


def metric_regressive_product(a: Multivector, b: Multivector) -> Multivector:
    """Regressive product via metric dual: (a* ∧ b*)*.

    Only works in nondegenerate algebras (VGA, STA, CGA).
    Raises ValueError in degenerate algebras (PGA).
    """
    return undual(op(dual(a), dual(b)))


# Aliases
meet = regressive_product
join = op


def norm2(x: Multivector) -> float:
    """Squared norm: scalar part of x * ~x."""
    return gp(x, reverse(x)).scalar_part


def norm(x: Multivector):
    """Norm: sqrt(|norm2(x)|). Returns float for eager, lazy scalar MV for lazy."""
    if x._is_lazy:
        val = float(np.sqrt(abs(norm2(x))))
        result = x.algebra.scalar(val)
        return x._lazy_result(result.data, _sym.Norm(x._to_expr()))
    return float(np.sqrt(abs(norm2(x))))


@lazy_unary("Unit")
def unit(x: Multivector) -> Multivector:
    """Normalize to unit multivector."""
    n = norm(x)
    if n < 1e-15:
        raise ValueError("Cannot normalize near-zero multivector")
    return x / n


@lazy_unary("Inverse")
def inverse(x: Multivector) -> Multivector:
    """Versor inverse: x⁻¹ = ~x / (x * ~x).scalar_part.

    This works for versors (products of non-null vectors), which includes
    all rotors, vectors, and most objects you'd want to invert in practice.
    It does NOT work for arbitrary multivectors — a general multivector
    inverse requires solving a linear system, which this library doesn't
    implement (by design: if you need it, you probably want a different
    approach).

    Raises ValueError if the multivector is not invertible (x * ~x ≈ 0).
    """
    x_rev = reverse(x)
    denom = gp(x, x_rev).scalar_part
    if abs(denom) < 1e-15:
        raise ValueError("Multivector is not invertible")
    return x_rev / denom


# --- Predicates ---


def is_scalar(x: Multivector) -> bool:
    """True if x is a pure scalar (all non-grade-0 components are zero)."""
    return np.allclose(x.data[1:], 0)


def is_vector(x: Multivector) -> bool:
    """True if x is a pure 1-vector."""
    return x == grade(x, 1)


def is_bivector(x: Multivector) -> bool:
    """True if x is a pure 2-vector."""
    return x == grade(x, 2)


def is_even(x: Multivector) -> bool:
    """True if x contains only even-grade components (grades 0, 2, 4, …)."""
    alg = x.algebra
    for k in range(alg.n + 1):
        if k % 2 == 1 and np.any(np.abs(x.data[alg._grade_masks[k]]) > 1e-12):
            return False
    return True


def is_rotor(x: Multivector) -> bool:
    """True if x is a rotor: even-graded and x * ~x ≈ 1."""
    return is_even(x) and np.isclose(gp(x, reverse(x)).scalar_part, 1.0)


def is_basis_blade(x: Multivector) -> bool:
    """True if x is a basis blade (possibly scaled).

    A basis blade has exactly one nonzero component in the coefficient
    array. e.g. e₁, 3e₁₂, -e₁₂₃ are blades; e₁ + e₂ is not.
    """
    return np.count_nonzero(np.abs(x.data) > 1e-12) == 1


@lazy_unary("Even")
def even_grades(x: Multivector) -> Multivector:
    """Extract even-grade components."""
    alg = x.algebra
    return grades(x, [k for k in range(0, alg.n + 1, 2)])


@lazy_unary("Odd")
def odd_grades(x: Multivector) -> Multivector:
    """Extract odd-grade components."""
    alg = x.algebra
    return grades(x, [k for k in range(1, alg.n + 1, 2)])


def squared(x: Multivector) -> Multivector:
    """Geometric product of x with itself: x²."""
    if x._is_lazy:
        return x.sq
    return gp(x, x)


def sandwich(r: Multivector, x: Multivector) -> Multivector:
    """Sandwich product: r x ~r.

    The fundamental transformation in GA. When r is a rotor (even-graded,
    r*~r = 1), this applies the rotation/boost encoded by r to x.
    Grade-preserving: if x is grade-k, the result is also grade-k.

    Laziness-aware: if r or x is lazy, the result is lazy with a symbolic
    expression tree.
    """
    return r * x * ~r


sw = sandwich


@lazy_unary("Exp")
def exp(B: Multivector) -> Multivector:
    """Bivector exponential: exp(B) = cos(|B|) + sin(|B|) * B/|B|.

    For a bivector B in a Euclidean algebra (B² < 0), this produces a rotor.
    For a timelike bivector (B² > 0), uses hyperbolic functions instead:
    exp(B) = cosh(|B|) + sinh(|B|) * B/|B|.
    For a null bivector (B² = 0), exp(B) = 1 + B.

    This is the standard way to build a rotor from a bivector without
    manually computing cos(θ/2) and sin(θ/2). Note: ``alg.rotor(B, radians=θ)``
    computes ``exp(-θ/2 * B)`` for a unit bivector B.
    """
    B2 = gp(B, B).scalar_part
    if abs(B2) < 1e-15:
        # Null bivector: exp(B) = 1 + B
        return B.algebra.scalar(1.0) + B
    if B2 < 0:
        # Spacelike bivector (Euclidean rotation): B² < 0
        mag = np.sqrt(-B2)
        return B.algebra.scalar(np.cos(mag)) + np.sin(mag) / mag * B
    else:
        # Timelike bivector (hyperbolic/boost): B² > 0
        mag = np.sqrt(B2)
        return B.algebra.scalar(np.cosh(mag)) + np.sinh(mag) / mag * B


@lazy_unary("Log")
def log(R: Multivector) -> Multivector:
    """Rotor logarithm: extract the bivector B such that exp(B) = R.

    R should be a normalised rotor (even-graded, R*~R = 1). Returns the
    bivector B. For Euclidean rotors, B encodes the half-angle and plane:
    the rotation angle is 2*norm(B) and the plane is unit(B).

    Raises ValueError if R is a pure scalar ±1 (log is zero or undefined).
    """
    s = R.data[0]  # scalar part
    B = R - R.algebra.scalar(s)  # bivector part
    B2 = gp(B, B).scalar_part

    if abs(B2) < 1e-15:
        # Pure scalar rotor: R ≈ ±1, log = 0
        return R.algebra.scalar(0.0) * R

    if B2 < 0:
        # Euclidean rotor
        mag = np.sqrt(-B2)
        theta = np.arctan2(mag, s)
        return (theta / mag) * B
    else:
        # Hyperbolic rotor
        mag = np.sqrt(B2)
        phi = np.arctanh(mag / s) if abs(s) > abs(mag) else np.arctan2(mag, s)
        return (phi / mag) * B


def project(v: Multivector, B: Multivector) -> Multivector:
    """Project v onto the subspace defined by blade B.

    Computes the component of v that lies within B:
    project(v, B) = (v ⌋ B) * B⁻¹

    For a vector v and a blade B, this gives the part of v parallel to B.
    """
    return gp(left_contraction(v, B), inverse(B))


def reject(v: Multivector, B: Multivector) -> Multivector:
    """Reject v from the subspace defined by blade B.

    Computes the component of v perpendicular to B:
    reject(v, B) = v - project(v, B)

    For a vector v and a blade B, this gives the part of v orthogonal to B.
    """
    return v - project(v, B)


def reflect(v: Multivector, n: Multivector) -> Multivector:
    """Reflect v in the hyperplane orthogonal to vector n.

    Computes -n * v * n⁻¹. The vector n defines the normal to the
    reflection hyperplane. For a unit vector n, this simplifies to
    -n * v * n.

    Note: this is a sandwich product with a sign flip. For reflection
    *through* n (not the hyperplane), use ``sandwich(n, v)`` instead.
    """
    return gp(gp(-n, v), inverse(n))


# --- Aliases ---
# These are literally the same functions, not wrappers. They exist so users
# can write whichever name feels natural: ``wedge(a, b)`` or ``op(a, b)``,
# ``rev(x)`` or ``reverse(x)``, etc. The short names are the "canonical" ones
# used throughout the codebase; the long names are for readability.

geometric_product = gp
wedge = op
outer_product = op
rev = reverse
grade_involution = involute
normalize = unit
normalise = unit
norm_squared = norm2
magnitude_squared = norm2
mag2 = norm2


def ip(a: Multivector, b: Multivector, mode: str = "doran_lasenby") -> Multivector:
    """Unified inner product dispatcher — removes ambiguity about which inner product.

    GA has multiple inner products that agree on simple cases (vector·vector)
    but diverge on mixed grades. Rather than guessing, this function makes
    the choice explicit.

    Modes:
        "doran_lasenby" — Doran–Lasenby inner product (default). Uses |r-s|
                     grade selection, includes scalars. This is the ``|``
                     operator. Also known as the Dorst inner product.
        "hestenes" — Hestenes inner product. Like Doran–Lasenby but kills
                     scalars (zero if either operand is grade-0).
        "left"     — Left contraction (a ⌋ b). Grade s-r, zero if r > s.
                     Most common in GA literature.
        "right"    — Right contraction (a ⌊ b). Grade r-s, zero if s > r.
                     Mirror of left contraction.
        "scalar"   — Scalar product. Grade-0 part of gp(a, b) only.
    """
    match mode:
        case "doran_lasenby" | "dorst":
            return doran_lasenby_inner(a, b)
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
                f"Use 'doran_lasenby', 'dorst', 'hestenes', 'left', 'right', or 'scalar'."
            )


inner_product = ip
