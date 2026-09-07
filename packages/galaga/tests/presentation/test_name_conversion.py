"""Bounded LaTeX conversion: independent Unicode and numeric contracts."""

import unicodedata
from dataclasses import FrozenInstanceError
from string import ascii_letters, digits

import numpy as np
import pytest

import galaga as ga
from galaga.expression import Symbol, evaluate
from galaga.names import LatexSymbols, Name

FONTS = {
    "mathbf": "BOLD",
    "mathit": "ITALIC",
    "mathcal": "SCRIPT",
    "mathfrak": "FRAKTUR",
    "mathbb": "DOUBLE-STRUCK",
}
# Independent Unicode-name oracle: production uses codepoint offsets.
# These pre-existing Letterlike Symbols occupy gaps in the math alphabet.
LETTERLIKE = {
    "mathit": {"h": "PLANCK CONSTANT"},
    "mathcal": {
        **{char: f"SCRIPT CAPITAL {char}" for char in "BEFHILMR"},
        **{char: f"SCRIPT SMALL {char.upper()}" for char in "ego"},
    },
    "mathfrak": {
        "C": "BLACK-LETTER CAPITAL C",
        "H": "BLACK-LETTER CAPITAL H",
        "I": "BLACK-LETTER CAPITAL I",
        "R": "BLACK-LETTER CAPITAL R",
        "Z": "BLACK-LETTER CAPITAL Z",
    },
    "mathbb": {char: f"DOUBLE-STRUCK CAPITAL {char}" for char in "CHNPQRZ"},
}


@pytest.mark.parametrize("font", FONTS)
@pytest.mark.parametrize("char", ascii_letters)
def test_every_font_letter_matches_the_unicode_database(font, char):
    case = "CAPITAL" if char.isupper() else "SMALL"
    unicode_name = LETTERLIKE.get(font, {}).get(char, f"MATHEMATICAL {FONTS[font]} {case} {char.upper()}")
    expected = unicodedata.lookup(unicode_name)
    latex = rf"\{font}{{{char}}}"
    symbols = LatexSymbols()
    assert symbols.lookup(latex) == (expected, char)
    assert symbols.unicode(latex) == expected
    assert symbols.ascii(latex) == char
    assert unicodedata.normalize("NFKD", expected) == char


@pytest.mark.parametrize("font", FONTS)
@pytest.mark.parametrize("char, word", tuple(enumerate("ZERO ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE".split())))
def test_font_digits_have_their_own_blocks_or_are_unsupported(font, char, word):
    latex = rf"\{font}{{{char}}}"
    if font in ("mathbf", "mathbb"):
        expected = unicodedata.lookup(f"MATHEMATICAL {FONTS[font]} DIGIT {word}")
        assert LatexSymbols().lookup(latex) == (expected, str(char))
    else:
        assert LatexSymbols().lookup(latex) is None


@pytest.mark.parametrize(
    "latex, expected",
    ((r"\mathbb{a}", "𝕒"), (r"\mathbb{z}", "𝕫"), (r"\mathcal{a}", "𝒶"), (r"\mathcal{z}", "𝓏")),
)
def test_lowercase_script_and_double_struck_regressions(latex, expected):
    assert LatexSymbols().unicode(latex) == expected


@pytest.mark.parametrize("font", FONTS)
@pytest.mark.parametrize("char", ("_", "θ", "ℍ", "é", "９", "𐐀", "\U0010ffff"))
def test_font_offsets_never_accept_non_latin_letters_or_non_ascii_digits(font, char):
    latex = rf"\{font}{{{char}}}"
    assert LatexSymbols().lookup(latex) is None
    assert LatexSymbols().unicode(latex) is None
    assert LatexSymbols().ascii(latex) is None


@pytest.mark.parametrize(
    "accent, unicode_name",
    (
        ("hat", "COMBINING CIRCUMFLEX ACCENT"),
        ("tilde", "COMBINING TILDE"),
        ("bar", "COMBINING MACRON"),
        ("vec", "COMBINING RIGHT ARROW ABOVE"),
        ("dot", "COMBINING DOT ABOVE"),
        ("ddot", "COMBINING DIAERESIS"),
    ),
)
def test_accents_cover_ascii_letters_and_digits_without_normalizing(accent, unicode_name):
    symbols = LatexSymbols()
    combining = unicodedata.lookup(unicode_name)
    for char in ascii_letters + digits:
        assert symbols.lookup(rf"\{accent}{{{char}}}") == (char + combining, f"{accent}_{char}")


@pytest.mark.parametrize(
    "latex",
    (
        "",
        "x",
        r"\unknown",
        r"\alpha trailing",
        " \\alpha",
        "\\alpha\n",
        r"\mathbf{}",
        r"\mathbf{ab}",
        r"\mathbf{a",
        r"\mathbf a",
        r"\mathbf{\alpha}",
        r"\mathsf{x}",
        r"\mathbf{x}y",
        r"\hat{θ}",
        r"\hat{_}",
        r"\hat{é}",
        r"\hat{\theta}",
        r"\hat{ab}",
        r"\hat{a}tail",
        r"\hat{}",
        r"\hat a",
        r"\hat{a",
    ),
)
def test_lookup_is_exact_and_does_not_guess_unsupported_tex(latex):
    symbols = LatexSymbols()
    assert symbols.lookup(latex) is None
    assert symbols.unicode(latex) is None
    assert symbols.ascii(latex) is None


@pytest.mark.parametrize("value", (None, 1, b"\\alpha", [], {}))
@pytest.mark.parametrize("method", ("lookup", "unicode", "ascii"))
def test_lookup_rejects_non_string_inputs(value, method):
    with pytest.raises(TypeError, match="LaTeX.*string"):
        getattr(LatexSymbols(), method)(value)


