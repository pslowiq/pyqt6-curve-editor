from .base import Curve
from scipy.special import comb
import numpy as np
from PyQt6.QtGui import QPen, QColor
from PyQt6.QtCore import QPointF


def bernstein(n, i, t):
    return comb(n, i) * (t ** (n - i)) * (1 - t) ** i


def bezier_curve(points, steps=1000):

    n = len(points)
    t = np.linspace(0.0, 1.0, steps)
    bernstein_polynomials = np.array(
        [bernstein(n - 1, i, t) for i in range(n - 1, -1, -1)]
    )

    x_new = np.dot(points[:, 0], bernstein_polynomials)
    y_new = np.dot(points[:, 1], bernstein_polynomials)

    return list(zip(x_new, y_new))


def weighted_bezier_curve(points, weights, steps=1000):

    n = len(points)
    t = np.linspace(0.0, 1.0, steps)
    weighted_bernstein = np.array(
        [bernstein(n - 1, i, t) * weights[n - 1 - i] for i in range(n - 1, -1, -1)]
    )

    sum_weighted_bernstein = np.sum(weighted_bernstein, axis=0)

    x_new = np.divide(np.dot(points[:, 0], weighted_bernstein), sum_weighted_bernstein)
    y_new = np.divide(np.dot(points[:, 1], weighted_bernstein), sum_weighted_bernstein)

    return list(zip(x_new, y_new))


def de_casteljau(points, t, get_coeffs=False):
    n = len(points) - 1
    coefficients = [points.copy()]

    for j in range(1, n + 1):
        prev_points = coefficients[-1]
        new_points = np.zeros((n - j + 1, prev_points.shape[1]))

        for i in range(n - j + 1):
            new_points[i] = (1 - t) * prev_points[i] + t * prev_points[i + 1]

        coefficients.append(new_points)

    if get_coeffs:
        return coefficients

    return coefficients[-1][0]


def de_casteljau_curve(points, steps=1000):

    t = np.linspace(0.0, 1.0, steps)
    ret = [de_casteljau(points, t_) for t_ in t]

    return list(ret)


def get_cubic_bezier_coef(points):
    n = len(points) - 1

    C = 4 * np.identity(n)
    np.fill_diagonal(C[1:], 1)
    np.fill_diagonal(C[:, 1:], 1)
    C[0, 0] = 2
    C[n - 1, n - 1] = 7
    C[n - 1, n - 2] = 2

    P = [2 * (2 * points[i] + points[i + 1]) for i in range(n)]
    P[0] = points[0] + 2 * points[1]
    P[n - 1] = 8 * points[n - 1] + points[n]

    A = np.linalg.solve(C, P)
    B = [0] * n
    for i in range(n - 1):
        B[i] = 2 * points[i + 1] - A[i + 1]
    B[n - 1] = (A[n - 1] + points[n]) / 2

    return A, B


import numpy as np


def combine_bezier_curves(curve1, curve2, c=2):

    n = curve1.shape[0]
    m = curve2.shape[0]

    if c == 0:
        return np.concatenate((curve1[-1:], curve2[1:]))

    if c == 1:
        pn = curve1[-1]
        pn_1 = curve1[-2]

        q0 = pn
        q1 = ((m + n) * pn - n * pn_1) / m

        return np.concatenate(([q0, q1], curve2[2:]))

    if c == 2:
        pn = curve1[-1]
        pn_1 = curve1[-2]
        pn_2 = curve1[-3]

        q0 = curve2[0]
        q1 = curve2[1]
        q2 = curve2[2]

        pn = curve1[-1]
        pn_1 = curve1[-2]

        q0 = pn
        q1 = ((m + n) * pn - n * pn_1) / m
        q2 = (
            (n - 1) * (n * pn - 2 * n * pn_1 + n * pn_2)
            + (2 * m * m - 2 * m) * q1
            - (m * m - m) * q0
        )
        q2 = q2 / (m * m - m)

        return np.concatenate(([q0, q1, q2], curve2[3:]))


