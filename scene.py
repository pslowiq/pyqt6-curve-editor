from PyQt6.QtCore import pyqtSignal

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem
from config import NAME_TO_CURVE_CLASS
from math import degrees, atan2


class EditorScene(QGraphicsScene):

    update_occured = pyqtSignal()

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent=parent)
        self.object_mapping = {}
        self.current_object = None
        self.image = None

    def update_mode(self, mode):
        self.current_mode = mode
        self.moving = False
        self.rotating = False

    def add_object(self, name, control_points=None, props=None):
        curve_type = name.split("-")[1]
        if control_points == None:
            obj = NAME_TO_CURVE_CLASS[curve_type]([], props=props, parent=self)
        else:
            obj = NAME_TO_CURVE_CLASS[curve_type](
                control_points, props=props, parent=self
            )

        self.current_object = obj
        self.current_object.name = name
        self.addItem(self.current_object)
        self.parent().ui.objects_widget.addItem(name)
        self.object_mapping[name] = obj

    def mousePressEvent(self, event: QMouseEvent) -> None:

        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.current_mode == "Add curve points"
        ):
            pos = event.scenePos()
            self.current_object.add_control_point(pos)
            self.update()

        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.current_mode == "Edit curve points"
        ):
            self.origin = event.scenePos()
            for object in self.items():
                if type(object) == QGraphicsPixmapItem:
                    continue
                for i, point in enumerate(object.control_points):
                    diff = self.origin - point

                    if diff.manhattanLength() < 3:
                        self.selected_point_index = i
                        self.current_object = object
                        self.moving = True
                        break

        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.current_mode == "Remove curve points"
        ):
            self.origin = event.scenePos()
            found = False
            for object in self.items():
                if type(object) == QGraphicsPixmapItem:
                    continue
                for i, point in enumerate(object.control_points):
                    diff = self.origin - point

                    if diff.manhattanLength() < 3:
                        self.selected_point_index = i
                        self.current_object = object
                        found = True
                        break
            if found:
                self.current_object.control_points.pop(self.selected_point_index)
                self.update()

        if event.button() == Qt.MouseButton.LeftButton and self.current_mode == "Move":
            self.moving = True
            self.origin = event.scenePos()

        if event.button() == Qt.MouseButton.RightButton and self.current_mode == "Move":
            self.rotating = True
            self.origin = event.scenePos()

    def mouseMoveEvent(self, event):
        if self.moving and self.current_mode == "Move":
            pos = event.scenePos()
            diff = pos - self.origin
            diff_x = pos.x() - self.origin.x()
            diff_y = pos.y() - self.origin.y()

            self.current_object.add_diff(diff, diff_x, diff_y)
            self.update()
            self.origin = event.scenePos()

        if self.moving and self.current_mode == "Edit curve points":
            self.current_object.control_points[self.selected_point_index] += (
                event.scenePos() - self.origin
            )
            self.origin = event.scenePos()
            self.update()

        if self.rotating and self.current_mode == "Move":
            delta = event.scenePos() - self.origin
            rotation_angle = degrees(atan2(delta.y(), delta.x()))
            self.current_rotation = rotation_angle
            self.current_object.rotate_points(rotation_angle)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if (self.rotating or self.moving) and (
            self.current_mode == "Move" or self.current_mode == "Edit curve points"
        ):
            self.update()
            self.moving = False
            self.rotating = False

        super().mouseReleaseEvent(event)

    def remove_current_object(self):
        del self.object_mapping[self.current_object.name]
        self.parent().ui.objects_widget.takeItem(
            self.parent().ui.objects_widget.row(
                self.parent().ui.objects_widget.findItems(
                    self.current_object.name, Qt.MatchFlag.MatchExactly
                )[0]
            )
        )
        self.removeItem(self.current_object)
        self.current_object = None
        self.update()
        self.parent().mode.switch_mode("None")

    def remove_all_objects(self):
        to_del = list(self.object_mapping.keys())
        for item in to_del:
            self.current_object = self.object_mapping[item]
            self.current_object.update()
            self.remove_current_object()
        self.parent().internal_counter = 0
        self.remove_image()

    def remove_image(self):
        if self.image != None:
            self.removeItem(self.image)
            self.image = None

    def remove_object(self, obj):
        if self.current_object == obj:
            self.current_object = None
        del self.object_mapping[obj.name]
        self.parent().ui.objects_widget.takeItem(
            self.parent().ui.objects_widget.row(
                self.parent().ui.objects_widget.findItems(
                    obj.name, Qt.MatchFlag.MatchExactly
                )[0]
            )
        )
        self.removeItem(obj)
        self.update()

    def update(self):
        super().update(self.sceneRect())
        self.update_occured.emit()
