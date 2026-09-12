"""Public blade contracts retaining all 102 historical method identities.

Names beginning with b_* identify their archived v1 responsibility, not APIs
used here. ADR-104 records deliberate changes to lookup, factories and mutation.
"""

from dataclasses import FrozenInstanceError, replace

import numpy as np
import pytest

from galaga import (
    Algebra,
    BladeConvention,
    BladeLabel,
    BladeRef,
    Name,
    default_blade_convention,
    indexed_blade_convention,
    null_cga_blade_convention,
    orthogonal_cga_blade_convention,
    p_cga,
    p_pga,
    p_sta,
    pga_blade_convention,
    spacetime_blade_convention,
)
from galaga import (
    geometric_product as gp,
)

GAMMA = Name("g", "γ", r"\gamma")
SIGMA = Name("s", "σ", r"\sigma")
XYZ = (Name("x", "ₓ", "x"), Name("y", "ᵧ", "y"), Name("z"))


def replace_labels(convention, names):
    """Replace explicit immutable labels; preserve roles and signed references."""
    return BladeConvention(
        convention.dimension,
        [replace(label, name=names.get(label.ref.mask, label.name)) for label in convention.labels],
        aliases=convention.aliases,
        roles=convention.roles,
    )


class TestFactoryDefaults:
    def test_b_default_compact(self):
        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        assert str(e1 ^ e2) == "e₁₂"
        assert str(e1 ^ e2 ^ e3) == "e₁₂₃"

    def test_b_default_latex(self):
        alg = Algebra(3)
        e1, e2, _ = alg.basis_vectors()
        assert "e_{12}" in (e1 ^ e2).latex()

    def test_b_gamma(self):
        alg = Algebra(
            1,
            3,
            blades=indexed_blade_convention(
                4,
                prefix=GAMMA,
                start=0,
                style="juxtapose",
            ),
        )
        g0, g1, _, _ = alg.basis_vectors()
        assert str(g0) == "γ₀"
        assert str(g1) == "γ₁"
        assert str(g0 * g1) == "γ₀γ₁"

    def test_b_sigma(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, prefix=SIGMA, style="juxtapose"))
        s1, s2, _ = alg.basis_vectors()
        assert str(s1) == "σ₁"
        assert str(s2) == "σ₂"

    def test_b_sigma_xyz(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, prefix=SIGMA, subscripts=XYZ, style="juxtapose"))
        sx, sy, sz = alg.basis_vectors()
        assert str(sx) == "σₓ"
        assert str(sy) == "σᵧ"

    def test_b_pga(self):
        alg = Algebra(3, 0, 1, blades=indexed_blade_convention(4, start=0, overrides={15: "I"}))
        e0, e1, e2, e3 = alg.basis_vectors()
        assert str(e0) == "e₀"
        assert str(e0 ^ e1) == "e₀₁"
        assert str(alg.pseudoscalar()) == "I"

    def test_b_sta_basic(self):
        alg = Algebra(signature=(1, -1, -1, -1), blades=spacetime_blade_convention(signature=(1, -1, -1, -1)))
        g0, _, _, _ = alg.basis_vectors()
        assert str(g0) == "γ₀"
        assert str(alg.pseudoscalar()) == "i"

    def test_b_sta_sigmas(self):
        alg = Algebra(
            signature=(1, -1, -1, -1), blades=spacetime_blade_convention(signature=(1, -1, -1, -1), sigmas=True)
        )
        g0, g1, g2, g3 = alg.basis_vectors()
        # Canonical STA convention: σₖ = γₖγ₀
        assert str(g1 * g0) == "σ₁"
        assert str(g0 * g1) == "-σ₁"
        # iσ₃ = I·σ₃ = -γ₁γ₂, so γ₁γ₂ = -iσ₃
        assert str(g1 * g2) == "-iσ₃"

    def test_b_sta_pseudovectors(self):
        alg = Algebra(
            signature=(1, -1, -1, -1), blades=spacetime_blade_convention(signature=(1, -1, -1, -1), pseudovectors=True)
        )
        g0, g1, g2, g3 = alg.basis_vectors()
        trivec = g1 * g2 * g3
        assert str(trivec) == "-iγ₀"

    def test_b_sta_all_blades_plain(self):
        alg = Algebra(signature=(1, -1, -1, -1), blades=spacetime_blade_convention(signature=(1, -1, -1, -1)))
        names = {i: alg.blade_label(i).name.unicode for i in range(16)}
        assert names == {
            0b0000: "1",
            0b0001: "γ₀",
            0b0010: "γ₁",
            0b0011: "γ₀γ₁",
            0b0100: "γ₂",
            0b0101: "γ₀γ₂",
            0b0110: "γ₁γ₂",
            0b0111: "γ₀γ₁γ₂",
            0b1000: "γ₃",
            0b1001: "γ₀γ₃",
            0b1010: "γ₁γ₃",
            0b1011: "γ₀γ₁γ₃",
            0b1100: "γ₂γ₃",
            0b1101: "γ₀γ₂γ₃",
            0b1110: "γ₁γ₂γ₃",
            0b1111: "i",
        }

    def test_b_sta_all_blades_sigmas(self):
        alg = Algebra(
            signature=(1, -1, -1, -1), blades=spacetime_blade_convention(signature=(1, -1, -1, -1), sigmas=True)
        )
        names = {i: alg.blade_label(i).name.unicode for i in range(16)}
        signs = {i: alg.blade_label(i).ref.orientation for i in range(16)}
        assert names == {
            0b0000: "1",
            0b0001: "γ₀",
            0b0010: "γ₁",
            0b0011: "σ₁",
            0b0100: "γ₂",
            0b0101: "σ₂",
            0b0110: "iσ₃",
            0b0111: "γ₀γ₁γ₂",
            0b1000: "γ₃",
            0b1001: "σ₃",
            0b1010: "iσ₂",
            0b1011: "γ₀γ₁γ₃",
            0b1100: "iσ₁",
            0b1101: "γ₀γ₂γ₃",
            0b1110: "γ₁γ₂γ₃",
            0b1111: "i",
        }
        assert signs == {
            0b0000: 1,
            0b0001: 1,
            0b0010: 1,
            0b0011: -1,  # σ₁ = γ₁γ₀ = -γ₀γ₁
            0b0100: 1,
            0b0101: -1,  # σ₂ = γ₂γ₀ = -γ₀γ₂
            0b0110: -1,  # iσ₃ = -γ₁γ₂
            0b0111: 1,
            0b1000: 1,
            0b1001: -1,  # σ₃ = γ₃γ₀ = -γ₀γ₃
            0b1010: 1,  # iσ₂ = γ₁γ₃
            0b1011: 1,
            0b1100: -1,  # iσ₁ = -γ₂γ₃
            0b1101: 1,
            0b1110: 1,
            0b1111: 1,
        }
        # Verify rendered products (σₖ = γₖγ₀, i = γ₀γ₁γ₂γ₃)
        g0, g1, g2, g3 = alg.basis_vectors()
        assert str(g1 * g0) == "σ₁"
        assert str(g0 * g1) == "-σ₁"
        assert str(g2 * g0) == "σ₂"
        assert str(g3 * g0) == "σ₃"
        assert str(g2 * g3) == "-iσ₁"
        assert str(g1 * g3) == "iσ₂"
        assert str(g1 * g2) == "-iσ₃"

    def test_b_sta_all_blades_pseudovectors(self):
        alg = Algebra(
            signature=(1, -1, -1, -1), blades=spacetime_blade_convention(signature=(1, -1, -1, -1), pseudovectors=True)
        )
        names = {i: alg.blade_label(i).name.unicode for i in range(16)}
        signs = {i: alg.blade_label(i).ref.orientation for i in range(16)}
        assert names == {
            0b0000: "1",
            0b0001: "γ₀",
            0b0010: "γ₁",
            0b0011: "γ₀γ₁",
            0b0100: "γ₂",
            0b0101: "γ₀γ₂",
            0b0110: "γ₁γ₂",
            0b0111: "iγ₃",
            0b1000: "γ₃",
            0b1001: "γ₀γ₃",
            0b1010: "γ₁γ₃",
            0b1011: "iγ₂",
            0b1100: "γ₂γ₃",
            0b1101: "iγ₁",
            0b1110: "iγ₀",
            0b1111: "i",
        }
        assert signs == {
            0b0000: 1,
            0b0001: 1,
            0b0010: 1,
            0b0011: 1,
            0b0100: 1,
            0b0101: 1,
            0b0110: 1,
            0b0111: -1,  # γ₀γ₁γ₂ = -iγ₃
            0b1000: 1,
            0b1001: 1,
            0b1010: 1,
            0b1011: 1,  # γ₀γ₁γ₃ = +iγ₂
            0b1100: 1,
            0b1101: -1,  # γ₀γ₂γ₃ = -iγ₁
            0b1110: -1,  # γ₁γ₂γ₃ = -iγ₀
            0b1111: 1,
        }
        # Verify rendered products
        g0, g1, g2, g3 = alg.basis_vectors()
        assert str(g0 * g1 * g2) == "-iγ₃"
        assert str(g0 * g1 * g3) == "iγ₂"
        assert str(g0 * g2 * g3) == "-iγ₁"
        assert str(g1 * g2 * g3) == "-iγ₀"

    def test_b_sta_all_blades_both(self):
        alg = Algebra(
            signature=(1, -1, -1, -1),
            blades=spacetime_blade_convention(signature=(1, -1, -1, -1), sigmas=True, pseudovectors=True),
        )
        names = {i: alg.blade_label(i).name.unicode for i in range(16)}
        signs = {i: alg.blade_label(i).ref.orientation for i in range(16)}
        assert names == {
            0b0000: "1",
            0b0001: "γ₀",
            0b0010: "γ₁",
            0b0011: "σ₁",
            0b0100: "γ₂",
            0b0101: "σ₂",
            0b0110: "iσ₃",
            0b0111: "iγ₃",
            0b1000: "γ₃",
            0b1001: "σ₃",
            0b1010: "iσ₂",
            0b1011: "iγ₂",
            0b1100: "iσ₁",
            0b1101: "iγ₁",
            0b1110: "iγ₀",
            0b1111: "i",
        }
        assert signs == {
            0b0000: 1,
            0b0001: 1,
            0b0010: 1,
            0b0011: -1,  # σ₁
            0b0100: 1,
            0b0101: -1,  # σ₂
            0b0110: -1,  # iσ₃ = -γ₁γ₂
            0b0111: -1,  # iγ₃
            0b1000: 1,
            0b1001: -1,  # σ₃
            0b1010: 1,  # iσ₂ = γ₁γ₃
            0b1011: 1,  # iγ₂
            0b1100: -1,  # iσ₁ = -γ₂γ₃
            0b1101: -1,  # iγ₁
            0b1110: -1,  # iγ₀
            0b1111: 1,
        }
        # Verify all named products
        g0, g1, g2, g3 = alg.basis_vectors()
        assert str(g1 * g0) == "σ₁"
        assert str(g2 * g0) == "σ₂"
        assert str(g3 * g0) == "σ₃"
        assert str(g2 * g3) == "-iσ₁"
        assert str(g1 * g3) == "iσ₂"
        assert str(g1 * g2) == "-iσ₃"
        assert str(g0 * g1 * g2) == "-iγ₃"
        assert str(g0 * g1 * g3) == "iγ₂"
        assert str(g0 * g2 * g3) == "-iγ₁"
        assert str(g1 * g2 * g3) == "-iγ₀"

    def test_b_cga(self):
        alg = Algebra(config=p_cga(frame="orthogonal"))
        _, _, _, ep, em = alg.basis_vectors()
        assert str(ep) == "e₊" and str(em) == "e₋"
        assert ep * ep == alg.scalar(alg.basis_squares[3])
        assert em * em == alg.scalar(alg.basis_squares[4])
        assert alg.locals()["ep"] == ep and alg.locals()["em"] == em
        assert str(alg.I) == "I"
        custom = alg.with_blades(replace_labels(alg.presentation.blades, {31: Name("I")}))
        assert str(custom.I) == "I"
        assert custom.numeric is alg.numeric

    def test_b_cga_origin_infinity_is_explicit_display_only(self):
        # Labels alone never change an orthogonal metric into a native-null frame.
        alg = Algebra(config=p_cga(frame="orthogonal"))
        renamed = alg.with_blades(null_cga_blade_convention(3, basis_order="euclidean-first"))
        np.testing.assert_array_equal(renamed.gram, alg.gram)
        _, _, _, eo, einf = renamed.basis_vectors()
        assert str(eo) == "eₒ" and str(einf) == "e∞"
        assert eo * eo == renamed.scalar(alg.basis_squares[3])
        assert einf * einf == renamed.scalar(alg.basis_squares[4])
        native = Algebra(config=p_cga(frame="null"))
        origin, _, _, _, infinity = native.basis_vectors()
        assert origin * origin == infinity * infinity == native.scalar(0)
        assert origin | infinity == native.scalar(native.gram[0, 4])
        assert native.gram[0, 4] != 0

    def test_b_cga_null_vectors_are_derived_from_default_frame(self):
        alg = Algebra(4, 1, blades=replace_labels(orthogonal_cga_blade_convention(3), {31: Name("I")}))
        _, _, _, ep, em = alg.basis_vectors()
        e4 = (em - ep) / 2
        e5 = em + ep
        assert gp(e4, e4) == alg.scalar(0)
        assert gp(e5, e5) == alg.scalar(0)
        expected_pairing = (alg.signature[4] - alg.signature[3]) / 2
        assert e4 | e5 == alg.scalar(expected_pairing)

    def test_b_sta31_basic(self):
        alg = Algebra(signature=(1, 1, 1, -1), blades=spacetime_blade_convention(signature=(1, 1, 1, -1)))
        g0, _, _, _ = alg.basis_vectors()
        assert str(g0) == "γ₀"
        assert str(alg.pseudoscalar()) == "i"

    def test_b_sta31_sigmas(self):
        alg = Algebra(signature=(1, 1, 1, -1), blades=spacetime_blade_convention(signature=(1, 1, 1, -1), sigmas=True))
        g0, g1, g2, g3 = alg.basis_vectors()

        # Canonical convention retained: σₖ = γₖγ₀
        assert str(g1 * g0) == "σ₁"
        assert str(g0 * g1) == "-σ₁"

        # In Cl(3,1), iσ signs differ from Cl(1,3) due to metric
        assert str(g2 * g3) == "iσ₁"
        assert str(g1 * g3) == "-iσ₂"
        assert str(g1 * g2) == "-iσ₃"

    def test_b_sta31_pseudovectors(self):
        alg = Algebra(
            signature=(1, 1, 1, -1), blades=spacetime_blade_convention(signature=(1, 1, 1, -1), pseudovectors=True)
        )
        g0, g1, g2, g3 = alg.basis_vectors()
        trivec = g1 * g2 * g3
        assert str(trivec) == "-iγ₀"

    def test_b_sta31_all_blades_plain(self):
        alg = Algebra(signature=(1, 1, 1, -1), blades=spacetime_blade_convention(signature=(1, 1, 1, -1)))
        names = {i: alg.blade_label(i).name.unicode for i in range(16)}
        assert names == {
            0b0000: "1",
            0b0001: "γ₀",
            0b0010: "γ₁",
            0b0011: "γ₀γ₁",
            0b0100: "γ₂",
            0b0101: "γ₀γ₂",
            0b0110: "γ₁γ₂",
            0b0111: "γ₀γ₁γ₂",
            0b1000: "γ₃",
            0b1001: "γ₀γ₃",
            0b1010: "γ₁γ₃",
            0b1011: "γ₀γ₁γ₃",
            0b1100: "γ₂γ₃",
            0b1101: "γ₀γ₂γ₃",
            0b1110: "γ₁γ₂γ₃",
            0b1111: "i",
        }

    def test_b_sta31_all_blades_sigmas(self):
        alg = Algebra(signature=(1, 1, 1, -1), blades=spacetime_blade_convention(signature=(1, 1, 1, -1), sigmas=True))
        names = {i: alg.blade_label(i).name.unicode for i in range(16)}
        signs = {i: alg.blade_label(i).ref.orientation for i in range(16)}

        assert names == {
            0b0000: "1",
            0b0001: "γ₀",
            0b0010: "γ₁",
            0b0011: "σ₁",
            0b0100: "γ₂",
            0b0101: "σ₂",
            0b0110: "iσ₃",
            0b0111: "γ₀γ₁γ₂",
            0b1000: "γ₃",
            0b1001: "σ₃",
            0b1010: "iσ₂",
            0b1011: "γ₀γ₁γ₃",
            0b1100: "iσ₁",
            0b1101: "γ₀γ₂γ₃",
            0b1110: "γ₁γ₂γ₃",
            0b1111: "i",
        }

        assert signs == {
            0b0000: 1,
            0b0001: 1,
            0b0010: 1,
            0b0011: -1,  # σ₁ = γ₁γ₀ = -γ₀γ₁
            0b0100: 1,
            0b0101: -1,  # σ₂ = γ₂γ₀ = -γ₀γ₂
            0b0110: -1,  # iσ₃ = -γ₁γ₂
            0b0111: 1,
            0b1000: 1,
            0b1001: -1,  # σ₃ = γ₃γ₀ = -γ₀γ₃
            0b1010: -1,  # iσ₂ = -γ₁γ₃
            0b1011: 1,
            0b1100: 1,  # iσ₁ = γ₂γ₃
            0b1101: 1,
            0b1110: 1,
            0b1111: 1,
        }

        g0, g1, g2, g3 = alg.basis_vectors()
        assert str(g1 * g0) == "σ₁"
        assert str(g0 * g1) == "-σ₁"
        assert str(g2 * g0) == "σ₂"
        assert str(g3 * g0) == "σ₃"
        assert str(g2 * g3) == "iσ₁"
        assert str(g1 * g3) == "-iσ₂"
        assert str(g1 * g2) == "-iσ₃"

    def test_b_sta31_all_blades_pseudovectors(self):
        alg = Algebra(
            signature=(1, 1, 1, -1), blades=spacetime_blade_convention(signature=(1, 1, 1, -1), pseudovectors=True)
        )
        names = {i: alg.blade_label(i).name.unicode for i in range(16)}
        signs = {i: alg.blade_label(i).ref.orientation for i in range(16)}

        assert names == {
            0b0000: "1",
            0b0001: "γ₀",
            0b0010: "γ₁",
            0b0011: "γ₀γ₁",
            0b0100: "γ₂",
            0b0101: "γ₀γ₂",
            0b0110: "γ₁γ₂",
            0b0111: "iγ₃",
            0b1000: "γ₃",
            0b1001: "γ₀γ₃",
            0b1010: "γ₁γ₃",
            0b1011: "iγ₂",
            0b1100: "γ₂γ₃",
            0b1101: "iγ₁",
            0b1110: "iγ₀",
            0b1111: "i",
        }

        assert signs == {
            0b0000: 1,
            0b0001: 1,
            0b0010: 1,
            0b0011: 1,
            0b0100: 1,
            0b0101: 1,
            0b0110: 1,
            0b0111: -1,  # iγ₃
            0b1000: 1,
            0b1001: 1,
            0b1010: 1,
            0b1011: -1,  # iγ₂
            0b1100: 1,
            0b1101: 1,  # iγ₁
            0b1110: -1,  # iγ₀
            0b1111: 1,
        }

        g0, g1, g2, g3 = alg.basis_vectors()
        assert str(g0 * g1 * g2) == "-iγ₃"
        assert str(g0 * g1 * g3) == "-iγ₂"
        assert str(g0 * g2 * g3) == "iγ₁"
        assert str(g1 * g2 * g3) == "-iγ₀"

    def test_b_sta31_all_blades_both(self):
        alg = Algebra(
            signature=(1, 1, 1, -1),
            blades=spacetime_blade_convention(signature=(1, 1, 1, -1), sigmas=True, pseudovectors=True),
        )
        names = {i: alg.blade_label(i).name.unicode for i in range(16)}
        signs = {i: alg.blade_label(i).ref.orientation for i in range(16)}

        assert names == {
            0b0000: "1",
            0b0001: "γ₀",
            0b0010: "γ₁",
            0b0011: "σ₁",
            0b0100: "γ₂",
            0b0101: "σ₂",
            0b0110: "iσ₃",
            0b0111: "iγ₃",
            0b1000: "γ₃",
            0b1001: "σ₃",
            0b1010: "iσ₂",
            0b1011: "iγ₂",
            0b1100: "iσ₁",
            0b1101: "iγ₁",
            0b1110: "iγ₀",
            0b1111: "i",
        }

        assert signs == {
            0b0000: 1,
            0b0001: 1,
            0b0010: 1,
            0b0011: -1,  # σ₁
            0b0100: 1,
            0b0101: -1,  # σ₂
            0b0110: -1,  # iσ₃
            0b0111: -1,  # iγ₃
            0b1000: 1,
            0b1001: -1,  # σ₃
            0b1010: -1,  # iσ₂
            0b1011: -1,  # iγ₂
            0b1100: 1,  # iσ₁
            0b1101: 1,  # iγ₁
            0b1110: -1,  # iγ₀
            0b1111: 1,
        }

        g0, g1, g2, g3 = alg.basis_vectors()
        assert str(g1 * g0) == "σ₁"
        assert str(g2 * g0) == "σ₂"
        assert str(g3 * g0) == "σ₃"
        assert str(g2 * g3) == "iσ₁"
        assert str(g1 * g3) == "-iσ₂"
        assert str(g1 * g2) == "-iσ₃"
        assert str(g0 * g1 * g2) == "-iγ₃"
        assert str(g0 * g1 * g3) == "-iγ₂"
        assert str(g0 * g2 * g3) == "iγ₁"
        assert str(g1 * g2 * g3) == "-iγ₀"


