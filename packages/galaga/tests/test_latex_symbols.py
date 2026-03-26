"""Tests for LaTeX → Unicode/ASCII symbol mapping."""

import pytest
from ga.latex_symbols import LatexSymbols


@pytest.fixture
def sym():
    return LatexSymbols()


class TestGreekLowercase:
    def test_alpha(self, sym):
        assert sym.unicode(r"\alpha") == "α"
        assert sym.ascii(r"\alpha") == "alpha"

    def test_beta(self, sym):
        assert sym.unicode(r"\beta") == "β"
        assert sym.ascii(r"\beta") == "beta"

    def test_gamma(self, sym):
        assert sym.unicode(r"\gamma") == "γ"
        assert sym.ascii(r"\gamma") == "gamma"

    def test_delta(self, sym):
        assert sym.unicode(r"\delta") == "δ"
        assert sym.ascii(r"\delta") == "delta"

    def test_epsilon(self, sym):
        assert sym.unicode(r"\epsilon") == "ϵ"
        assert sym.ascii(r"\epsilon") == "epsilon"

    def test_varepsilon(self, sym):
        assert sym.unicode(r"\varepsilon") == "ε"
        assert sym.ascii(r"\varepsilon") == "varepsilon"

    def test_zeta(self, sym):
        assert sym.unicode(r"\zeta") == "ζ"
        assert sym.ascii(r"\zeta") == "zeta"

    def test_eta(self, sym):
        assert sym.unicode(r"\eta") == "η"
        assert sym.ascii(r"\eta") == "eta"

    def test_theta(self, sym):
        assert sym.unicode(r"\theta") == "θ"
        assert sym.ascii(r"\theta") == "theta"

    def test_vartheta(self, sym):
        assert sym.unicode(r"\vartheta") == "ϑ"
        assert sym.ascii(r"\vartheta") == "vartheta"

    def test_iota(self, sym):
        assert sym.unicode(r"\iota") == "ι"
        assert sym.ascii(r"\iota") == "iota"

    def test_kappa(self, sym):
        assert sym.unicode(r"\kappa") == "κ"
        assert sym.ascii(r"\kappa") == "kappa"

    def test_lambda(self, sym):
        assert sym.unicode(r"\lambda") == "λ"
        assert sym.ascii(r"\lambda") == "lambda_"

    def test_mu(self, sym):
        assert sym.unicode(r"\mu") == "μ"
        assert sym.ascii(r"\mu") == "mu"

    def test_nu(self, sym):
        assert sym.unicode(r"\nu") == "ν"
        assert sym.ascii(r"\nu") == "nu"

    def test_xi(self, sym):
        assert sym.unicode(r"\xi") == "ξ"
        assert sym.ascii(r"\xi") == "xi"

    def test_pi(self, sym):
        assert sym.unicode(r"\pi") == "π"
        assert sym.ascii(r"\pi") == "pi"

    def test_varpi(self, sym):
        assert sym.unicode(r"\varpi") == "ϖ"
        assert sym.ascii(r"\varpi") == "varpi"

    def test_rho(self, sym):
        assert sym.unicode(r"\rho") == "ρ"
        assert sym.ascii(r"\rho") == "rho"

    def test_varrho(self, sym):
        assert sym.unicode(r"\varrho") == "ϱ"
        assert sym.ascii(r"\varrho") == "varrho"

    def test_sigma(self, sym):
        assert sym.unicode(r"\sigma") == "σ"
        assert sym.ascii(r"\sigma") == "sigma"

    def test_varsigma(self, sym):
        assert sym.unicode(r"\varsigma") == "ς"
        assert sym.ascii(r"\varsigma") == "varsigma"

    def test_tau(self, sym):
        assert sym.unicode(r"\tau") == "τ"
        assert sym.ascii(r"\tau") == "tau"

    def test_upsilon(self, sym):
        assert sym.unicode(r"\upsilon") == "υ"
        assert sym.ascii(r"\upsilon") == "upsilon"

    def test_phi(self, sym):
        assert sym.unicode(r"\phi") == "ϕ"
        assert sym.ascii(r"\phi") == "phi"

    def test_varphi(self, sym):
        assert sym.unicode(r"\varphi") == "φ"
        assert sym.ascii(r"\varphi") == "varphi"

    def test_chi(self, sym):
        assert sym.unicode(r"\chi") == "χ"
        assert sym.ascii(r"\chi") == "chi"

    def test_psi(self, sym):
        assert sym.unicode(r"\psi") == "ψ"
        assert sym.ascii(r"\psi") == "psi"

    def test_omega(self, sym):
        assert sym.unicode(r"\omega") == "ω"
        assert sym.ascii(r"\omega") == "omega"


