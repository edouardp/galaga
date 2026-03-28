"""Tests for LaTeX → Unicode/ASCII symbol mapping."""

import pytest

from galaga.latex_symbols import LatexSymbols


@pytest.fixture
def sym():
    return LatexSymbols()


class TestGreekLowercase:
    def test_alpha(self, sym):
        """Maps \\alpha to unicode α and ascii 'alpha'."""
        assert sym.unicode(r"\alpha") == "α"
        assert sym.ascii(r"\alpha") == "alpha"

    def test_beta(self, sym):
        """Maps \\beta to unicode and ascii."""
        assert sym.unicode(r"\beta") == "β"
        assert sym.ascii(r"\beta") == "beta"

    def test_gamma(self, sym):
        """Maps \\gamma to unicode and ascii."""
        assert sym.unicode(r"\gamma") == "γ"
        assert sym.ascii(r"\gamma") == "gamma"

    def test_delta(self, sym):
        """Maps \\delta to unicode and ascii."""
        assert sym.unicode(r"\delta") == "δ"
        assert sym.ascii(r"\delta") == "delta"

    def test_epsilon(self, sym):
        """Maps \\epsilon to unicode and ascii."""
        assert sym.unicode(r"\epsilon") == "ϵ"
        assert sym.ascii(r"\epsilon") == "epsilon"

    def test_varepsilon(self, sym):
        """Maps \\varepsilon to unicode and ascii."""
        assert sym.unicode(r"\varepsilon") == "ε"
        assert sym.ascii(r"\varepsilon") == "varepsilon"

    def test_zeta(self, sym):
        """Maps \\zeta to unicode and ascii."""
        assert sym.unicode(r"\zeta") == "ζ"
        assert sym.ascii(r"\zeta") == "zeta"

    def test_eta(self, sym):
        """Maps \\eta to unicode and ascii."""
        assert sym.unicode(r"\eta") == "η"
        assert sym.ascii(r"\eta") == "eta"

    def test_theta(self, sym):
        """Maps \\theta to unicode and ascii."""
        assert sym.unicode(r"\theta") == "θ"
        assert sym.ascii(r"\theta") == "theta"

    def test_vartheta(self, sym):
        """Maps \\vartheta to unicode and ascii."""
        assert sym.unicode(r"\vartheta") == "ϑ"
        assert sym.ascii(r"\vartheta") == "vartheta"

    def test_iota(self, sym):
        """Maps \\iota to unicode and ascii."""
        assert sym.unicode(r"\iota") == "ι"
        assert sym.ascii(r"\iota") == "iota"

    def test_kappa(self, sym):
        """Maps \\kappa to unicode and ascii."""
        assert sym.unicode(r"\kappa") == "κ"
        assert sym.ascii(r"\kappa") == "kappa"

    def test_lambda(self, sym):
        """Maps \\lambda to unicode and ascii."""
        assert sym.unicode(r"\lambda") == "λ"
        assert sym.ascii(r"\lambda") == "lambda_"

    def test_mu(self, sym):
        """Maps \\mu to unicode and ascii."""
        assert sym.unicode(r"\mu") == "μ"
        assert sym.ascii(r"\mu") == "mu"

    def test_nu(self, sym):
        """Maps \\nu to unicode and ascii."""
        assert sym.unicode(r"\nu") == "ν"
        assert sym.ascii(r"\nu") == "nu"

    def test_xi(self, sym):
        """Maps \\xi to unicode and ascii."""
        assert sym.unicode(r"\xi") == "ξ"
        assert sym.ascii(r"\xi") == "xi"

    def test_pi(self, sym):
        """Maps \\pi to unicode and ascii."""
        assert sym.unicode(r"\pi") == "π"
        assert sym.ascii(r"\pi") == "pi"

    def test_varpi(self, sym):
        """Maps \\varpi to unicode and ascii."""
        assert sym.unicode(r"\varpi") == "ϖ"
        assert sym.ascii(r"\varpi") == "varpi"

    def test_rho(self, sym):
        """Maps \\rho to unicode and ascii."""
        assert sym.unicode(r"\rho") == "ρ"
        assert sym.ascii(r"\rho") == "rho"

    def test_varrho(self, sym):
        """Maps \\varrho to unicode and ascii."""
        assert sym.unicode(r"\varrho") == "ϱ"
        assert sym.ascii(r"\varrho") == "varrho"

    def test_sigma(self, sym):
        """Maps \\sigma to unicode and ascii."""
        assert sym.unicode(r"\sigma") == "σ"
        assert sym.ascii(r"\sigma") == "sigma"

    def test_varsigma(self, sym):
        """Maps \\varsigma to unicode and ascii."""
        assert sym.unicode(r"\varsigma") == "ς"
        assert sym.ascii(r"\varsigma") == "varsigma"

    def test_tau(self, sym):
        """Maps \\tau to unicode and ascii."""
        assert sym.unicode(r"\tau") == "τ"
        assert sym.ascii(r"\tau") == "tau"

    def test_upsilon(self, sym):
        """Maps \\upsilon to unicode and ascii."""
        assert sym.unicode(r"\upsilon") == "υ"
        assert sym.ascii(r"\upsilon") == "upsilon"

    def test_phi(self, sym):
        """Maps \\phi to unicode and ascii."""
        assert sym.unicode(r"\phi") == "ϕ"
        assert sym.ascii(r"\phi") == "phi"

    def test_varphi(self, sym):
        """Maps \\varphi to unicode and ascii."""
        assert sym.unicode(r"\varphi") == "φ"
        assert sym.ascii(r"\varphi") == "varphi"

    def test_chi(self, sym):
        """Maps \\chi to unicode and ascii."""
        assert sym.unicode(r"\chi") == "χ"
        assert sym.ascii(r"\chi") == "chi"

    def test_psi(self, sym):
        """Maps \\psi to unicode and ascii."""
        assert sym.unicode(r"\psi") == "ψ"
        assert sym.ascii(r"\psi") == "psi"

    def test_omega(self, sym):
        """Maps \\omega to unicode and ascii."""
        assert sym.unicode(r"\omega") == "ω"
        assert sym.ascii(r"\omega") == "omega"