class TestStyleVariations:
    def test_compact_unicode(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, style="compact"))
        e1, e2, _ = alg.basis_vectors()
        assert str(e1 ^ e2) == "e₁₂"

    def test_compact_ascii(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, style="compact"))
        e1, e2, _ = alg.basis_vectors()
        assert format(e1 ^ e2, "value/ascii") == "e12"

    def test_compact_latex(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, style="compact"))
        e1, e2, _ = alg.basis_vectors()
        assert "e_{12}" in (e1 ^ e2).latex()

    def test_juxtapose_unicode(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, style="juxtapose"))
        e1, e2, _ = alg.basis_vectors()
        assert str(e1 ^ e2) == "e₁e₂"

    def test_juxtapose_ascii(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, style="juxtapose"))
        e1, e2, _ = alg.basis_vectors()
        assert format(e1 ^ e2, "value/ascii") == "e1e2"

    def test_juxtapose_latex(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, style="juxtapose"))
        e1, e2, _ = alg.basis_vectors()
        assert "e_{1} e_{2}" in (e1 ^ e2).latex()

    def test_wedge_unicode(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, style="wedge"))
        e1, e2, _ = alg.basis_vectors()
        assert "∧" in str(e1 ^ e2)

    def test_wedge_ascii(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, style="wedge"))
        e1, e2, _ = alg.basis_vectors()
        assert "^" in format(e1 ^ e2, "value/ascii")

    def test_wedge_latex(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, style="wedge"))
        e1, e2, _ = alg.basis_vectors()
        assert r"\wedge" in (e1 ^ e2).latex()