class TestGreekUppercase:
    def test_Gamma(self, sym):
        assert sym.unicode(r"\Gamma") == "Γ"
        assert sym.ascii(r"\Gamma") == "Gamma"

    def test_Delta(self, sym):
        assert sym.unicode(r"\Delta") == "Δ"
        assert sym.ascii(r"\Delta") == "Delta"

    def test_Theta(self, sym):
        assert sym.unicode(r"\Theta") == "Θ"
        assert sym.ascii(r"\Theta") == "Theta"

    def test_Lambda(self, sym):
        assert sym.unicode(r"\Lambda") == "Λ"
        assert sym.ascii(r"\Lambda") == "Lambda"

    def test_Xi(self, sym):
        assert sym.unicode(r"\Xi") == "Ξ"
        assert sym.ascii(r"\Xi") == "Xi"

    def test_Pi(self, sym):
        assert sym.unicode(r"\Pi") == "Π"
        assert sym.ascii(r"\Pi") == "Pi"

    def test_Sigma(self, sym):
        assert sym.unicode(r"\Sigma") == "Σ"
        assert sym.ascii(r"\Sigma") == "Sigma"

    def test_Upsilon(self, sym):
        assert sym.unicode(r"\Upsilon") == "Υ"
        assert sym.ascii(r"\Upsilon") == "Upsilon"

    def test_Phi(self, sym):
        assert sym.unicode(r"\Phi") == "Φ"
        assert sym.ascii(r"\Phi") == "Phi"

    def test_Psi(self, sym):
        assert sym.unicode(r"\Psi") == "Ψ"
        assert sym.ascii(r"\Psi") == "Psi"

    def test_Omega(self, sym):
        assert sym.unicode(r"\Omega") == "Ω"
        assert sym.ascii(r"\Omega") == "Omega"


class TestMathFonts:
    def test_mathbf_A(self, sym):
        assert sym.unicode(r"\mathbf{A}") == "𝐀"
        assert sym.ascii(r"\mathbf{A}") == "A"

    def test_mathbf_z(self, sym):
        assert sym.unicode(r"\mathbf{z}") == "𝐳"
        assert sym.ascii(r"\mathbf{z}") == "z"

    def test_mathit_A(self, sym):
        assert sym.unicode(r"\mathit{A}") == "𝐴"
        assert sym.ascii(r"\mathit{A}") == "A"

    def test_mathit_z(self, sym):
        assert sym.unicode(r"\mathit{z}") == "𝑧"
        assert sym.ascii(r"\mathit{z}") == "z"

    def test_mathcal_A(self, sym):
        assert sym.unicode(r"\mathcal{A}") == "𝒜"
        assert sym.ascii(r"\mathcal{A}") == "A"

    def test_mathcal_Z(self, sym):
        assert sym.unicode(r"\mathcal{Z}") == "𝒵"
        assert sym.ascii(r"\mathcal{Z}") == "Z"

    def test_mathfrak_A(self, sym):
        assert sym.unicode(r"\mathfrak{A}") == "𝔄"
        assert sym.ascii(r"\mathfrak{A}") == "A"

    def test_mathfrak_g(self, sym):
        assert sym.unicode(r"\mathfrak{g}") == "𝔤"
        assert sym.ascii(r"\mathfrak{g}") == "g"

    def test_mathfrak_z(self, sym):
        assert sym.unicode(r"\mathfrak{z}") == "𝔷"
        assert sym.ascii(r"\mathfrak{z}") == "z"

    def test_mathbb_A(self, sym):
        assert sym.unicode(r"\mathbb{A}") == "𝔸"
        assert sym.ascii(r"\mathbb{A}") == "A"

    def test_mathbb_R(self, sym):
        assert sym.unicode(r"\mathbb{R}") == "ℝ"
        assert sym.ascii(r"\mathbb{R}") == "R"

    def test_mathbb_Z(self, sym):
        assert sym.unicode(r"\mathbb{Z}") == "ℤ"
        assert sym.ascii(r"\mathbb{Z}") == "Z"

    def test_mathbb_N(self, sym):
        assert sym.unicode(r"\mathbb{N}") == "ℕ"
        assert sym.ascii(r"\mathbb{N}") == "N"

    def test_mathbb_Q(self, sym):
        assert sym.unicode(r"\mathbb{Q}") == "ℚ"
        assert sym.ascii(r"\mathbb{Q}") == "Q"

    def test_mathbb_C(self, sym):
        assert sym.unicode(r"\mathbb{C}") == "ℂ"
        assert sym.ascii(r"\mathbb{C}") == "C"

    def test_mathbb_H(self, sym):
        assert sym.unicode(r"\mathbb{H}") == "ℍ"
        assert sym.ascii(r"\mathbb{H}") == "H"

    def test_mathbb_P(self, sym):
        assert sym.unicode(r"\mathbb{P}") == "ℙ"
        assert sym.ascii(r"\mathbb{P}") == "P"