class TestGreekUppercase:
    def test_Gamma(self, sym):
        """Maps \\Gamma to unicode and ascii."""
        assert sym.unicode(r"\Gamma") == "Γ"
        assert sym.ascii(r"\Gamma") == "Gamma"

    def test_Delta(self, sym):
        """Maps \\Delta to unicode and ascii."""
        assert sym.unicode(r"\Delta") == "Δ"
        assert sym.ascii(r"\Delta") == "Delta"

    def test_Theta(self, sym):
        """Maps \\Theta to unicode and ascii."""
        assert sym.unicode(r"\Theta") == "Θ"
        assert sym.ascii(r"\Theta") == "Theta"

    def test_Lambda(self, sym):
        """Maps \\Lambda to unicode and ascii."""
        assert sym.unicode(r"\Lambda") == "Λ"
        assert sym.ascii(r"\Lambda") == "Lambda"

    def test_Xi(self, sym):
        """Maps \\Xi to unicode and ascii."""
        assert sym.unicode(r"\Xi") == "Ξ"
        assert sym.ascii(r"\Xi") == "Xi"

    def test_Pi(self, sym):
        """Maps \\Pi to unicode and ascii."""
        assert sym.unicode(r"\Pi") == "Π"
        assert sym.ascii(r"\Pi") == "Pi"

    def test_Sigma(self, sym):
        """Maps \\Sigma to unicode and ascii."""
        assert sym.unicode(r"\Sigma") == "Σ"
        assert sym.ascii(r"\Sigma") == "Sigma"

    def test_Upsilon(self, sym):
        """Maps \\Upsilon to unicode and ascii."""
        assert sym.unicode(r"\Upsilon") == "Υ"
        assert sym.ascii(r"\Upsilon") == "Upsilon"

    def test_Phi(self, sym):
        """Maps \\Phi to unicode and ascii."""
        assert sym.unicode(r"\Phi") == "Φ"
        assert sym.ascii(r"\Phi") == "Phi"

    def test_Psi(self, sym):
        """Maps \\Psi to unicode and ascii."""
        assert sym.unicode(r"\Psi") == "Ψ"
        assert sym.ascii(r"\Psi") == "Psi"

    def test_Omega(self, sym):
        """Maps \\Omega to unicode and ascii."""
        assert sym.unicode(r"\Omega") == "Ω"
        assert sym.ascii(r"\Omega") == "Omega"