class TestOverrides:
    def test_pss_override(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, overrides={7: "I"}))
        assert str(alg.pseudoscalar()) == "I"

    def test_bivector_override(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, overrides={3: "B"}))
        e1, e2, _ = alg.basis_vectors()
        assert str(e1 ^ e2) == "B"

    def test_override_3tuple(self):
        alg = Algebra(
            3,
            blades=indexed_blade_convention(
                3,
                overrides={
                    3: Name("B12", "B₁₂", r"B_{12}"),
                },
            ),
        )
        e1, e2, _ = alg.basis_vectors()
        assert format(e1 ^ e2, "value/ascii") == "B12"
        assert str(e1 ^ e2) == "B₁₂"
        assert "B_{12}" in (e1 ^ e2).latex()

    def test_override_spaces_optional(self):
        # V2 keys are exterior masks; old metric-role text is not a parser.
        for key in ("+1+2", "+1 +2"):
            with pytest.raises(ValueError, match="mask"):
                indexed_blade_convention(3, overrides={key: "X"})
        alg = Algebra(3, blades=indexed_blade_convention(3, overrides={3: "X"}))
        assert str(alg.blade(1) ^ alg.blade(2)) == "X"

    def test_null_vector_override(self):
        # Keep the historical null-first layout explicitly; p_pga is Euclidean-first.
        alg = Algebra(signature=(0, 1, 1, 1), blades=indexed_blade_convention(4, start=0, overrides={15: "I", 3: "L"}))
        e0, e1, _, _ = alg.basis_vectors()
        assert str(e0 ^ e1) == "L"
        assert e0 * e0 == alg.scalar(0)
        assert str(alg.I) == "I"

    def test_factory_overrides_merge(self):
        # Keep the historical null-first layout explicitly; p_pga is Euclidean-first.
        alg = Algebra(signature=(0, 1, 1, 1), blades=indexed_blade_convention(4, start=0, overrides={15: "I", 3: "L"}))
        e0, e1, _, _ = alg.basis_vectors()
        assert str(e0 ^ e1) == "L"
        assert e0 * e0 == alg.scalar(0)
        assert str(alg.I) == "I"

    def test_user_override_wins_on_conflict(self):
        plain = indexed_blade_convention(4, start=0, overrides={15: "I"})
        custom = replace_labels(plain, {15: Name("𝐈")})
        alg = Algebra(signature=(0, 1, 1, 1), blades=custom)
        assert str(alg.I) == "𝐈"
        assert plain.label(15).name == Name("I")


