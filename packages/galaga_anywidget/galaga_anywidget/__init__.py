"""Interactive AnyWidget visualizations for Galaga geometric algebra."""

from . import viz
from .cga2d import DEFAULT_COLOR_CYCLE, CGA2DChange, CGA2DKind, CGA2DLineStyle, CGA2DPlot, cga2d
from .oblique2d import Oblique2DPlot, oblique2d
from .viz import CGA2D

__all__ = [
    "CGA2DKind",
    "CGA2DLineStyle",
    "CGA2DChange",
    "CGA2DPlot",
    "CGA2D",
    "DEFAULT_COLOR_CYCLE",
    "cga2d",
    "Oblique2DPlot",
    "oblique2d",
    "viz",
]
