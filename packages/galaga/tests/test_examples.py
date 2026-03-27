from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_polarisation_notebook_does_not_embed_gm_calls_inside_markdown_cells():
    source = (ROOT / "examples" / "polarisation.py").read_text()

    assert 'mo.md(r"""\n    gm.md(' not in source
    assert 'gm.md(t"\\"\\"' not in source


def test_polarisation_notebook_uses_explicit_latex_naming_over_raw_positional_strings():
    source = (ROOT / "examples" / "polarisation.py").read_text()

    assert 'latex=r"R_{45^\\circ}"' in source
    assert 'latex=r"e_{12}"' in source
    assert '.name(r"R_{45\\degree}")' not in source
    assert ".name(r'e_{12}')" not in source


def test_polarisation_notebook_uses_private_temporaries_in_repeated_marimo_cells():
    source = (ROOT / "examples" / "polarisation.py").read_text()

    assert "    N = n_slider.value" not in source
    assert "    step_deg = 90.0 / N" not in source
    assert "    E = e1.eval()" not in source
    assert "    for i in range(1, N + 1):" not in source
    assert "    I_out = norm(E) ** 2" not in source
    assert "    theory = np.cos(np.radians(step_deg)) ** (2 * N)" not in source


def test_polarisation_notebook_avoids_mathtext_in_matplotlib_plot_labels():
    source = (ROOT / "examples" / "polarisation.py").read_text()

    assert "label=r'$\\frac{1}{4}\\sin^2(2\\theta)$'" not in source
    assert "label=r'$\\cos^{2N}(90°/N)$'" not in source