class TestErrors:
    def test_override_nonexistent_vector(self):
        with pytest.raises(ValueError, match="mask"):
            indexed_blade_convention(2, overrides={12: "X"})

    def test_override_invalid_key(self):
        with pytest.raises(ValueError):
            Algebra(3, blades=indexed_blade_convention(3, overrides={"foo": "X"}))

    def test_incompatible_sta_sigmas(self):
        convention = spacetime_blade_convention(signature=(1, -1, -1, -1), sigmas=True)
        with pytest.raises(ValueError, match="dimension"):
            Algebra(3, blades=convention)

    def test_compact_mixed_prefix_fallback(self):
        # Arbitrary vector words are supplied as a complete explicit label table.
        convention = BladeConvention(2, {0: "1", 1: "x", 2: "y", 3: "xy"})
        alg = Algebra((1, 1), blades=convention)
        x, y = alg.basis_vectors()
        assert str(x ^ y) == "xy"

    def test_invalid_blades_type(self):
        with pytest.raises(TypeError):
            Algebra(3, blades="bogus")

    def test_too_few_vector_names(self):
        with pytest.raises(ValueError, match="label"):
            BladeConvention(3, {0: "1", 1: "a"})


class TestBladeLookup:
    def test_metric_role_string(self):
        alg = Algebra(config=p_sta(sigmas=True))
        g0, g1, _, _ = alg.basis_vectors()
        assert alg.blade("time") == g0
        assert alg.blade(BladeRef(3)) == g0 ^ g1
        with pytest.raises(KeyError):
            alg.blade("+1-1")

    def test_display_name_match(self):
        alg = Algebra(config=p_sta(sigmas=True))
        g0, g1, _, _ = alg.basis_vectors()
        # Fix the old test's native-mask lookup: the name means the signed product.
        assert alg.blade("σ₁") == g1 * g0
        assert alg.blade("σ₁") == -(g0 ^ g1)
        assert alg.blade("g0g1") == g0 ^ g1

    def test_pss_shorthand(self):
        plain = indexed_blade_convention(3, aliases={"pss": BladeRef(7)})
        alg = Algebra(3, blades=plain)
        assert alg.blade("pss") == alg.I
        with pytest.raises(KeyError):
            Algebra(3).blade("pss")

    def test_0based_digit_parsing(self):
        pga = Algebra(3, 0, 1, blades=indexed_blade_convention(4, start=0, overrides={15: "I"}))
        e0, e1, _, _ = pga.basis_vectors()
        assert pga.blade("e01") == e0 ^ e1

    def test_1based_digit_parsing(self):
        alg = Algebra(3)
        e1, e2, _ = alg.basis_vectors()
        assert alg.blade("e12") == e1 ^ e2

    def test_invalid_name_raises(self):
        alg = Algebra(3)
        with pytest.raises(KeyError):
            alg.blade("e99")

    def test_nonsense_raises(self):
        alg = Algebra(3)
        with pytest.raises(KeyError):
            alg.blade("nonsense")


