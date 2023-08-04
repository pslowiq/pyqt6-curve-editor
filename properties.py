from PyQt6.QtCore import Qt, QModelIndex, QVariant, QAbstractItemModel, QPointF
from PyQt6.QtGui import QColor


class CurvePropertiesModel(QAbstractItemModel):
    def __init__(self, curve=None, parent=None):
        super().__init__()
        self.parentt = parent
        if curve != None:
            self.properties = [
                ("Name", curve.name),
                ("Points limit", curve.points_limit),
                ("Line Color", curve.line_pen.color()),
                ("Line Width", curve.line_pen.width()),
                ("Marker Color", curve.point_pen.color()),
                ("Marker Size", curve.point_pen.width()),
                ("Points:", ""),
                *[
                    (
                        "point" + str(i),
                        str((curve.control_points[i].x(), curve.control_points[i].y())),
                    )
                    for i in range(len(curve.control_points))
                ],
            ]
        else:
            self.properties = []

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            return self.createIndex(row, column, None)

        return QModelIndex()

    def parent(self, index):
        return QModelIndex()

    def rowCount(self, parent=QModelIndex()):
        if not parent.isValid():
            return len(self.properties)

        return 0

    def columnCount(self, parent=QModelIndex()):
        return 2

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return QVariant()

        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            if index.column() == 0:
                return self.properties[index.row()][0]
            elif index.column() == 1:
                return self.properties[index.row()][1]

        return QVariant()

    def setCurve(self, curve):
        if curve == None:
            self.properties = []
            self.curve = None
            return
        self.curve = curve

        self.properties = [
            ("Name", curve.name),
            ("Type", curve.get_type()),
            ("Points limit", curve.points_limit),
            ("Line Color", curve.line_pen.color()),
            ("Line Width", curve.line_pen.width()),
            ("Marker Color", curve.point_pen.color()),
            ("Marker Size", curve.point_pen.width()),
            ("Show Control Line", curve.show_control_line),
            ("Show Convex Hull", curve.show_convex_hull),
            ("Show Control Points", curve.show_points),
            ("Points:", ""),
            *[
                (
                    "control_point" + str(i),
                    str((curve.control_points[i].x(), curve.control_points[i].y())),
                )
                for i in range(len(curve.control_points))
            ],
        ]
        if self.curve.get_type() == "WeightedBezier" and len(curve.weights):
            self.properties.append(("Weights:", ""))
            self.properties.extend(
                [
                    (
                        "weight" + str(i),
                        str((curve.weights[i])),
                    )
                    for i in range(len(curve.weights))
                ]
            )

        if "BSpline" in self.curve.get_type():
            self.properties.append(("Degree", curve.degree))

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if index.isValid() and role == Qt.ItemDataRole.EditRole:
            row = index.row()
            if 0 <= row < len(self.properties):
                property_name, old_value = self.properties[row]
                self.properties[row] = (property_name, value)
                self.dataChanged.emit(index, index, [role])

                if self.curve is not None:
                    if property_name == "Name":
                        self.curve.name = value
                    elif property_name == "Points limit":
                        self.curve.points_limit = value
                    elif property_name == "Line Color":
                        self.curve.line_pen.setColor(QColor.fromString(value))
                    elif property_name == "Line Width":
                        self.curve.line_pen.setWidth(int(value))
                    elif property_name == "Marker Color":
                        self.curve.point_pen.setColor(QColor.fromString(value))
                    elif property_name == "Marker Size":
                        self.curve.point_pen.setWidth(int(value))
                    elif property_name == "Show Convex Hull":
                        self.curve.show_convex_hull = bool(value)
                    elif property_name == "Show Control Line":
                        self.curve.show_control_line = bool(value)
                    elif property_name == "Show Control Points":
                        self.curve.show_points = bool(value)
                    elif property_name == "Degree":
                        self.curve.degree = int(value)
                    elif property_name == "Type":
                        cp = self.curve.control_points.copy()
                        name = self.curve.get_id() + "-" + value
                        self.parentt.scene.remove_current_object()
                        self.parentt.scene.add_object(name, cp)
                        self.curve = self.parentt.scene.current_object
                        self.parentt.ui.update()
                    elif "control_point" in property_name:
                        value = eval(value)
                        self.curve.control_points[int(property_name[5:])] = QPointF(
                            value[0], value[1]
                        )
                    elif "weight" in property_name:
                        value = eval(value)
                        self.curve.change_weight(int(property_name[6:]), value)

                    self.curve.update()

                return True

        return False

    def flags(self, index):
        default_flags = super().flags(index)
        if index.isValid() and index.column() == 1:
            return default_flags | Qt.ItemFlag.ItemIsEditable
        return default_flags