class TestCommonSymbols:
    def test_hbar(self, sym):
        assert sym.unicode(r"\hbar") == "ℏ"
        assert sym.ascii(r"\hbar") == "hbar"

    def test_ell(self, sym):
        assert sym.unicode(r"\ell") == "ℓ"
        assert sym.ascii(r"\ell") == "ell"

    def test_nabla(self, sym):
        assert sym.unicode(r"\nabla") == "∇"
        assert sym.ascii(r"\nabla") == "nabla"

    def test_partial(self, sym):
        assert sym.unicode(r"\partial") == "∂"
        assert sym.ascii(r"\partial") == "partial"

    def test_infty(self, sym):
        assert sym.unicode(r"\infty") == "∞"
        assert sym.ascii(r"\infty") == "infty"

    def test_forall(self, sym):
        assert sym.unicode(r"\forall") == "∀"
        assert sym.ascii(r"\forall") == "forall"

    def test_exists(self, sym):
        assert sym.unicode(r"\exists") == "∃"
        assert sym.ascii(r"\exists") == "exists"

    def test_emptyset(self, sym):
        assert sym.unicode(r"\emptyset") == "∅"
        assert sym.ascii(r"\emptyset") == "emptyset"

    def test_aleph(self, sym):
        assert sym.unicode(r"\aleph") == "ℵ"
        assert sym.ascii(r"\aleph") == "aleph"

    def test_wp(self, sym):
        assert sym.unicode(r"\wp") == "℘"
        assert sym.ascii(r"\wp") == "wp"

    def test_Re(self, sym):
        assert sym.unicode(r"\Re") == "ℜ"
        assert sym.ascii(r"\Re") == "Re"

    def test_Im(self, sym):
        assert sym.unicode(r"\Im") == "ℑ"
        assert sym.ascii(r"\Im") == "Im"


class TestOperators:
    def test_cdot(self, sym):
        assert sym.unicode(r"\cdot") == "·"
        assert sym.ascii(r"\cdot") == "."

    def test_times(self, sym):
        assert sym.unicode(r"\times") == "×"
        assert sym.ascii(r"\times") == "x"

    def test_wedge(self, sym):
        assert sym.unicode(r"\wedge") == "∧"
        assert sym.ascii(r"\wedge") == "^"

    def test_vee(self, sym):
        assert sym.unicode(r"\vee") == "∨"
        assert sym.ascii(r"\vee") == "v"

    def test_star(self, sym):
        assert sym.unicode(r"\star") == "⋆"
        assert sym.ascii(r"\star") == "*"

    def test_dagger(self, sym):
        assert sym.unicode(r"\dagger") == "†"
        assert sym.ascii(r"\dagger") == "dag"

    def test_pm(self, sym):
        assert sym.unicode(r"\pm") == "±"
        assert sym.ascii(r"\pm") == "+/-"

    def test_mp(self, sym):
        assert sym.unicode(r"\mp") == "∓"
        assert sym.ascii(r"\mp") == "-/+"

    def test_circ(self, sym):
        assert sym.unicode(r"\circ") == "∘"
        assert sym.ascii(r"\circ") == "o"

    def test_otimes(self, sym):
        assert sym.unicode(r"\otimes") == "⊗"
        assert sym.ascii(r"\otimes") == "(x)"

    def test_oplus(self, sym):
        assert sym.unicode(r"\oplus") == "⊕"
        assert sym.ascii(r"\oplus") == "(+)"


