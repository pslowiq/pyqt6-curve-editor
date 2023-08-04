from .base import Curve
from scipy import interpolate
import numpy as np
from PyQt6.QtCore import QPointF


def lagrange_interpolation(x, y, x_interp):
    n = len(x)
    m = len(x_interp)
    y_interp = np.zeros(m)

    for i in range(m):
        for j in range(n):
            l = 1.0
            for k in range(n):
                if k != j:
                    l *= (x_interp[i] - x[k]) / (x[j] - x[k])
            y_interp[i] += y[j] * l

    return y_interp


def interpolate_curve_nifs3(x, y, steps=1000):
    if len(x) == 1:
        return list(zip(x, y))
    t = np.arange(len(x))

    splinex = interpolate.splrep(t, x, k=min(len(x) - 1, 3))
    spliney = interpolate.splrep(t, y, k=min(len(x) - 1, 3))

    t_new = np.linspace(0, len(x) - 1, steps)

    x_new = interpolate.splev(t_new, splinex)
    y_new = interpolate.splev(t_new, spliney)

    return list(zip(x_new, y_new))


class NIFS3Curve(Curve):
    def __init__(self, control_points, points_limit=1000, props=None, parent=None):
        super().__init__(control_points, points_limit, props, parent)

    def _get_points(self):
        self._points = [
            QPointF(p[0], p[1])
            for p in interpolate_curve_nifs3(
                [x.x() for x in self.control_points],
                [y.y() for y in self.control_points],
                self.points_limit,
            )
        ]
        return self._points


class LagrangeCurve(Curve):
    def __init__(self, control_points, points_limit=1000, props=None, parent=None):
        super().__init__(control_points, points_limit, props, parent)

    def _get_points(self):
        points = np.array([(x.x(), x.y()) for x in self.control_points])
        x = lagrange_interpolation(
            np.arange(len(points)),
            points[:, 0],
            np.linspace(0, len(points) - 1, self.points_limit),
        )
        y = lagrange_interpolation(
            np.arange(len(points)),
            points[:, 1],
            np.linspace(0, len(points) - 1, self.points_limit),
        )
        self._points = [QPointF(p[0], p[1]) for p in zip(x, y)]
        return self._points
