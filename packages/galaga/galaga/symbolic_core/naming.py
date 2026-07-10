"""Shared symbolic naming helpers."""

from __future__ import annotations

from dataclasses import dataclass

from galaga.latex_symbols import LatexSymbols


@dataclass(frozen=True)
class NameParts:
    """Normalized display names for all supported render formats."""

    ascii: str
    unicode: str
    latex: str


def _strip_optional(value: str | None) -> str | None:
    return value.strip() if value is not None else None


def normalize_name(
    label: str | None = None,
    *,
    latex: str | None = None,
    unicode: str | None = None,
    ascii: str | None = None,
) -> NameParts:
    """Normalize a Galaga-style display name.

    This mirrors the existing ``Multivector.name()`` behavior: ``label`` is the
    fallback for all formats, ``latex=`` can derive unicode/ascii names through
    ``LatexSymbols``, explicit format overrides win, and surrounding whitespace
    is stripped.
    """

    if label is None and latex is None:
        raise ValueError("At least one of label or latex must be provided")

    label = _strip_optional(label)
    latex = _strip_optional(latex)
    unicode = _strip_optional(unicode)
    ascii = _strip_optional(ascii)

    if latex is not None and (unicode is None or ascii is None):
        derived = LatexSymbols().lookup(latex)
        if derived is not None:
            unicode_derived, ascii_derived = derived
            if unicode is None:
                unicode = unicode_derived
            if ascii is None:
                ascii = ascii_derived

    ascii_name = ascii or label or latex
    latex_name = latex or label
    unicode_name = unicode or label or ascii_name

    return NameParts(ascii=ascii_name, unicode=unicode_name, latex=latex_name)


class SymbolicNamingMixin:
    """Reusable in-place naming lifecycle for symbolic value wrappers.

    Subclasses provide copy and leaf-expression hooks. The mixin deliberately
    follows the Multivector naming lifecycle rather than inventing a second
    one for matrices.
    """

    _name: str | None
    _name_latex: str | None
    _name_unicode: str | None
    _is_symbolic: bool
    _expr: object | None

    def _init_symbolic_state(self) -> None:
        self._name = None
        self._name_latex = None
        self._name_unicode = None
        self._is_symbolic = False
        self._expr = None

    def name(
        self,
        label: str | None = None,
        *,
        latex: str | None = None,
        unicode: str | None = None,
        ascii: str | None = None,
    ):
        parts = normalize_name(label, latex=latex, unicode=unicode, ascii=ascii)
        self._name = parts.ascii
        self._name_latex = parts.latex
        self._name_unicode = parts.unicode
        self._is_symbolic = True

        if self._expr is None or self._is_symbolic_leaf_expr(self._expr):
            self._expr = self._make_symbolic_leaf()
        return self

    def anon(self):
        """Remove display name while preserving existing symbolic expression."""

        if self._is_symbolic_leaf_expr(self._expr):
            self._expr = None
        self._name = None
        self._name_latex = None
        self._name_unicode = None
        return self

    def symbolic(self):
        self._is_symbolic = True
        return self

    def lazy(self):
        return self.symbolic()

    def numeric(self, name: str | None = None):
        self._is_symbolic = False
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

    def eager(self, name: str | None = None):
        return self.numeric(name)

    def eval(self):
        return self._copy_with_symbolic(
            _is_symbolic=False,
            _expr=None,
            _name=None,
            _name_latex=None,
            _name_unicode=None,
        )

    def reveal(self):
        return self._copy_with_symbolic(
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
    ):
        return self._copy_with_symbolic().name(label, latex=latex, unicode=unicode, ascii=ascii)

    def _copy_with_symbolic(self, **overrides):
        raise NotImplementedError

    def _make_symbolic_leaf(self):
        raise NotImplementedError

    def _is_symbolic_leaf_expr(self, expr) -> bool:
        from .expr import Sym

        return isinstance(expr, Sym)