class TestRelations:
    def test_leq(self, sym):
        assert sym.unicode(r"\leq") == "≤"
        assert sym.ascii(r"\leq") == "<="

    def test_geq(self, sym):
        assert sym.unicode(r"\geq") == "≥"
        assert sym.ascii(r"\geq") == ">="

    def test_neq(self, sym):
        assert sym.unicode(r"\neq") == "≠"
        assert sym.ascii(r"\neq") == "!="

    def test_approx(self, sym):
        assert sym.unicode(r"\approx") == "≈"
        assert sym.ascii(r"\approx") == "~="

    def test_equiv(self, sym):
        assert sym.unicode(r"\equiv") == "≡"
        assert sym.ascii(r"\equiv") == "==="

    def test_sim(self, sym):
        assert sym.unicode(r"\sim") == "∼"
        assert sym.ascii(r"\sim") == "~"

    def test_propto(self, sym):
        assert sym.unicode(r"\propto") == "∝"
        assert sym.ascii(r"\propto") == "propto"

    def test_in_(self, sym):
        assert sym.unicode(r"\in") == "∈"
        assert sym.ascii(r"\in") == "in"

    def test_subset(self, sym):
        assert sym.unicode(r"\subset") == "⊂"
        assert sym.ascii(r"\subset") == "subset"

    def test_supset(self, sym):
        assert sym.unicode(r"\supset") == "⊃"
        assert sym.ascii(r"\supset") == "supset"


class TestArrows:
    def test_to(self, sym):
        assert sym.unicode(r"\to") == "→"
        assert sym.ascii(r"\to") == "->"

    def test_leftarrow(self, sym):
        assert sym.unicode(r"\leftarrow") == "←"
        assert sym.ascii(r"\leftarrow") == "<-"

    def test_Rightarrow(self, sym):
        assert sym.unicode(r"\Rightarrow") == "⇒"
        assert sym.ascii(r"\Rightarrow") == "=>"

    def test_Leftarrow(self, sym):
        assert sym.unicode(r"\Leftarrow") == "⇐"
        assert sym.ascii(r"\Leftarrow") == "<="

    def test_leftrightarrow(self, sym):
        assert sym.unicode(r"\leftrightarrow") == "↔"
        assert sym.ascii(r"\leftrightarrow") == "<->"

    def test_mapsto(self, sym):
        assert sym.unicode(r"\mapsto") == "↦"
        assert sym.ascii(r"\mapsto") == "|->"


class TestUnknown:
    def test_unknown_returns_none(self, sym):
        assert sym.unicode(r"\bogus") is None
        assert sym.ascii(r"\bogus") is None

    def test_plain_letter(self, sym):
        assert sym.unicode("x") is None
        assert sym.ascii("x") is None

    def test_lookup(self, sym):
        u, a = sym.lookup(r"\phi")
        assert u == "ϕ"
        assert a == "phi"

    def test_lookup_unknown(self, sym):
        assert sym.lookup(r"\bogus") is None

    def test_lookup_mathbf(self, sym):
        u, a = sym.lookup(r"\mathbf{v}")
        assert u == "𝐯"
        assert a == "v"


class TestAccents:
    def test_hat(self, sym):
        assert sym.unicode(r"\hat{a}") == "a\u0302"
        assert sym.ascii(r"\hat{a}") == "hat_a"

    def test_tilde(self, sym):
        assert sym.unicode(r"\tilde{R}") == "R\u0303"
        assert sym.ascii(r"\tilde{R}") == "tilde_R"

    def test_bar(self, sym):
        assert sym.unicode(r"\bar{x}") == "x\u0304"
        assert sym.ascii(r"\bar{x}") == "bar_x"

    def test_vec(self, sym):
        assert sym.unicode(r"\vec{v}") == "v\u20D7"
        assert sym.ascii(r"\vec{v}") == "vec_v"

    def test_dot(self, sym):
        assert sym.unicode(r"\dot{q}") == "q\u0307"
        assert sym.ascii(r"\dot{q}") == "dot_q"

    def test_ddot(self, sym):
        assert sym.unicode(r"\ddot{x}") == "x\u0308"
        assert sym.ascii(r"\ddot{x}") == "ddot_x"

    def test_hat_in_name(self):
        from ga import Algebra
        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors()
        n = e1.name(latex=r"\hat{n}")
        assert "n" in str(n)
        assert n._name == "hat_n"
