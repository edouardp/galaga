"""Shared exhaustive emitter dispatch with target-owned rewrites."""

from __future__ import annotations

import re
import unicodedata

from .tree import (
    Accent,
    Call,
    Delimited,
    Equality,
    Fraction,
    Group,
    Identifier,
    Infix,
    Literal,
    MathClass,
    Node,
    Postfix,
    Power,
    Prefix,
    Product,
    Subscript,
    Sum,
    Text,
    Underset,
    Wrapper,
)

_SUPERSCRIPT = str.maketrans("0123456789+-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻")
_SUBSCRIPT = str.maketrans("0123456789+-", "₀₁₂₃₄₅₆₇₈₉₊₋")
_POSITIONAL_MARKERS = frozenset("★☆●○")
_LATEX_ESCAPE = str.maketrans(
    {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "\\": r"\textbackslash{}",
    }
)


def emit(node: Node, target: str) -> str:
    """Serialize a semantic tree for one supported target."""
    if not isinstance(node, Node):
        raise TypeError("emit expects a semantic render node")
    if target not in {"ascii", "unicode", "latex"}:
        raise ValueError("emit target must be 'ascii', 'unicode', or 'latex'")
    return _emit(node, target)


def _emit(node: Node, target: str) -> str:
    if isinstance(node, Identifier):
        return node.name.for_target(target)
    if isinstance(node, Literal):
        return _number(node.value, target, node.precision)
    if isinstance(node, Text):
        return _escape_text(node.value, target)
    if isinstance(node, Group):
        body = _emit(node.body, target)
        return rf"\left({body}\right)" if target == "latex" else f"({body})"
    if isinstance(node, Sum):
        rendered: list[str] = []
        for index, term in enumerate(node.terms):
            body = _emit(term.body, target)
            if index == 0:
                rendered.append(f"-{body}" if term.negative else body)
            else:
                rendered.append((" - " if term.negative else " + ") + body)
        return "".join(rendered)
    if isinstance(node, Product):
        if node.separator is None:
            separator = " " if target == "latex" else ""
        else:
            separator = f" {node.separator.for_target(target)} "
        return separator.join(_emit(factor, target) for factor in node.factors)
    if isinstance(node, Fraction):
        numerator = _emit(node.numerator, target)
        denominator = _emit(node.denominator, target)
        if target == "latex":
            return rf"\frac{{{numerator}}}{{{denominator}}}"
        if node.numerator.precedence < node.precedence:
            numerator = f"({numerator})"
        if node.denominator.precedence <= node.precedence:
            denominator = f"({denominator})"
        return f"{numerator} / {denominator}"
    if isinstance(node, Power):
        base = _emit(node.base, target)
        exponent = _emit(node.exponent, target)
        if target == "latex":
            if isinstance(node.base, Power):
                base = "{" + base + "}"
            if re.fullmatch(r"[A-Za-z0-9*]", exponent):
                return f"{base}^{exponent}"
            return rf"{base}^{{{exponent}}}"
        if target == "unicode":
            compact = _unicode_script(exponent, superscript=True)
            if compact is not None:
                return f"{base}{compact}"
            if exponent in _POSITIONAL_MARKERS:
                return f"{base}^{exponent}"
            return f"{base}^({exponent})"
        return f"{base}^{exponent}"
    if isinstance(node, Subscript):
        base = _emit(node.base, target)
        subscript = _emit(node.subscript, target)
        if target == "latex":
            return rf"{base}_{{{subscript}}}"
        if target == "unicode":
            compact = _unicode_script(subscript, superscript=False)
            if compact is not None:
                return f"{base}{compact}"
            if subscript in _POSITIONAL_MARKERS:
                return f"{base}_{subscript}"
            return f"{base}_[{subscript}]"
        return f"{base}[{subscript}]"
    if isinstance(node, Call):
        function = node.function.for_target(target)
        if target == "latex":
            function = _latex_function(function)
            opening, closing = (r"\left(", r"\right)") if node.scalable else ("(", ")")
            separator = r",\, " if not node.scalable else ", "
        else:
            opening, closing = "(", ")"
            separator = ", "
        arguments = separator.join(_emit(argument, target) for argument in node.arguments)
        return f"{function}{opening}{arguments}{closing}"
    if isinstance(node, Prefix):
        operator = node.operator.for_target(target)
        operand = _emit(node.operand, target)
        return f"{operator}{operand}"
    if isinstance(node, Postfix):
        return f"{_emit(node.operand, target)}{node.operator.for_target(target)}"
    if isinstance(node, Infix):
        operator = _emit(node.operator, target)
        return f" {operator} ".join(_emit(operand, target) for operand in node.operands)
    if isinstance(node, Accent):
        return _accent(node, target)
    if isinstance(node, Underset):
        body = _emit(node.body, target)
        annotation = _emit(node.annotation, target)
        if target == "latex":
            return rf"\underset{{{annotation}}}{{{body}}}"
        if target == "unicode":
            compact = _unicode_script(annotation, superscript=False)
            return f"{body}{compact}" if compact is not None else f"{body}_[{annotation}]"
        return f"{body}[{annotation}]"
    if isinstance(node, MathClass):
        body = _emit(node.body, target)
        if target == "latex" and node.kind == "binary":
            return rf"\mathbin{{{body}}}"
        return body
    if isinstance(node, Wrapper):
        opening = node.opening.for_target(target)
        closing = node.closing.for_target(target)
        body = _emit(node.body, target)
        if target == "latex" and node.scalable:
            opening_space = " " if opening.startswith("\\") else ""
            closing_space = " " if closing.startswith("\\") else ""
            return rf"\left{opening}{opening_space}{body}{closing_space}\right{closing}"
        return f"{opening}{body}{closing}"
    if isinstance(node, Delimited):
        opening = node.opening.for_target(target)
        closing = node.closing.for_target(target)
        separator = node.separator.for_target(target)
        items = separator.join(_emit(item, target) for item in node.items)
        if target == "latex" and node.scalable:
            opening_space = " " if opening.startswith("\\") else ""
            closing_space = " " if closing.startswith("\\") else ""
            return rf"\left{opening}{opening_space}{items}{closing_space}\right{closing}"
        return f"{opening}{items}{closing}"
    if isinstance(node, Equality):
        separator = r" \quad = \quad " if target == "latex" else " = "
        # Teaching display omits parts that become identical only after the
        # selected notation and target have been emitted.
        rendered_parts = dict.fromkeys(_emit(part, target) for part in node.parts)
        return separator.join(rendered_parts)
    raise TypeError(f"unsupported semantic render node {type(node).__name__}")