class TestGetBasisBlade:
    def test_metric_role_string(self):
        alg = Algebra(config=p_sta())
        ref = alg.presentation.blades.resolve("g0g1")
        assert ref == BladeRef(3)
        assert alg.blade_label(ref.mask) is alg.presentation.blades.label(ref.mask)
        assert alg.blade(ref) == alg.blade(1) ^ alg.blade(2)

    def test_bitmask_int(self):
        alg = Algebra(config=p_sta())
        label = alg.blade_label(3)
        assert label is alg.blade_label(3)
        assert label.ref == BladeRef(3)
        assert alg.blade(label.ref) == alg.blade(alg.blade(1) ^ alg.blade(2))

    def test_pss_string(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, aliases={"pss": 7}))
        ref = alg.presentation.blades.resolve("pss")
        assert alg.blade_label(ref.mask) is alg.blade_label(7)
        assert alg.blade(ref) == alg.I


class TestRename:
    def test_rename_string(self):
        alg = Algebra(3)
        name = Name("B")
        view = alg.with_blades(replace_labels(alg.presentation.blades, {3: name}))
        for target in ("ascii", "unicode", "latex"):
            assert view.blade(3).display(f"value/{target}") == name.for_target(target)
        assert str(alg.blade(3)) == "e₁₂"
        assert view.numeric is alg.numeric
        assert view.blade(3) == alg.blade(3)

    def test_rename_3tuple(self):
        alg = Algebra(3)
        name = Name("B12", "B₁₂", r"B_{12}")
        view = alg.with_blades(replace_labels(alg.presentation.blades, {3: name}))
        for target in ("ascii", "unicode", "latex"):
            assert view.blade(3).display(f"value/{target}") == name.for_target(target)
        assert str(alg.blade(3)) == "e₁₂"
        assert view.numeric is alg.numeric
        assert view.blade(3) == alg.blade(3)

    def test_rename_keyword(self):
        alg = Algebra(3)
        old = alg.blade_label(3).name
        name = replace(old, unicode="X")
        view = alg.with_blades(replace_labels(alg.presentation.blades, {3: name}))
        assert str(view.blade(3)) == "X"
        assert repr(view.blade(3)) == repr(alg.blade(3)) == "e12"
        assert view.blade(3).latex() == alg.blade(3).latex()

    def test_rename_is_live(self):
        alg = Algebra(3)
        mv = alg.blade(1) ^ alg.blade(2)
        view = alg.with_blades(replace_labels(alg.presentation.blades, {3: Name("Z")}))
        assert str(mv) == "e₁₂"
        with alg.use_presentation(view.presentation):
            assert str(mv) == "Z"
        assert str(mv) == "e₁₂"
        assert mv == view.blade(3)


