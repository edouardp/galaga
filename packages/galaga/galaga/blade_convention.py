"""Blade naming conventions for Clifford algebras.

Controls how basis blades are named and displayed. Orthogonal to the
metric (which defines the algebra) and to Notation (which controls
how operations are rendered).

Usage::

    from galaga import Algebra, b_default, b_gamma, b_pga, b_sta

    Algebra(3)                              # default: e₁₂ compact
    Algebra(1, 3, blades=b_gamma())         # γ₀, γ₁, γ₂, γ₃
    Algebra(3, 0, 1, blades=b_pga())        # e₀₁ compact, PSS → I
    Algebra(1, 3, blades=b_sta(sigmas=True)) # γ₀…γ₃, σ₁/σ₂/σ₃
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from galaga.basis_blade import BasisBlade

_SUBS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


@dataclass
class BladeConvention:
    """Configuration for blade naming and display.

    Attributes:
        vector_names: Per-vector names. Each entry is a string (all formats)
            or a 3-tuple (ascii, unicode, latex). If None, generated from
            prefix and index_base.
        style: How multi-vector blades are derived: "compact", "juxtapose", "wedge".
        overrides: Per-blade name overrides using metric-role keys.
        index_base: Starting index for auto-generated names (0 or 1).
        prefix: Basis vector prefix for auto-generated names.
    """

    vector_names: tuple | list | None = None
    style: str = "compact"
    overrides: dict | None = None
    index_base: int = 1
    prefix: str = "e"


def _parse_name_value(val):
    """Normalize an override/rename value to (ascii, unicode, latex)."""
    if isinstance(val, str):
        return val, val, val
    if isinstance(val, tuple):
        if len(val) == 2:
            return val[0], val[1], val[1]
        if len(val) == 3:
            return val[0], val[1], val[2]
    raise ValueError(f"Name value must be str, 2-tuple, or 3-tuple, got {val!r}")


def _resolve_metric_role_key(key: str, signature: tuple) -> int:
    """Parse a metric-role key like '+1-2' or 'pss' into a bitmask."""
    if key == "pss":
        return (1 << len(signature)) - 1

    # Group signature indices by metric sign
    pos = [i for i, s in enumerate(signature) if s == 1]
    neg = [i for i, s in enumerate(signature) if s == -1]
    null = [i for i, s in enumerate(signature) if s == 0]

    # Parse components: +1, -2, _1 etc (spaces optional)
    stripped = key.replace(" ", "")
    parts = re.findall(r"([+\-_])(\d+)", stripped)
    if not parts or len("".join(s + d for s, d in parts)) != len(stripped):
        raise ValueError(f"Invalid metric-role key: {key!r}")

    bitmask = 0
    for sign, num_str in parts:
        idx = int(num_str) - 1  # 1-indexed in the key
        if sign == "+":
            if idx < 0 or idx >= len(pos):
                raise ValueError(
                    f"Positive vector index {int(num_str)} out of range (algebra has {len(pos)} positive vectors)"
                )
            bitmask |= 1 << pos[idx]
        elif sign == "-":
            if idx < 0 or idx >= len(neg):
                raise ValueError(
                    f"Negative vector index {int(num_str)} out of range (algebra has {len(neg)} negative vectors)"
                )
            bitmask |= 1 << neg[idx]
        elif sign == "_":
            if idx < 0 or idx >= len(null):
                raise ValueError(
                    f"Null vector index {int(num_str)} out of range (algebra has {len(null)} null vectors)"
                )
            bitmask |= 1 << null[idx]
    return bitmask


_PREFIX_MAP = {
    "γ": ("y", "γ", r"\gamma"),
    "σ": ("s", "σ", r"\sigma"),
}


def _gen_vector_names(conv: BladeConvention, n: int) -> list[tuple[str, str, str]]:
    """Generate (ascii, unicode, latex) for each basis vector."""
    if conv.vector_names is not None:
        result = []
        for v in conv.vector_names:
            result.append(_parse_name_value(v))
        if len(result) < n:
            raise ValueError(f"vector_names has {len(result)} entries, need at least {n}")
        return result[:n]

    a_pre, u_pre, l_pre = _PREFIX_MAP.get(conv.prefix, (conv.prefix, conv.prefix, conv.prefix))
    names = []
    for i in range(n):
        idx = i + conv.index_base
        s = str(idx)
        a = f"{a_pre}{s}"
        u = f"{u_pre}{s.translate(_SUBS)}"
        lx = f"{l_pre}_{{{s}}}"
        names.append((a, u, lx))
    return names


def _common_prefix(strings: list[str]) -> str:
    """Find the longest common prefix of a list of strings."""
    if not strings:
        return ""
    prefix = strings[0]
    for s in strings[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix


def build_blades(
    conv: BladeConvention,
    signature: tuple,
) -> dict[int, BasisBlade]:
    """Build all BasisBlade objects for an algebra.

    Args:
        conv: The blade convention to apply.
        signature: The algebra's metric signature tuple.

    Returns:
        Dict mapping bitmask index to BasisBlade.
    """
    n = len(signature)
    dim = 1 << n
    vec_names = _gen_vector_names(conv, n)

    # Build blade names by style
    blades = {}
    for idx in range(dim):
        if idx == 0:
            blades[idx] = BasisBlade(0, "1", "1", "1")
            continue

        bits = [k for k in range(n) if idx & (1 << k)]
        a_parts = [vec_names[k][0] for k in bits]
        u_parts = [vec_names[k][1] for k in bits]
        l_parts = [vec_names[k][2] for k in bits]

        if conv.style == "compact":
            # Try to merge subscripts under common prefix
            u_prefix = _common_prefix(u_parts)
            a_prefix = _common_prefix(a_parts)
            if u_prefix and a_prefix:
                u_subs = "".join(p[len(u_prefix) :] for p in u_parts)
                a_subs = "".join(p[len(a_prefix) :] for p in a_parts)
                a = f"{a_prefix}{a_subs}"
                u = f"{u_prefix}{u_subs}"
                # LaTeX: extract subscript content from each latex name
                # e.g. "e_{1}" → "1", "\gamma_{0}" → "0"
                l_subs = []
                for lp in l_parts:
                    m = re.search(r"_\{([^}]*)\}", lp)
                    l_subs.append(m.group(1) if m else lp)
                # Find latex prefix (everything before _{...})
                m = re.match(r"^(.*?)_\{", l_parts[0])
                l_prefix = m.group(1) if m else a_prefix
                lx = f"{l_prefix}_{{{(''.join(l_subs))}}}"
            else:
                # Fallback to juxtapose
                a = "".join(a_parts)
                u = "".join(u_parts)
                lx = " ".join(l_parts)
        elif conv.style == "wedge":
            a = "^".join(a_parts)
            u = "∧".join(u_parts)
            lx = r" \wedge ".join(l_parts)
        else:  # juxtapose
            a = "".join(a_parts)
            u = "".join(u_parts)
            lx = " ".join(l_parts)

        blades[idx] = BasisBlade(idx, a, u, lx)

    # Apply overrides
    if conv.overrides:
        for key, val in conv.overrides.items():
            if isinstance(key, tuple):
                # Tuple of vector indices — compute bitmask directly
                bitmask = 0
                for idx in key:
                    bitmask |= 1 << idx
            else:
                bitmask = _resolve_metric_role_key(key, signature)
            if isinstance(val, NamedBlade):
                sign = val.sign
                if sign is None and val.vectors is not None:
                    _, sign = _product_sign(val.vectors, signature)
                blades[bitmask] = BasisBlade(bitmask, val.ascii, val.unicode, val.latex, sign or 1)
            else:
                a, u, lx = _parse_name_value(val)
                blades[bitmask] = BasisBlade(bitmask, a, u, lx)

    return blades


@dataclass
class NamedBlade:
    """A blade name with an optional sign or vector ordering for sign computation."""

    ascii: str
    unicode: str
    latex: str
    sign: int | None = None
    vectors: list | None = None


def _named_blade(name_val, vectors: list) -> NamedBlade:
    """Create a NamedBlade with vector indices for automatic sign computation."""
    a, u, lx = _parse_name_value(name_val)
    return NamedBlade(a, u, lx, vectors=vectors)


def _reorder_sign(indices: list[int]) -> int:
    """Sign from sorting a list of basis vector indices into canonical order.

    Counts the number of adjacent swaps needed (bubble sort parity).
    """
    n = len(indices)
    lst = list(indices)
    swaps = 0
    for i in range(n):
        for j in range(i + 1, n):
            if lst[i] > lst[j]:
                swaps += 1
    return (-1) ** swaps


def _product_sign(indices: list[int], signature: tuple) -> tuple[int, int]:
    """Compute the bitmask and sign of a product of basis vectors.

    Handles repeated indices (contraction via metric) and reordering.
    Returns (bitmask, sign).
    """
    sign = 1
    bitmask = 0
    for idx in indices:
        bit = 1 << idx
        if bitmask & bit:
            # Repeated index: contract via metric
            above = 0
            for k in range(idx + 1, len(signature)):
                if bitmask & (1 << k):
                    above += 1
            sign *= (-1) ** above * signature[idx]
            bitmask ^= bit
        else:
            # New index: count swaps to insert in order
            above = 0
            for k in range(idx + 1, len(signature)):
                if bitmask & (1 << k):
                    above += 1
            sign *= (-1) ** above
            bitmask |= bit
    return bitmask, sign


# ── Factory functions ──


def b_default(
    *,
    prefix: str = "e",
    start: int = 1,
    style: str = "compact",
    overrides: dict[str, str | tuple] | None = None,
) -> BladeConvention:
    """Default: e₁, e₂, … (1-based, compact)."""
    return BladeConvention(
        prefix=prefix,
        index_base=start,
        style=style,
        overrides=overrides,
    )


def b_gamma(
    *,
    start: int = 0,
    style: str = "juxtapose",
    overrides: dict[str, str | tuple] | None = None,
) -> BladeConvention:
    """Gamma: γ₀, γ₁, … (0-based, juxtapose)."""
    return BladeConvention(
        prefix="γ",
        index_base=start,
        style=style,
        overrides=overrides,
    )


def b_sigma(
    *,
    start: int = 1,
    style: str = "juxtapose",
    overrides: dict[str, str | tuple] | None = None,
) -> BladeConvention:
    """Sigma: σ₁, σ₂, … (1-based, juxtapose)."""
    return BladeConvention(
        prefix="σ",
        index_base=start,
        style=style,
        overrides=overrides,
    )


def b_sigma_xyz(
    *,
    style: str = "juxtapose",
    overrides: dict[str, str | tuple] | None = None,
) -> BladeConvention:
    """Sigma xyz: σₓ, σᵧ, σ_z."""
    _LETTER_SUBS = {"x": "ₓ", "y": "ᵧ"}
    letters = "xyzwvu"
    # Store as a callable that generates names for n dimensions
    names = [(c, f"σ{_LETTER_SUBS.get(c, c)}", f"\\sigma_{c}") for c in letters]
    return BladeConvention(
        vector_names=names,
        style=style,
        overrides=overrides,
    )


def b_pga(
    *,
    style: str = "compact",
    pseudoscalar: str | tuple | None = "I",
    overrides: dict[str, str | tuple] | None = None,
) -> BladeConvention:
    """PGA: e₀, e₁, … (0-based, compact, PSS → I)."""
    merged = {}
    if pseudoscalar is not None:
        merged["pss"] = pseudoscalar
    if overrides:
        merged.update(overrides)
    return BladeConvention(
        prefix="e",
        index_base=0,
        style=style,
        overrides=merged or None,
    )


def b_sta(
    *,
    style: str = "juxtapose",
    sigmas: bool = False,
    pseudovectors: bool = False,
    overrides: dict[str, str | tuple] | None = None,
) -> BladeConvention:
    """STA: γ₀…γ₃, PSS → i.

    Works with both Cl(1,3) and Cl(3,1). Signs are computed automatically
    from the metric so that σₖ = γₖγ₀ and iγₖ = I·γₖ display correctly.

    sigmas=True names the six grade-2 bivectors (σₖ and iσₖ).
    pseudovectors=True names the four grade-3 trivectors (iγₖ).
    """
    # σₖ = γₖγ₀: vector indices [k, 0]
    # iσₖ = I·γₖ·γ₀: vector indices [0,1,2,3, k, 0]
    # iγₖ = I·γₖ: vector indices [0,1,2,3, k]
    I_vecs = [0, 1, 2, 3]

    merged = {"pss": ("i", "i", "i")}
    if sigmas:
        merged[(0, 1)] = _named_blade(("s1", "σ₁", r"\sigma_{1}"), [1, 0])
        merged[(0, 2)] = _named_blade(("s2", "σ₂", r"\sigma_{2}"), [2, 0])
        merged[(0, 3)] = _named_blade(("s3", "σ₃", r"\sigma_{3}"), [3, 0])
        merged[(2, 3)] = _named_blade(("is1", "iσ₁", r"i\sigma_{1}"), I_vecs + [1, 0])
        merged[(1, 3)] = _named_blade(("is2", "iσ₂", r"i\sigma_{2}"), I_vecs + [2, 0])
        merged[(1, 2)] = _named_blade(("is3", "iσ₃", r"i\sigma_{3}"), I_vecs + [3, 0])
    if pseudovectors:
        merged[(1, 2, 3)] = _named_blade(("iy0", "iγ₀", r"i\gamma_{0}"), I_vecs + [0])
        merged[(0, 2, 3)] = _named_blade(("iy1", "iγ₁", r"i\gamma_{1}"), I_vecs + [1])
        merged[(0, 1, 3)] = _named_blade(("iy2", "iγ₂", r"i\gamma_{2}"), I_vecs + [2])
        merged[(0, 1, 2)] = _named_blade(("iy3", "iγ₃", r"i\gamma_{3}"), I_vecs + [3])
    if overrides:
        merged.update(overrides)
    return BladeConvention(
        prefix="γ",
        index_base=0,
        style=style,
        overrides=merged,
    )


def b_cga(
    *,
    euclidean: int = 3,
    null_basis: str = "origin_infinity",
    style: str = "compact",
    pseudoscalar: str | tuple | None = "I",
    overrides: dict[str, str | tuple] | None = None,
) -> BladeConvention:
    """CGA: e₁…eₙ, eₒ, e∞ (compact, PSS → I)."""
    # Euclidean vectors + two special vectors
    names = []
    for i in range(1, euclidean + 1):
        s = str(i)
        names.append((f"e{s}", f"e{s.translate(_SUBS)}", f"e_{{{s}}}"))
    if null_basis == "origin_infinity":
        names.append(("eo", "eₒ", r"e_{o}"))
        names.append(("ei", "e∞", r"e_{\infty}"))
    elif null_basis == "plus_minus":
        names.append(("ep", "e₊", r"e_{+}"))
        names.append(("em", "e₋", r"e_{-}"))
    else:
        raise ValueError(f"Unknown null_basis: {null_basis!r}")

    merged = {}
    if pseudoscalar is not None:
        merged["pss"] = pseudoscalar
    # Null pair override: last positive ∧ the negative
    merged[f"+{euclidean + 1}-1"] = ("E0", "E₀", "E_{0}")
    if overrides:
        merged.update(overrides)

    return BladeConvention(
        vector_names=names,
        style=style,
        overrides=merged,
    )