class BezierCurve(Curve):
    def __init__(self, control_points, points_limit=1000, props=None, parent=None):
        super().__init__(control_points, points_limit, props, parent)

    def _get_points(self):
        points = np.array([(x.x(), x.y()) for x in self.control_points])
        self._points = [
            QPointF(p[0], p[1]) for p in bezier_curve(points, self.points_limit)
        ]
        return self._points

    def elevate_degree(self):
        n = len(self.control_points)
        new_points = [self.control_points[0]]
        for i in range(1, n):
            new_points.append(
                i / n * self.control_points[i - 1]
                + (1 - i / n) * self.control_points[i]
            )
        new_points.append(self.control_points[n - 1])
        self.control_points = new_points
        self.update(self.boundingRect())

    def reduce_degree(self):
        control_points = self.control_points
        n = len(control_points)

        M = np.zeros((n, n - 1))
        B = np.array([(x.x(), x.y()) for x in self.control_points])
        M[0, 0] = 1
        M[n - 1, n - 2] = 1
        for i in range(n - 1):
            M[i, i - 1] = i / n
            M[i, i] = 1 - i / n

        B_0 = np.linalg.solve(M.T @ M, M.T @ B)

        self.control_points = [
            self.control_points[0],
            *[QPointF(p[0], p[1]) for p in B_0[1:-1]],
            self.control_points[-1],
        ]
        self.update(self.boundingRect())

    def reduce_degree2(self):
        control_points = self.control_points
        n = len(control_points) - 1
        new_control_points = [control_points[0]]

        for i in range(1, n - 1):
            t = i / n
            new_point = (1 - t) * control_points[i] + t * control_points[i + 1]
            new_control_points.append(new_point)

        new_control_points.append(control_points[-1])
        self.control_points = new_control_points
        self.update(self.boundingRect())

    def get_split_points(self, u=0.5):
        points = np.array([(x.x(), x.y()) for x in self.control_points])
        coeffs = de_casteljau(points, u, get_coeffs=True)
        left, right = [], []
        n = len(coeffs)
        for i in range(n):
            left.append(coeffs[i][0])
            right.append(coeffs[i][len(coeffs) - 1 - i])

        return [QPointF(p[0], p[1]) for p in left], [QPointF(p[0], p[1]) for p in right]

    def merge_bezier_curves(self, other, continuity=2):
        points1 = np.array([(x.x(), x.y()) for x in self.control_points])
        points2 = np.array([(x.x(), x.y()) for x in other.control_points])
        new_points = combine_bezier_curves(points1, points2, c=continuity)
        return [QPointF(p[0], p[1]) for p in new_points]

    def join_bezier_curves(self, other, continuity=2):
        points1 = np.array([(x.x(), x.y()) for x in self.control_points])
        points2 = np.array([(x.x(), x.y()) for x in other.control_points])
        new_points = combine_bezier_curves(points1, points2, c=continuity)
        other.control_points = [QPointF(p[0], p[1]) for p in new_points]
        other.update()
        return


