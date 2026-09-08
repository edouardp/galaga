"""Public naming-preset contracts with complete v1 vocabulary evidence."""

import json
from dataclasses import FrozenInstanceError
from functools import lru_cache
from pathlib import Path

import numpy as np
import pytest

import galaga as ga
import galaga.core as core

ARCHIVE = json.loads((Path(__file__).parents[2] / "tools/baselines/naming-presets-v1.json").read_text())
TARGETS = ("ascii", "unicode", "latex")
GRAMS = (
    ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    ((2, 0.5, -0.25), (0.5, -1, 0.75), (-0.25, 0.75, 3)),
    ((1, 1, 0), (1, 1, 0), (0, 0, 0)),
)
CUSTOM_NAMES = (ga.Name("a", "𝐚", "𝐚"), ga.Name("b", "𝐛", "𝐛"), ga.Name("c", "𝐜", "𝐜"))


def word_convention(names):
    """Name native exterior masks, not evaluated geometric vector words."""
    labels = []
    for mask in range(1 << len(names)):
        selected = [name for index, name in enumerate(names) if mask & (1 << index)]
        labels.append(
            ga.Name(
                "".join(name.ascii for name in selected) or "1",
                "".join(name.unicode for name in selected) or "1",
                " ".join(name.latex for name in selected) or "1",
            )
        )
    return ga.BladeConvention(len(names), labels)


def convention_for(key):
    if key == "gamma":
        return ga.indexed_blade_convention(4, prefix=ga.Name("g", "γ", r"\gamma"), start=0, style="juxtapose")
    if key == "sigma":
        return ga.indexed_blade_convention(3, prefix=ga.Name("s", "σ", r"\sigma"), style="juxtapose")
    if key == "sigma_xyz":
        return word_convention(
            (ga.Name("x", "σₓ", r"\sigma_{x}"), ga.Name("y", "σᵧ", r"\sigma_{y}"), ga.Name("z", "σz", r"\sigma_{z}"))
        )
    assert key in {"custom_2", "custom_3"}
    return word_convention(CUSTOM_NAMES[: int(key[-1])])


def accepted_latex(text):
    for subscript in "xyz":
        text = text.replace(r"\sigma_" + subscript, rf"\sigma_{{{subscript}}}")
    return text


def assert_data(actual, expected):
    actual, expected = np.asarray(actual), np.asarray(expected)
    assert actual.ndim == expected.ndim == 1 and actual.shape == expected.shape
    assert np.isfinite(actual).all() and np.isfinite(expected).all()
    np.testing.assert_allclose(actual, expected, rtol=0, atol=2e-12)


def exterior_coefficients(dimension, mask, orientation=1):
    data = np.zeros(1 << dimension)
    data[mask] = orientation
    return data


def exterior_blade(algebra, mask):
    blade = algebra.identity
    for index, vector in enumerate(algebra.basis_vectors()):
        if mask & (1 << index):
            blade = blade ^ vector
    return blade


def assert_named_vector(key, signature, ascii_name, unicode_name, latex_name):
    algebra = ga.Algebra(signature=signature, blades=convention_for(key))
    vector = algebra.basis_vectors()[0]
    assert_data(vector.data, exterior_coefficients(algebra.n, 1))
    assert repr(vector) == ascii_name
    assert str(vector) == vector.unicode() == unicode_name
    assert vector.latex() == latex_name
    for name in (ascii_name, unicode_name, latex_name):
        assert algebra.blade(name) == vector


class TestNamingPresets:
    def test_gamma_preset(self):
        assert_named_vector("gamma", (1, -1, -1, -1), "g0", "γ₀", r"\gamma_{0}")

    def test_sigma_preset(self):
        assert_named_vector("sigma", (1, 1, 1), "s1", "σ₁", r"\sigma_{1}")

    def test_sigma_xyz_preset(self):
        assert_named_vector("sigma_xyz", (1, 1, 1), "x", "σₓ", r"\sigma_{x}")

    def test_custom_names(self):
        assert_named_vector("custom_2", (1, 1), "a", "𝐚", "𝐚")

    def test_custom_names_wrong_length(self):
        with pytest.raises(ValueError, match="requires 4 labels"):
            ga.BladeConvention(2, ("1", "a"))
        with pytest.raises(ValueError, match="dimensions must match"):
            ga.Algebra(2, blades=ga.BladeConvention(1, ("1", "a")))

    def test_invalid_blades_type(self):
        with pytest.raises(TypeError, match="blades must be a BladeConvention"):
            ga.Algebra(2, blades="bogus")

    def test_blade_lookup_custom_names(self):
        algebra = ga.Algebra(signature=(1, -1, -1, -1), blades=convention_for("gamma"))
        g0, g1, _, _ = algebra.basis_vectors()
        assert algebra.blade("g0g1") == g0 ^ g1
        assert_data(algebra.blade("g0g1").data, exterior_coefficients(4, 3))

    def test_blade_lookup_custom_no_match(self):
        algebra = ga.Algebra(2, blades=convention_for("custom_2"))
        with pytest.raises(KeyError, match="unknown blade"):
            algebra.blade("xyz")

    def test_blade_name_custom_unicode(self):
        algebra = ga.Algebra(3, blades=convention_for("custom_3"))
        a, b, c = algebra.basis_vectors()
        assert str(a * b) == "𝐚𝐛" and repr(a * b) == "ab"
        assert str(a * b * c) == "𝐚𝐛𝐜" and repr(a * b * c) == "abc"
        assert a * b == a ^ b
        assert a * b * c == a ^ b ^ c