class TestReprUnicode:
    def test_repr_unicode_true(self):
        alg = Algebra(3)
        mv = alg.blade(3)
        assert repr(mv) == "e12"
        assert mv.display("value/unicode") == "e₁₂"
        with pytest.raises(TypeError):
            Algebra(3, repr_unicode=True)

    def test_repr_unicode_false(self):
        alg = Algebra(3)
        e1, e2, _ = alg.basis_vectors()
        r = repr(e1 ^ e2)
        assert "12" in r
        assert "₁₂" not in r

    def test_str_always_unicode(self):
        alg = Algebra(3)
        e1, e2, _ = alg.basis_vectors()
        assert "₁₂" in str(e1 ^ e2)


class TestFactoryKeywords:
    def test_prefix(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, prefix="v"))
        assert str(alg.basis_vectors()[0]) == "v₁"

    def test_start_0(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, start=0))
        assert str(alg.basis_vectors()[0]) == "e₀"

    def test_gamma_start_1(self):
        alg = Algebra(4, blades=indexed_blade_convention(4, prefix=GAMMA, start=1, style="juxtapose"))
        assert str(alg.basis_vectors()[0]) == "γ₁"

    def test_pga_custom_pseudoscalar(self):
        plain = pga_blade_convention(3)
        custom = replace_labels(plain, {(1 << plain.dimension) - 1: Name("𝐈")})
        alg = Algebra(signature=(1, 1, 1, 0), blades=custom)
        assert str(alg.I) == "𝐈"
        assert custom.label(1) == plain.label(1)
        assert alg.blade("projective") ** 2 == alg.scalar(0)

    def test_default_pss(self):
        plain = default_blade_convention(3)
        custom = replace_labels(plain, {(1 << plain.dimension) - 1: Name("I")})
        alg = Algebra(signature=(1, 1, 1), blades=custom)
        assert str(alg.I) == "I"
        assert custom.label(1) == plain.label(1)

    def test_default_pss_none(self):
        alg = Algebra(3, blades=default_blade_convention(3))
        assert str(alg.I) == "e₁₂₃"

    def test_gamma_pss(self):
        plain = indexed_blade_convention(3, prefix=GAMMA, start=0, style="juxtapose")
        custom = replace_labels(plain, {(1 << plain.dimension) - 1: Name("I")})
        alg = Algebra(signature=(1, 1, 1), blades=custom)
        assert str(alg.I) == "I"
        assert custom.label(1) == plain.label(1)

    def test_sigma_pss(self):
        plain = indexed_blade_convention(3, prefix=SIGMA, style="juxtapose")
        custom = replace_labels(plain, {(1 << plain.dimension) - 1: Name("I")})
        alg = Algebra(signature=(1, 1, 1), blades=custom)
        assert str(alg.I) == "I"
        assert custom.label(1) == plain.label(1)

    def test_sigma_xyz_pss(self):
        plain = indexed_blade_convention(3, prefix=SIGMA, subscripts=XYZ, style="juxtapose")
        custom = replace_labels(plain, {(1 << plain.dimension) - 1: Name("ω")})
        alg = Algebra(signature=(1, 1, 1), blades=custom)
        assert str(alg.I) == "ω"
        assert custom.label(1) == plain.label(1)

    def test_sta_pss_override(self):
        plain = spacetime_blade_convention()
        custom = replace_labels(plain, {(1 << plain.dimension) - 1: Name("I")})
        alg = Algebra(signature=(1, -1, -1, -1), blades=custom)
        assert str(alg.I) == "I"
        assert custom.label(1) == plain.label(1)

    def test_sta_pss_default(self):
        alg = Algebra(signature=(1, -1, -1, -1), blades=spacetime_blade_convention(signature=(1, -1, -1, -1)))
        assert str(alg.pseudoscalar()) == "i"

    def test_cga_pss(self):
        plain = orthogonal_cga_blade_convention(3)
        custom = replace_labels(plain, {(1 << plain.dimension) - 1: Name("Ω")})
        alg = Algebra(signature=(1, 1, 1, 1, -1), blades=custom)
        assert str(alg.I) == "Ω"
        assert custom.label(1) == plain.label(1)

    def test_cga_pss_none(self):
        alg = Algebra(config=p_cga(frame="orthogonal"))
        assert str(alg.I) == "I"

    def test_pga_pss_none(self):
        alg = Algebra(config=p_pga(2))
        assert str(alg.I) == "e₁₂₀"

    def test_style_override_on_factory(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, prefix=GAMMA, start=0, style="compact"))
        g0, g1, _ = alg.basis_vectors()
        assert str(g0 ^ g1) == "γ₀₁"


