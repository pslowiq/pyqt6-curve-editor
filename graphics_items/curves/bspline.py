from .base import Curve
from scipy.special import comb
import numpy as np
from PyQt6.QtGui import QPen, QColor
from PyQt6.QtCore import QPointF


def bspline(control_points, degree, points_limit=1000):
    def basis_function(i, p, u, knots):
        left = 0.0
        right = 0.0
        if p == 0:
            if knots[i] <= u and u < knots[i + 1]:
                return 1
            else:
                return 0
        if (knots[i + p] - knots[i]) != 0.0:
            left = (
                (u - knots[i])
                / (knots[i + p] - knots[i])
                * basis_function(i, p - 1, u, knots)
            )
        if (knots[i + p + 1] - knots[i + 1]) != 0.0:
            right = (
                (knots[i + p + 1] - u)
                / (knots[i + p + 1] - knots[i + 1])
                * basis_function(i + 1, p - 1, u, knots)
            )

        return left + right

    def b_spline_eval(t):
        knot_vector = np.linspace(0, 1, len(control_points) - degree + 1)
        knot_vector = np.concatenate(
            ([knot_vector[0]] * (degree), knot_vector, [knot_vector[-1]] * (degree))
        )

        curve_point = np.zeros_like(control_points[0])
        for i in range(len(control_points)):
            basis = basis_function(i, degree, t, knot_vector)
            curve_point += control_points[i] * basis

        return curve_point

    return b_spline_eval


def de_boor(control_points, degree, points_limit=1000):
    def basis_function(i, p, u, knots):
        left = 0.0
        right = 0.0
        if p == 0:
            if knots[i] <= u and u < knots[i + 1]:
                return 1
            else:
                return 0
        if (knots[i + p] - knots[i]) != 0.0:
            left = (
                (u - knots[i])
                / (knots[i + p] - knots[i])
                * basis_function(i, p - 1, u, knots)
            )
        if (knots[i + p + 1] - knots[i + 1]) != 0.0:
            right = (
                (knots[i + p + 1] - u)
                / (knots[i + p + 1] - knots[i + 1])
                * basis_function(i + 1, p - 1, u, knots)
            )

        return left + right

    def deBoor(k: int, x: int, t, c, p: int):
        d = [c[j + k - p] for j in range(0, p + 1)]

        for r in range(1, p + 1):
            for j in range(p, r - 1, -1):
                alpha = (x - t[j + k - p]) / (t[j + 1 + k - r] - t[j + k - p])
                d[j] = (1.0 - alpha) * d[j - 1] + alpha * d[j]

        return d[p]

    def find_interval(t, knots):
        if t == 1.0:
            return len(control_points) - 1
        for i in range(len(knots) - 1):
            if knots[i] <= t and knots[i + 1] > t:
                return i

    def b_spline_eval(t):
        knot_vector = np.linspace(0, 1, len(control_points) - degree + 1)
        knot_vector = np.concatenate(
            ([knot_vector[0]] * (degree), knot_vector, [knot_vector[-1]] * (degree))
        )

        curve_point = np.array(
            deBoor(
                find_interval(t, knot_vector), t, knot_vector, control_points, degree
            )
        )

        return curve_point

    return b_spline_eval


class BSplineDeBoor(Curve):
    def __init__(self, control_points, points_limit=1000, props=None, parent=None):
        super().__init__(control_points, points_limit, props, parent)
        self.degree = 3

    def _get_points(self):
        if len(self.control_points) < self.degree + 1:
            self._points = self.control_points.copy()
            return self._points
        points = np.array([(x.x(), x.y()) for x in self.control_points])
        fun = de_boor(points, self.degree)
        t = np.linspace(0.0, 1.0, self.points_limit)
        self._points = []

        for i in range(len(t)):
            p = fun(t[i])
            self._points.append(QPointF(p[0], p[1]))

        self._points = self._points[:-1]
        return self._points[:-1]


class BSpline(Curve):
    def __init__(self, control_points, points_limit=1000, props=None, parent=None):
        super().__init__(control_points, points_limit, props, parent)
        self.degree = 3

    def _get_points(self):
        if len(self.control_points) < self.degree + 1:
            self._points = self.control_points.copy()
            return self._points
        points = np.array([(x.x(), x.y()) for x in self.control_points])
        fun = bspline(points, self.degree)
        t = np.linspace(0.0, 1.0, self.points_limit)
        self._points = []

        for i in range(len(t)):
            p = fun(t[i])
            # if p[0] != 0 and p[1] != 0:
            self._points.append(QPointF(p[0], p[1]))

        self._points = self._points[:-1]
        return self._points[:-1]