class TestMathFonts:
    def test_mathbf_A(self, sym):
        """Maps \\mathbf{A} to unicode and ascii."""
        assert sym.unicode(r"\mathbf{A}") == "𝐀"
        assert sym.ascii(r"\mathbf{A}") == "A"

    def test_mathbf_z(self, sym):
        """Maps \\mathbf{z} to unicode and ascii."""
        assert sym.unicode(r"\mathbf{z}") == "𝐳"
        assert sym.ascii(r"\mathbf{z}") == "z"

    def test_mathit_A(self, sym):
        """Maps \\mathit{A} to unicode and ascii."""
        assert sym.unicode(r"\mathit{A}") == "𝐴"
        assert sym.ascii(r"\mathit{A}") == "A"

    def test_mathit_z(self, sym):
        """Maps \\mathit{z} to unicode and ascii."""
        assert sym.unicode(r"\mathit{z}") == "𝑧"
        assert sym.ascii(r"\mathit{z}") == "z"

    def test_mathcal_A(self, sym):
        """Maps \\mathcal{A} to unicode and ascii."""
        assert sym.unicode(r"\mathcal{A}") == "𝒜"
        assert sym.ascii(r"\mathcal{A}") == "A"

    def test_mathcal_Z(self, sym):
        """Maps \\mathcal{Z} to unicode and ascii."""
        assert sym.unicode(r"\mathcal{Z}") == "𝒵"
        assert sym.ascii(r"\mathcal{Z}") == "Z"

    def test_mathfrak_A(self, sym):
        """Maps \\mathfrak{A} to unicode and ascii."""
        assert sym.unicode(r"\mathfrak{A}") == "𝔄"
        assert sym.ascii(r"\mathfrak{A}") == "A"

    def test_mathfrak_g(self, sym):
        """Maps \\mathfrak{g} to unicode and ascii."""
        assert sym.unicode(r"\mathfrak{g}") == "𝔤"
        assert sym.ascii(r"\mathfrak{g}") == "g"

    def test_mathfrak_z(self, sym):
        """Maps \\mathfrak{z} to unicode and ascii."""
        assert sym.unicode(r"\mathfrak{z}") == "𝔷"
        assert sym.ascii(r"\mathfrak{z}") == "z"

    def test_mathbb_A(self, sym):
        """Maps \\mathbb{A} to unicode and ascii."""
        assert sym.unicode(r"\mathbb{A}") == "𝔸"
        assert sym.ascii(r"\mathbb{A}") == "A"

    def test_mathbb_R(self, sym):
        """Maps \\mathbb{R} to unicode and ascii."""
        assert sym.unicode(r"\mathbb{R}") == "ℝ"
        assert sym.ascii(r"\mathbb{R}") == "R"

    def test_mathbb_Z(self, sym):
        """Maps \\mathbb{Z} to unicode and ascii."""
        assert sym.unicode(r"\mathbb{Z}") == "ℤ"
        assert sym.ascii(r"\mathbb{Z}") == "Z"

    def test_mathbb_N(self, sym):
        """Maps \\mathbb{N} to unicode and ascii."""
        assert sym.unicode(r"\mathbb{N}") == "ℕ"
        assert sym.ascii(r"\mathbb{N}") == "N"

    def test_mathbb_Q(self, sym):
        """Maps \\mathbb{Q} to unicode and ascii."""
        assert sym.unicode(r"\mathbb{Q}") == "ℚ"
        assert sym.ascii(r"\mathbb{Q}") == "Q"

    def test_mathbb_C(self, sym):
        """Maps \\mathbb{C} to unicode and ascii."""
        assert sym.unicode(r"\mathbb{C}") == "ℂ"
        assert sym.ascii(r"\mathbb{C}") == "C"

    def test_mathbb_H(self, sym):
        """Maps \\mathbb{H} to unicode and ascii."""
        assert sym.unicode(r"\mathbb{H}") == "ℍ"
        assert sym.ascii(r"\mathbb{H}") == "H"

    def test_mathbb_P(self, sym):
        """Maps \\mathbb{P} to unicode and ascii."""
        assert sym.unicode(r"\mathbb{P}") == "ℙ"
        assert sym.ascii(r"\mathbb{P}") == "P"