class TestCrossLibrary:
    """Historical spelling examples, not executions of external libraries."""

    def test_clifford_style(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, style="compact"))
        e1, e2, _ = alg.basis_vectors()
        assert str(e1 ^ e2) == "e₁₂"

    def test_ganja_style(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, start=0, style="compact"))
        e0, e1, _ = alg.basis_vectors()
        assert str(e0 ^ e1) == "e₀₁"

    def test_galgebra_style(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, style="wedge"))
        e1, e2, _ = alg.basis_vectors()
        assert "∧" in str(e1 ^ e2)

    def test_julia_style(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, prefix="v", style="compact"))
        v1, v2, _ = alg.basis_vectors()
        assert str(v1 ^ v2) == "v₁₂"


class TestCoverageGaps:
    def test_override_2tuple(self):
        alg = Algebra(
            3,
            blades=indexed_blade_convention(
                3,
                overrides={
                    3: Name("B12", "B₁₂"),
                },
            ),
        )
        e1, e2, _ = alg.basis_vectors()
        assert format(e1 ^ e2, "value/ascii") == "B12"
        assert str(e1 ^ e2) == "B₁₂"
        # latex derived from unicode
        assert "B₁₂" in (e1 ^ e2).latex()

    def test_override_invalid_value_type(self):
        with pytest.raises(ValueError, match="name"):
            indexed_blade_convention(3, overrides={3: 42})
        with pytest.raises(ValueError, match="name"):
            indexed_blade_convention(3, overrides={3: ("B12", "B₁₂")})

    def test_override_negative_out_of_range(self):
        with pytest.raises(ValueError, match="mask"):
            indexed_blade_convention(3, overrides={-1: "X"})

    def test_b_sta_with_user_overrides(self):
        alg = Algebra(config=p_sta())
        custom = replace_labels(alg.presentation.blades, {3: Name("MyBlade")})
        view = alg.with_blades(custom)
        assert str(view.blade(1) * view.blade(2)) == "MyBlade"
        assert str(view.I) == str(alg.I) == "i"
        assert view.numeric is alg.numeric

    def test_b_cga_with_user_overrides(self):
        alg = Algebra(config=p_cga(frame="orthogonal"))
        custom = replace_labels(alg.presentation.blades, {3: Name("MyBlade")})
        view = alg.with_blades(custom)
        assert str(view.blade(1) * view.blade(2)) == "MyBlade"
        assert str(view.I) == str(alg.I) == "I"
        assert view.numeric is alg.numeric

    def test_b_cga_invalid_null_basis(self):
        with pytest.raises(ValueError, match="frame"):
            p_cga(frame="bogus")

    def test_rename_2tuple(self):
        alg = Algebra(3)
        name = Name("B12", "B₁₂")
        view = alg.with_blades(replace_labels(alg.presentation.blades, {3: name}))
        for target in ("ascii", "unicode", "latex"):
            assert view.blade(3).display(f"value/{target}") == name.for_target(target)
        assert str(alg.blade(3)) == "e₁₂"
        assert view.numeric is alg.numeric
        assert view.blade(3) == alg.blade(3)

    def test_rename_invalid_value(self):
        with pytest.raises(ValueError, match="name"):
            Name(42)
        with pytest.raises(TypeError, match="Name"):
            BladeLabel(42, BladeRef(3))

    def test_basis_blade_property_setters(self):
        label = BladeLabel(Name("e12", "e₁₂", "e_{12}"), BladeRef(3))
        for field in ("ascii", "unicode", "latex"):
            with pytest.raises(FrozenInstanceError):
                setattr(label.name, field, "X")
        with pytest.raises(FrozenInstanceError):
            label.name = Name("X")
        for field, value in (("mask", 7), ("orientation", -1)):
            with pytest.raises(FrozenInstanceError):
                setattr(label.ref, field, value)

    def test_basis_blade_repr(self):
        label = BladeLabel(Name("e12", "e₁₂", "e_{12}"), BladeRef(3))
        assert "BladeLabel" in repr(label)
        assert "e12" in repr(label)
        assert "mask=3" in repr(label)

    def test_null_vector_out_of_range(self):
        with pytest.raises(ValueError, match="mask"):
            indexed_blade_convention(3, overrides={8: "X"})
        with pytest.raises(ValueError, match="mask"):
            indexed_blade_convention(3, overrides={"_1": "X"})