@pytest.mark.parametrize("table", ARCHIVE["tables"], ids=lambda table: table["id"])
@pytest.mark.parametrize("target", TARGETS)
@pytest.mark.parametrize("expr", (False, True))
def test_complete_archived_vocabularies_preserve_lookup_values_and_blade_squares(table, target, expr):
    algebra = ga.Algebra(signature=table["signature"], blades=convention_for(table["id"]))
    labels = algebra.presentation.blades.labels
    assert [row["mask"] for row in table["labels"]] == list(range(algebra.dim))
    for row in table["labels"]:
        mask = row["mask"]
        expected = exterior_coefficients(algebra.n, mask)
        assert_data(row["data"], expected)
        assert_data(exterior_blade(algebra, mask).data, expected)
        label = labels[mask]
        name = accepted_latex(row["names"][target]) if target == "latex" else row["names"][target]
        assert label.name.for_target(target) == name and label.ref == ga.BladeRef(mask)
        value = algebra.blade(name, expr=expr)
        assert_data(value.data, expected)
        assert_data(value.data, row["lookups"][target])
        assert (value.expr is not None) == expr
        if expr:
            assert_data(ga.evaluate(value.expr, algebra=algebra).data, expected)
        before, value_hash = value.expr, hash(value)
        assert value.display("value/" + target) == name
        assert str(value) == row["unicode"]
        assert row["repr"] == row["unicode"]  # V1 repr was Unicode.
        assert repr(value) == row["names"]["ascii"]
        assert value.latex(content="value") == accepted_latex(row["latex"])
        assert value.expr is before and hash(value) == value_hash
        indices = [i for i in range(algebra.n) if mask & (1 << i)]
        grade = len(indices)
        square = (-1) ** (grade * (grade - 1) // 2) * np.linalg.det(algebra.gram[np.ix_(indices, indices)])
        expected_square = exterior_coefficients(algebra.n, 0, square)
        assert_data(row["square"], expected_square)
        assert_data((value * value).data, expected_square)


@lru_cache
def reference_products(gram):
    reference = core.Algebra(gram=gram, product_backend="reference")
    return np.stack([reference.left_action(reference.blade(mask)) for mask in range(reference.dim)], axis=1)


@pytest.mark.parametrize("gram", GRAMS, ids=("euclidean", "oblique-indefinite", "degenerate"))
@pytest.mark.parametrize("style", ("compact", "juxtapose", "wedge"))
@pytest.mark.parametrize("target", TARGETS)
def test_indexed_words_are_exterior_labels_in_general_gram_frames(gram, style, target):
    base = ga.Algebra(gram=gram)
    convention = ga.indexed_blade_convention(3, prefix=ga.Name("g", "γ", r"\gamma"), start=0, style=style)
    view = base.with_blades(convention)
    assert view.numeric is base.numeric
    assert view.presentation.local_names is base.presentation.local_names
    assert view.display_order == base.display_order
    tensor = reference_products(gram)
    for left_mask in range(view.dim):
        name = convention.label(left_mask).name.for_target(target)
        left = view.blade(name, expr=True)
        assert_data(left.data, exterior_coefficients(view.n, left_mask))
        assert_data(ga.evaluate(left.expr, algebra=view).data, left.data)
        assert left.display("value/" + target) == name
        assert left == exterior_blade(base, left_mask)
        for right_mask in range(view.dim):
            right_name = convention.label(right_mask).name.for_target(target)
            right = view.blade(right_name, expr=True)
            product = left * right
            assert_data(product.data, tensor[:, left_mask, right_mask])
            assert_data(ga.evaluate(product.expr, algebra=view).data, tensor[:, left_mask, right_mask])
            assert product.display("value/" + target)
    g0, g1, g2 = view.basis_vectors()
    plane, volume = view.blade(3), view.blade(7)
    assert plane == g0 ^ g1 and volume == g0 ^ g1 ^ g2
    gp, triple = (g0 * g1).data, (g0 * g1 * g2).data
    expected_pair = exterior_coefficients(3, 3)
    expected_pair[0] = gram[0][1]
    expected_triple = exterior_coefficients(3, 7)
    expected_triple[1], expected_triple[2], expected_triple[4] = gram[1][2], -gram[0][2], gram[0][1]
    assert_data(gp, expected_pair)
    assert_data(triple, expected_triple)
    assert (g0 * g1 == plane) == (gram[0][1] == 0)


def signed_view(gram):
    algebra = ga.Algebra(gram=gram, blades=convention_for("custom_3"))
    a, b, _ = algebra.basis_vectors()
    reverse_plane = b ^ a
    (mask,) = np.flatnonzero(reverse_plane.data)
    ref = ga.BladeRef(int(mask), int(reverse_plane.data[mask]))
    labels = list(algebra.presentation.blades.labels)
    labels[mask] = ga.BladeLabel(ga.Name("ba", "𝐛𝐚", "𝐛 𝐚"), ref)
    convention = ga.BladeConvention(3, labels, aliases={"ab": int(mask)}, roles={"oriented_plane": ref})
    return algebra, algebra.with_blades(convention), reverse_plane, ref


@pytest.mark.parametrize("gram", GRAMS)
@pytest.mark.parametrize("target", TARGETS)
@pytest.mark.parametrize("expr", (False, True))
def test_oriented_names_aliases_and_native_masks_preserve_computed_exterior_signs(gram, target, expr):
    base, view, reverse_plane, ref = signed_view(gram)
    spelling = view.blade_label(ref.mask).name.for_target(target)
    expected = exterior_coefficients(3, ref.mask, ref.orientation)
    assert_data(reverse_plane.data, expected)
    for key in (spelling, "oriented_plane", ref):
        value = view.blade(key, expr=expr)
        assert_data(value.data, expected)
        assert value == reverse_plane and hash(value) == hash(reverse_plane)
        assert value.display("value/" + target) == spelling
        if expr:
            assert value.expr == ga.BladeLiteral(ref.mask, ref.orientation)
            assert_data(ga.evaluate(value.expr, algebra=view).data, expected)
    native = view.blade(ref.mask)
    assert view.blade("ab") == native == -reverse_plane
    assert native.display("value/" + target) == "-" + spelling
    assert view.numeric is base.numeric
    assert view.presentation.local_names is base.presentation.local_names
    original = base.presentation
    with pytest.raises(RuntimeError, match="restore"):
        with base.use_presentation(view.presentation):
            assert base.blade("oriented_plane") == reverse_plane
            raise RuntimeError("restore")
    assert base.presentation is original
    with pytest.raises(KeyError):
        base.blade("oriented_plane")


@pytest.mark.parametrize("gram", GRAMS)
def test_display_names_do_not_implicitly_replace_python_local_bindings(gram):
    base, view, reverse_plane, ref = signed_view(gram)
    assert tuple(base.locals()) == tuple(view.locals())
    assert "ba" not in view.locals()
    explicit = view.with_local_names(ga.LocalNamePolicy.from_convention(view.presentation.blades))
    assert explicit.locals()["ba"] == reverse_plane
    assert explicit.locals(expr=True)["ba"].expr == ga.Symbol("ba")
    assert explicit.numeric is base.numeric
    assert dict(base.locals()) == dict(view.locals())
    assert explicit.presentation.blades is view.presentation.blades
    assert explicit.blade(ref) == reverse_plane


@pytest.mark.parametrize("kind", ("sequence", "mapping"))
def test_complete_label_inputs_are_snapshotted_and_metadata_stays_immutable(kind):
    labels = ["1", "a", "b", "ab"]
    source = labels if kind == "sequence" else dict(enumerate(labels))
    aliases, roles = {"plane": 3}, {"first": 1}
    convention = ga.BladeConvention(2, source, aliases=aliases, roles=roles)
    before = hash(convention)
    source[3] = "changed"
    aliases["plane"], roles["first"] = 1, 2
    assert convention.label(3).name == ga.Name("ab")
    assert convention.resolve("plane") == ga.BladeRef(3)
    assert convention.resolve("first") == ga.BladeRef(1)
    assert hash(convention) == before
    with pytest.raises(FrozenInstanceError):
        convention.dimension = 3
    with pytest.raises(FrozenInstanceError):
        convention.label(3).name = ga.Name("changed")


@pytest.mark.parametrize("field", ("ascii", "unicode", "latex"))
def test_ambiguous_target_spellings_are_rejected_before_binding(field):
    names = [
        ga.Name("1"),
        ga.Name("a", "α", r"\alpha"),
        ga.Name("b", "β", r"\beta"),
        ga.Name("ab", "αβ", r"\alpha \beta"),
    ]
    variants = dict(zip(TARGETS, names[2].variants, strict=True))
    variants[field] = getattr(names[1], field)
    names[2] = ga.Name(**variants)
    with pytest.raises(ValueError, match="ambiguous canonical"):
        ga.BladeConvention(2, names)


def test_xyz_ascii_keys_and_safe_latex_scripts_are_explicit_not_prefix_inference():
    algebra = ga.Algebra(3, blades=convention_for("sigma_xyz"))
    for index, key in enumerate("xyz"):
        assert algebra.blade(key) == algebra.blade(rf"\sigma_{{{key}}}") == algebra.blade(1 << index)
        for missing in ("s" + key, r"\sigma_" + key):
            with pytest.raises(KeyError, match="unknown blade"):
                algebra.blade(missing)
