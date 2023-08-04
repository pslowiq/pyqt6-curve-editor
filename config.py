from graphics_items.curves.base import Curve
from graphics_items.curves.interpolated import NIFS3Curve, LagrangeCurve
from graphics_items.curves.bezier import (
    BezierCurve,
    CubicBezierInterpCurve,
    WeightedBezierCurve,
)
from graphics_items.curves.bspline import BSpline, BSplineDeBoor

NAME_TO_CURVE_CLASS = {
    "Control": Curve,
    "NIFS3": NIFS3Curve,
    "Bezier": BezierCurve,
    "WeightedBezier": WeightedBezierCurve,
    "CubicBezierInterp": CubicBezierInterpCurve,
    "LagrangeCurve": LagrangeCurve,
    "BSpline": BSpline,
    "BSplineDeBoor": BSplineDeBoor,
}