@pytest.mark.parametrize(
    "latex, variants",
    (
        (r"\alpha", ("alpha", "α", r"\alpha")),
        (r"\lambda", ("lambda_", "λ", r"\lambda")),
        (r"\mathbb{a}", ("a", "𝕒", r"\mathbb{a}")),
        (r"\hat{n}", ("hat_n", "n\u0302", r"\hat{n}")),
        (r"\mathbf{0}", ("0", "𝟎", r"\mathbf{0}")),
        (r"\to", ("->", "→", r"\to")),
    ),
)
def test_explicit_name_factory_derives_spellings(latex, variants):
    name = Name.from_latex(latex)
    assert ga.Name is Name
    assert name.variants == variants
    assert name == Name(*variants) and hash(name) == hash(Name(*variants))
    assert str(name) == variants[1]
    for target, spelling in zip(("ascii", "unicode", "latex"), variants, strict=True):
        assert name.for_target(target) == spelling
    with pytest.raises(FrozenInstanceError):
        name.ascii = "changed"


@pytest.mark.parametrize(
    "latex, overrides, expected",
    (
        (r"\alpha", {"ascii": "a"}, ("a", "α", r"\alpha")),
        (r"\alpha", {"unicode": "a"}, ("alpha", "a", r"\alpha")),
        (r"\alpha", {"ascii": "a", "unicode": "A"}, ("a", "A", r"\alpha")),
        (r"\hat{\theta}", {"ascii": "normal"}, ("normal", "normal", r"\hat{\theta}")),
        (r"\hat{\theta}", {"ascii": "normal", "unicode": "θ̂"}, ("normal", "θ̂", r"\hat{\theta}")),
    ),
)
def test_explicit_overrides_win_and_unknown_tex_uses_an_explicit_fallback(latex, overrides, expected):
    assert Name.from_latex(latex, **overrides).variants == expected


def test_only_the_opt_in_factory_strips_surrounding_whitespace():
    assert Name.from_latex(" \n\\alpha\t ") == Name("alpha", "α", r"\alpha")
    assert Name(" x ").variants == (" x ", " x ", " x ")
    assert Name(r"\alpha").variants == (r"\alpha", r"\alpha", r"\alpha")
    assert Name("a", latex=r"\alpha").variants == ("a", "a", r"\alpha")
    value = ga.Algebra(1).blade(1).named(r"\alpha")
    assert value.name == Name(r"\alpha")


@pytest.mark.parametrize("latex", ("x", r"\unknown", r"\hat{\theta}", r"\mathbf{θ}"))
@pytest.mark.parametrize("overrides", ({}, {"unicode": "θ"}))
def test_unknown_tex_requires_an_explicit_ascii_fallback(latex, overrides):
    with pytest.raises(ValueError, match="provide ascii="):
        Name.from_latex(latex, **overrides)


@pytest.mark.parametrize("latex", ("", " ", "\n\t"))
def test_factory_rejects_blank_latex_even_with_a_fallback(latex):
    with pytest.raises(ValueError, match="LaTeX.*non-empty"):
        Name.from_latex(latex, ascii="x")


@pytest.mark.parametrize("latex", (None, 1, b"\\alpha", [], {}))
def test_factory_rejects_non_string_latex(latex):
    with pytest.raises(TypeError, match="LaTeX.*string"):
        Name.from_latex(latex, ascii="x")


@pytest.mark.parametrize("latex", (r"\alpha", r"\unknown"))
@pytest.mark.parametrize(
    "overrides, message",
    (
        ({"ascii": ""}, "ASCII"),
        ({"ascii": 1}, "ASCII"),
        ({"ascii": "x", "unicode": ""}, "Unicode"),
        ({"ascii": "x", "unicode": 1}, "Unicode"),
    ),
)
def test_factory_reuses_nonempty_name_target_validation(latex, overrides, message):
    with pytest.raises(ValueError, match=message):
        Name.from_latex(latex, **overrides)


@pytest.mark.parametrize(
    "gram",
    (((1, 0), (0, 1)), ((1, 0), (0, 0)), ((2, 0.5), (0.5, -1)), ((0, -1), (-1, 0))),
    ids=("euclidean", "degenerate", "oblique", "native-null"),
)
def test_derived_names_change_only_presentation_not_metric_products_or_replay(gram):
    algebra = ga.Algebra(gram=gram)
    left, right = algebra.basis_vectors()
    # Compute the unlabeled algebra first, then use the metric independently.
    expected = (left * right).data.copy()
    np.testing.assert_array_equal(expected, [gram[0][1], 0, 0, 1])
    assert float(left * left) == gram[0][0] and float(right * right) == gram[1][1]
    left_name, right_name = Name.from_latex(r"\hat{n}"), Name.from_latex(r"\mathbb{a}")
    named_left, named_right = left.named(left_name), right.named(right_name)
    assert named_left.numeric is left.numeric and named_right.numeric is right.numeric
    assert named_left == left and hash(named_left) == hash(left)
    assert named_right == right and hash(named_right) == hash(right)
    product = named_left * named_right
    np.testing.assert_array_equal(product.data, expected)
    assert product.expr.operands == (Symbol(left_name), Symbol(right_name))
    replayed = evaluate(product.expr, algebra=algebra, environment={left_name: left, right_name: right})
    np.testing.assert_array_equal(replayed.data, expected)
    for target, spelling in zip(("ascii", "unicode", "latex"), left_name.variants, strict=True):
        assert named_left.display(f"name/{target}") == spelling
    assert left.name is None and right.name is None
    assert left.expr is None and right.expr is None