class WeightedBezierCurve(Curve):
    def __init__(self, control_points, points_limit=1000, props=None, parent=None):
        super().__init__(control_points, points_limit, props, parent)
        self.weights = np.ones(len(control_points))

    def add_control_point(self, point):
        super().add_control_point(point)
        self.weights = np.append(self.weights, 1)

    def _get_points(self):
        points = np.array([(x.x(), x.y()) for x in self.control_points])
        self._points = [
            QPointF(p[0], p[1])
            for p in weighted_bezier_curve(points, self.weights, self.points_limit)
        ]
        return self._points

    def change_weight(self, idx, value):
        self.weights[idx] = value

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)

    def elevate_degree(self):
        n = len(self.control_points)

        new_weights = [self.weights[0]]
        for i in range(1, n):
            new_weights.append(
                i / n * self.weights[i - 1] + (1 - i / n) * self.weights[i]
            )
        new_weights.append(self.weights[n - 1])

        new_points = [self.control_points[0]]
        for i in range(1, n):
            new_points.append(
                (
                    (i / n) * self.weights[i - 1] * self.control_points[i - 1]
                    + (1 - i / n) * self.weights[i] * self.control_points[i]
                )
                / (self.weights[i - 1] * (i / n) + (1 - i / n) * self.weights[i])
            )
        new_points.append(self.control_points[n - 1])

        self.control_points = new_points
        self.weights = np.array(new_weights)
        self.update(self.boundingRect())

    def reduce_degree(self):
        new_points = [self.control_points[0]]
        new_weights = [self.weights[0]]

        for i in range(1, len(self.control_points) - 2):
            alpha = self.weights[i] / (self.weights[i] + self.weights[i + 1])
            new_control_point = (
                alpha * self.control_points[i]
                + (1 - alpha) * self.control_points[i + 1]
            )
            new_weight = self.weights[i] + self.weights[i + 1]
            new_points.append(new_control_point)
            new_weights.append(new_weight)

        new_points.append(self.control_points[-1])
        new_weights.append(self.weights[-1])

        self.control_points = new_points
        self.weights = np.array(new_weights)
        self.update(self.boundingRect())

    def reduce_degree(self):
        control_points = self.control_points
        new_weights = [self.weights[0]]
        n = len(control_points)

        M = np.zeros((n, n - 1))
        B = np.array([(x.x(), x.y()) for x in self.control_points])
        M[0, 0] = self.weights[0]
        M[n - 1, n - 2] = self.weights[-1]
        for i in range(0, n - 1):
            M[i, i - 1] = i / n * self.weights[i - 1]
            M[i, i] = 1 - (i / n) * self.weights[i]
            new_weights.append(
                i / n * self.weights[i - 1] + 1 - (i / n) * self.weights[i]
            )

        B_0 = np.linalg.solve(M.T @ M, M.T @ B)

        self.control_points = [
            self.control_points[0],
            *[QPointF(p[0], p[1]) for p in B_0[1:-1]],
            self.control_points[-1],
        ]
        self.weights = np.array(new_weights)
        self.update(self.boundingRect())


class CubicBezierInterpCurve(Curve):
    def __init__(self, control_points, points_limit=1000, props=None, parent=None):
        super().__init__(control_points, points_limit, props, parent)
        self._control_points = [x for x in control_points]

        self.show_weight_points = True

        self.weight_point_pen = QPen(QColor(155, 155, 55), 5)
        self.weight_point_brush = QColor(122, 163, 39)

    def add_control_point(self, point):

        if len(self._control_points) == 0:
            self.leftmost_x = point.x()
            self.rightmost_x = point.x()
            self.highest_y = point.y()
            self.lowest_y = point.y()

        self.leftmost_x = min(self.leftmost_x, point.x())
        self.rightmost_x = max(self.rightmost_x, point.x())
        self.highest_y = min(self.highest_y, point.y())
        self.lowest_y = max(self.lowest_y, point.y())

        self._control_points.append(point)
        if len(self._control_points) > 1:
            self.control_points.clear()
            points = np.array([(x.x(), x.y()) for x in self._control_points])
            A, B = get_cubic_bezier_coef(points)
            for i in range(len(self._control_points) - 1):
                self.control_points.extend(
                    [
                        QPointF(p[0], p[1])
                        for p in [points[i], A[i], B[i], points[i + 1]]
                    ]
                )

    def _get_points(self):
        n = len(self.control_points)
        points = np.array([(x.x(), x.y()) for x in self.control_points])
        if n > 1:
            ret = []
            points_per_segment = self.points_limit // ((n) // 3)
            for i in range(0, n, 4):
                ret.extend(
                    bezier_curve(np.array(points[i : i + 4]), points_per_segment)
                )
            self._points = [QPointF(p[0], p[1]) for p in ret]
        else:
            self._points = self.control_points
        return self._points
