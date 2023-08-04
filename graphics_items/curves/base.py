from PyQt6.QtCore import QRectF, Qt, QPointF
from PyQt6.QtGui import QPen, QColor, QPainterPath
from PyQt6.QtWidgets import QGraphicsItem

from scipy.spatial import ConvexHull
import numpy as np


class Curve(QGraphicsItem):
    def __init__(self, control_points, points_limit=1000, props=None, parent=None):
        super().__init__()
        self.parent = parent
        self.control_points = control_points
        self.points_limit = points_limit
        self.points = []

        self.point_pen = QPen(QColor(79, 106, 25), 5)
        self.line_pen = QPen(QColor(79, 106, 25), 1)
        if props != None:
            self.point_pen.setColor(QColor.fromRgb(*props["point_color"]))
            self.point_pen.setWidth(props["point_size"])
            self.line_pen.setColor(QColor.fromRgb(*props["line_color"]))
            self.line_pen.setWidth(props["line_size"])

        self.leftmost_x = 0.0
        self.rightmost_x = 0.0
        self.highest_y = 0.0
        self.lowest_y = 0.0

        self.show_bounding_rect = False
        self.show_control_line = False
        self.show_convex_hull = False
        self.show_points = True
        self.closed = False

        self.current_rotation = None

        self.bounding_cords = [
            self.leftmost_x,
            self.rightmost_x,
            self.highest_y,
            self.lowest_y,
        ]

    def boundingRect(self):
        return QRectF(
            self.leftmost_x,
            self.highest_y,
            abs(self.leftmost_x - self.rightmost_x),
            abs(self.highest_y - self.lowest_y),
        )

    def paint(self, painter, option, widget=None):
        if self.control_points:
            painter.setPen(self.point_pen)
            painter.setBrush(self.point_pen.brush())
            if self.show_points:
                painter.drawPoints(self.control_points)

            painter.setPen(self.line_pen)
            painter.setBrush(self.line_pen.brush())

            self._get_points()

            path = QPainterPath(self._points[0])
            for i in range(1, len(self._points)):
                path.lineTo(self._points[i])
            painter.strokePath(path, self.line_pen)

            if self.show_bounding_rect:
                painter.drawPoint(self.boundingRect().center())
                painter.drawRect(self.boundingRect())

            if self.show_control_line:
                self.paint_control_curve(painter)

            if self.show_convex_hull:
                self.paint_convex_hull(painter)

    def _get_points(self):
        self._points = self.control_points
        return self.control_points

    def paint_control_curve(self, painter):

        painter.setPen(QPen(QColor(255, 120, 65), 1))
        for i in range(1, len(self.control_points)):
            painter.drawLine(self.control_points[i - 1], self.control_points[i])

    def paint_convex_hull(self, painter):
        if len(self.control_points) < 3:
            return
        hull = ConvexHull(
            [
                (self.control_points[i].x(), self.control_points[i].y())
                for i in range(len(self.control_points))
            ]
        )
        painter.setPen(QPen(QColor(178, 34, 34), 1))
        for i in range(len(hull.vertices)):
            painter.drawLine(
                self.control_points[hull.vertices[i - 1]],
                self.control_points[hull.vertices[i]],
            )

    def rotate_points(self, target_deg):
        if self.current_rotation == None:
            self.current_rotation = target_deg
        else:
            temp = target_deg
            diff = self.current_rotation - target_deg
            target_deg = diff
            self.current_rotation = temp
        cp = np.array(
            [self.boundingRect().center().x(), self.boundingRect().center().y()]
        )
        points = np.array([(x.x(), x.y()) for x in self.control_points])
        angle_rad = np.radians(target_deg)

        translated_points = points - cp

        rotated_points = np.empty_like(translated_points)
        rotated_points[:, 0] = translated_points[:, 0] * np.cos(
            angle_rad
        ) - translated_points[:, 1] * np.sin(angle_rad)
        rotated_points[:, 1] = translated_points[:, 0] * np.sin(
            angle_rad
        ) + translated_points[:, 1] * np.cos(angle_rad)

        rotated_points += cp

        self.control_points = [QPointF(p[0], p[1]) for p in rotated_points]
        self.update()

        return

    def add_control_point(self, point):

        if len(self.control_points) == 0:
            self.leftmost_x = point.x()
            self.rightmost_x = point.x()
            self.highest_y = point.y()
            self.lowest_y = point.y()

        self.leftmost_x = min(self.leftmost_x, point.x())
        self.rightmost_x = max(self.rightmost_x, point.x())
        self.highest_y = min(self.highest_y, point.y())
        self.lowest_y = max(self.lowest_y, point.y())

        self.control_points.append(point)

    def add_diff(self, diff, diff_x, diff_y):
        for i in range(len(self.control_points)):
            self.control_points[i] += diff

        self.leftmost_x += diff_x
        self.rightmost_x += diff_x
        self.highest_y += diff_y
        self.lowest_y += diff_y

    def get_type(self):
        return self.name.split("-")[1]

    def get_id(self):
        return self.name.split("-")[0]