def _number(value: int | float, target: str, precision: int) -> str:
    if isinstance(value, int):
        return str(value)
    text = format(value, f".{precision}g")
    if target != "latex" or "e" not in text.lower():
        return text
    mantissa, exponent = re.split("[eE]", text)
    normalized_exponent = str(int(exponent))
    if mantissa == "1":
        return rf"10^{{{normalized_exponent}}}"
    if mantissa == "-1":
        return rf"-10^{{{normalized_exponent}}}"
    return rf"{mantissa} \times 10^{{{normalized_exponent}}}"


def _unicode_script(value: str, *, superscript: bool) -> str | None:
    translation = _SUPERSCRIPT if superscript else _SUBSCRIPT
    if all(character in "0123456789+-⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻₀₁₂₃₄₅₆₇₈₉₊₋" for character in value):
        return value.translate(translation)
    return None


def _latex_function(value: str) -> str:
    if value.startswith("\\") or value.startswith("{"):
        return value
    return rf"\operatorname{{{_escape_text(value, 'latex')}}}"


def _escape_text(value: str, target: str) -> str:
    if target == "latex":
        return value.translate(_LATEX_ESCAPE)
    return value


def _accent(node: Accent, target: str) -> str:
    body = _emit(node.body, target)
    accent = node.accent.for_target(target)
    if target == "latex":
        if accent.startswith("\\"):
            return rf"{accent}{{{body}}}"
        command = "underaccent" if node.position == "under" else "overset"
        return rf"\{command}{{{accent}}}{{{body}}}"
    if target == "unicode" and accent and all(unicodedata.combining(character) for character in accent):
        return f"{body}{accent}"
    if target == "ascii" and accent in {"~", "-", "_", "^"}:
        return f"{accent}{body}"
    return f"{accent}({body})"


__all__ = ["emit"]