class TestSignConsistency:
    @pytest.mark.parametrize("sig", [(1, -1, -1, -1), (-1, 1, 1, 1)])
    @pytest.mark.parametrize("sigmas, pseudovectors", [(True, False), (False, True), (True, True)])
    def test_named_blade_signs_match_products(self, sig, sigmas, pseudovectors):
        alg = Algebra(signature=sig)
        g = alg.basis_vectors()
        products = {}
        if sigmas:
            for index in range(1, 4):
                products[f"s{index}"] = g[index] * g[0]
                products[f"is{index}"] = alg.I * g[index] * g[0]
        if pseudovectors:
            for index in range(4):
                products[f"ig{index}"] = alg.I * g[index]
        convention = spacetime_blade_convention(signature=sig, sigmas=sigmas, pseudovectors=pseudovectors)
        for name, result in products.items():
            mask = np.flatnonzero(result.data).item()
            ref = convention.resolve(name)
            assert ref == BladeRef(mask, int(result.data[mask]))
            assert alg.blade(ref) == result


class TestSubscriptsParameter:
    def test_compact_latex(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, prefix="e", subscripts=["x", "y", "z"]))
        assert alg.blade_label(0b001).name.latex == "e_{x}"
        assert alg.blade_label(0b010).name.latex == "e_{y}"
        assert alg.blade_label(0b011).name.latex == "e_{xy}"
        assert alg.blade_label(0b101).name.latex == "e_{xz}"
        assert alg.blade_label(0b110).name.latex == "e_{yz}"
        assert alg.blade_label(0b111).name.latex == "e_{xyz}"

    def test_compact_ascii(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, prefix="e", subscripts=["x", "y", "z"]))
        assert alg.blade_label(0b001).name.ascii == "ex"
        assert alg.blade_label(0b011).name.ascii == "exy"
        assert alg.blade_label(0b111).name.ascii == "exyz"

    def test_wedge_latex(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, prefix="e", subscripts=["x", "y", "z"], style="wedge"))
        assert alg.blade_label(0b011).name.latex == r"e_{x} \wedge e_{y}"
        assert alg.blade_label(0b101).name.latex == r"e_{x} \wedge e_{z}"

    def test_juxtapose_latex(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, prefix="e", subscripts=["x", "y", "z"], style="juxtapose"))
        assert alg.blade_label(0b011).name.latex == "e_{x} e_{y}"

    def test_gamma_prefix(self):
        alg = Algebra(4, blades=indexed_blade_convention(4, prefix=GAMMA, subscripts=["t", "x", "y", "z"]))
        assert alg.blade_label(0b0001).name.latex == r"\gamma_{t}"
        assert alg.blade_label(0b0011).name.latex == r"\gamma_{tx}"

    def test_pss_override(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, prefix="e", subscripts=["x", "y", "z"], overrides={7: "I"}))
        assert alg.blade_label(0b111).name.ascii == "I"
        assert alg.blade_label(0b111).name.latex == "I"

    def test_subscripts_priority_over_vector_names(self):
        # Ambiguous generator arguments are no longer silently ignored.
        with pytest.raises(TypeError):
            indexed_blade_convention(3, prefix="e", subscripts=["x", "y", "z"], vector_names=["a", "b", "c"])
        alg = Algebra(3, blades=indexed_blade_convention(3, prefix="e", subscripts=["x", "y", "z"]))
        assert alg.blade_label(1).name.latex == "e_{x}"

    def test_too_few_subscripts_raises(self):
        with pytest.raises(ValueError, match="subscripts"):
            Algebra(3, blades=indexed_blade_convention(3, prefix="e", subscripts=["x", "y"]))

    def test_computation_unaffected(self):
        alg = Algebra(3, blades=indexed_blade_convention(3, prefix="e", subscripts=["x", "y", "z"]))
        e = alg.basis_vectors()
        # e_x * e_x = 1 (Euclidean)
        assert e[0] * e[0] == alg.scalar(alg.basis_squares[0])
        # e_x * e_y = -e_y * e_x
        assert np.allclose((e[0] * e[1]).data, -(e[1] * e[0]).data)
