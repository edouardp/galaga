# `galaga_mermaid` example

[Mermaid diagrams from Galaga expressions](mermaid_diagram.py) is an
executable Marimo notebook covering facade-value and expression-level diagram
generation, value annotations, compact trees, layout directions, generated
source, and notation-sensitive labels.

The notebook requires Python 3.14 for Marimo t-strings. From the repository
root, open the local example gallery with:

```shell
make run-marimo
```

The launcher selects local packages as editable installations, including
working-tree changes. The notebook is portable, but the experimental Mermaid
companion is not part of joint PyPI publication: outside the checkout, install
that companion from source or a locally built wheel as well as its dependencies.
