"""Permanent package and dependency-direction contracts for the numeric core."""

from __future__ import annotations

import runpy
from importlib.metadata import requires
from importlib.resources import files
from pathlib import Path

import galaga.core as core
import galaga.facade as facade
from galaga import Algebra as PublicAlgebra

ARCHITECTURE = runpy.run_path(str(Path(__file__).parents[1] / "facade/test_architecture_contracts.py"))


def test_top_level_algebra_is_the_promoted_facade() -> None:
    """One public wrapper owns a presentation-independent core value."""
    assert PublicAlgebra is not core.Algebra
    assert PublicAlgebra is facade.Algebra
    assert PublicAlgebra.__module__ == "galaga.facade._numeric"
    assert core.Algebra.__module__ == "galaga.core"
    numeric = core.Algebra(2)
    public = PublicAlgebra.from_numeric(numeric)
    assert public.numeric is numeric and public.blade(1).numeric.algebra is numeric


def test_core_source_does_not_import_outer_galaga_modules() -> None:
    """Inspect nested resources and zipped wheels, not just flat source files."""
    sources = list(ARCHITECTURE["python_sources"](files("galaga.core"), "galaga.core"))
    assert sources
    for _module, package, source in sources:
        ARCHITECTURE["assert_core_only_imports"](source, package)


def test_distribution_has_no_external_gram_dependency() -> None:
    """The core is part of Galaga's distribution rather than another package."""
    requirements = requires("galaga") or []
    assert not any(requirement.lower().startswith("gram") for requirement in requirements)