class TestCommonSymbols:
    def test_hbar(self, sym):
        """Maps \\hbar to unicode and ascii."""
        assert sym.unicode(r"\hbar") == "ℏ"
        assert sym.ascii(r"\hbar") == "hbar"

    def test_ell(self, sym):
        """Maps \\ell to unicode and ascii."""
        assert sym.unicode(r"\ell") == "ℓ"
        assert sym.ascii(r"\ell") == "ell"

    def test_nabla(self, sym):
        """Maps \\nabla to unicode and ascii."""
        assert sym.unicode(r"\nabla") == "∇"
        assert sym.ascii(r"\nabla") == "nabla"

    def test_partial(self, sym):
        """Maps \\partial to unicode and ascii."""
        assert sym.unicode(r"\partial") == "∂"
        assert sym.ascii(r"\partial") == "partial"

    def test_infty(self, sym):
        """Maps \\infty to unicode and ascii."""
        assert sym.unicode(r"\infty") == "∞"
        assert sym.ascii(r"\infty") == "infty"

    def test_forall(self, sym):
        """Maps \\forall to unicode and ascii."""
        assert sym.unicode(r"\forall") == "∀"
        assert sym.ascii(r"\forall") == "forall"

    def test_exists(self, sym):
        """Maps \\exists to unicode and ascii."""
        assert sym.unicode(r"\exists") == "∃"
        assert sym.ascii(r"\exists") == "exists"

    def test_emptyset(self, sym):
        """Maps \\emptyset to unicode and ascii."""
        assert sym.unicode(r"\emptyset") == "∅"
        assert sym.ascii(r"\emptyset") == "emptyset"

    def test_aleph(self, sym):
        """Maps \\aleph to unicode and ascii."""
        assert sym.unicode(r"\aleph") == "ℵ"
        assert sym.ascii(r"\aleph") == "aleph"

    def test_wp(self, sym):
        """Maps \\wp to unicode and ascii."""
        assert sym.unicode(r"\wp") == "℘"
        assert sym.ascii(r"\wp") == "wp"

    def test_Re(self, sym):
        """Maps \\Re to unicode and ascii."""
        assert sym.unicode(r"\Re") == "ℜ"
        assert sym.ascii(r"\Re") == "Re"

    def test_Im(self, sym):
        """Maps \\Im to unicode and ascii."""
        assert sym.unicode(r"\Im") == "ℑ"
        assert sym.ascii(r"\Im") == "Im"


class TestOperators:
    def test_cdot(self, sym):
        """Maps \\cdot operator."""
        assert sym.unicode(r"\cdot") == "·"
        assert sym.ascii(r"\cdot") == "."

    def test_times(self, sym):
        """Maps \\times operator."""
        assert sym.unicode(r"\times") == "×"
        assert sym.ascii(r"\times") == "x"

    def test_wedge(self, sym):
        """Maps \\wedge operator."""
        assert sym.unicode(r"\wedge") == "∧"
        assert sym.ascii(r"\wedge") == "^"

    def test_vee(self, sym):
        """Maps \\vee operator."""
        assert sym.unicode(r"\vee") == "∨"
        assert sym.ascii(r"\vee") == "v"

    def test_star(self, sym):
        """Maps \\star operator."""
        assert sym.unicode(r"\star") == "⋆"
        assert sym.ascii(r"\star") == "*"

    def test_dagger(self, sym):
        """Maps \\dagger operator."""
        assert sym.unicode(r"\dagger") == "†"
        assert sym.ascii(r"\dagger") == "dag"

    def test_pm(self, sym):
        """Maps \\pm operator."""
        assert sym.unicode(r"\pm") == "±"
        assert sym.ascii(r"\pm") == "+/-"

    def test_mp(self, sym):
        """Maps \\mp operator."""
        assert sym.unicode(r"\mp") == "∓"
        assert sym.ascii(r"\mp") == "-/+"

    def test_circ(self, sym):
        """Maps \\circ operator."""
        assert sym.unicode(r"\circ") == "∘"
        assert sym.ascii(r"\circ") == "o"

    def test_otimes(self, sym):
        """Maps \\otimes operator."""
        assert sym.unicode(r"\otimes") == "⊗"
        assert sym.ascii(r"\otimes") == "(x)"

    def test_oplus(self, sym):
        """Maps \\oplus operator."""
        assert sym.unicode(r"\oplus") == "⊕"
        assert sym.ascii(r"\oplus") == "(+)"


class TestRelations:
    def test_leq(self, sym):
        """Maps \\leq relation."""
        assert sym.unicode(r"\leq") == "≤"
        assert sym.ascii(r"\leq") == "<="

    def test_geq(self, sym):
        """Maps \\geq relation."""
        assert sym.unicode(r"\geq") == "≥"
        assert sym.ascii(r"\geq") == ">="

    def test_neq(self, sym):
        """Maps \\neq relation."""
        assert sym.unicode(r"\neq") == "≠"
        assert sym.ascii(r"\neq") == "!="

    def test_approx(self, sym):
        """Maps \\approx relation."""
        assert sym.unicode(r"\approx") == "≈"
        assert sym.ascii(r"\approx") == "~="

    def test_equiv(self, sym):
        """Maps \\equiv relation."""
        assert sym.unicode(r"\equiv") == "≡"
        assert sym.ascii(r"\equiv") == "==="

    def test_sim(self, sym):
        """Maps \\sim relation."""
        assert sym.unicode(r"\sim") == "∼"
        assert sym.ascii(r"\sim") == "~"

    def test_propto(self, sym):
        """Maps \\propto relation."""
        assert sym.unicode(r"\propto") == "∝"
        assert sym.ascii(r"\propto") == "propto"

    def test_in_(self, sym):
        """Maps \\in_ relation."""
        assert sym.unicode(r"\in") == "∈"
        assert sym.ascii(r"\in") == "in"

    def test_subset(self, sym):
        """Maps \\subset relation."""
        assert sym.unicode(r"\subset") == "⊂"
        assert sym.ascii(r"\subset") == "subset"

    def test_supset(self, sym):
        """Maps \\supset relation."""
        assert sym.unicode(r"\supset") == "⊃"
        assert sym.ascii(r"\supset") == "supset"


class TestArrows:
    def test_to(self, sym):
        """Maps \\to arrow."""
        assert sym.unicode(r"\to") == "→"
        assert sym.ascii(r"\to") == "->"

    def test_leftarrow(self, sym):
        """Maps \\leftarrow arrow."""
        assert sym.unicode(r"\leftarrow") == "←"
        assert sym.ascii(r"\leftarrow") == "<-"

    def test_Rightarrow(self, sym):
        """Maps \\Rightarrow arrow."""
        assert sym.unicode(r"\Rightarrow") == "⇒"
        assert sym.ascii(r"\Rightarrow") == "=>"

    def test_Leftarrow(self, sym):
        """Maps \\Leftarrow arrow."""
        assert sym.unicode(r"\Leftarrow") == "⇐"
        assert sym.ascii(r"\Leftarrow") == "<="

    def test_leftrightarrow(self, sym):
        """Maps \\leftrightarrow arrow."""
        assert sym.unicode(r"\leftrightarrow") == "↔"
        assert sym.ascii(r"\leftrightarrow") == "<->"

    def test_mapsto(self, sym):
        """Maps \\mapsto arrow."""
        assert sym.unicode(r"\mapsto") == "↦"
        assert sym.ascii(r"\mapsto") == "|->"


class TestUnknown:
    def test_unknown_returns_none(self, sym):
        """Unknown command returns None."""
        assert sym.unicode(r"\bogus") is None
        assert sym.ascii(r"\bogus") is None

    def test_plain_letter(self, sym):
        """Plain letter returns None."""
        assert sym.unicode("x") is None
        assert sym.ascii("x") is None

    def test_lookup(self, sym):
        """lookup() returns (unicode, ascii) pair."""
        u, a = sym.lookup(r"\phi")
        assert u == "ϕ"
        assert a == "phi"

    def test_lookup_unknown(self, sym):
        """lookup() returns None for unknown."""
        assert sym.lookup(r"\bogus") is None

    def test_lookup_mathbf(self, sym):
        """lookup() handles \\mathbf."""
        u, a = sym.lookup(r"\mathbf{v}")
        assert u == "𝐯"
        assert a == "v"


class TestAccents:
    def test_hat(self, sym):
        """Maps \\hat accent."""
        assert sym.unicode(r"\hat{a}") == "a\u0302"
        assert sym.ascii(r"\hat{a}") == "hat_a"

    def test_tilde(self, sym):
        """Maps \\tilde accent."""
        assert sym.unicode(r"\tilde{R}") == "R\u0303"
        assert sym.ascii(r"\tilde{R}") == "tilde_R"

    def test_bar(self, sym):
        """Maps \\bar accent."""
        assert sym.unicode(r"\bar{x}") == "x\u0304"
        assert sym.ascii(r"\bar{x}") == "bar_x"

    def test_vec(self, sym):
        """Maps \\vec accent."""
        assert sym.unicode(r"\vec{v}") == "v\u20d7"
        assert sym.ascii(r"\vec{v}") == "vec_v"

    def test_dot(self, sym):
        """Maps \\dot accent."""
        assert sym.unicode(r"\dot{q}") == "q\u0307"
        assert sym.ascii(r"\dot{q}") == "dot_q"

    def test_ddot(self, sym):
        """Maps \\ddot accent."""
        assert sym.unicode(r"\ddot{x}") == "x\u0308"
        assert sym.ascii(r"\ddot{x}") == "ddot_x"

    def test_hat_in_name(self):
        """Maps \\hat_in_name accent."""
        from galaga import Algebra

        alg = Algebra((1, 1, 1))
        e1, _, _ = alg.basis_vectors()
        n = e1.name(latex=r"\hat{n}")
        assert "n" in str(n)
        assert n._name == "hat_n"
