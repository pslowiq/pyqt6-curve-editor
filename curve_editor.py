from scene import EditorScene
from view import EditorView
from ui import EditorUI
from mode import EditorMode
from properties import CurvePropertiesModel


from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QInputDialog
import sys


class EditorWindow(QMainWindow):
    def __init__(self, ui):
        super().__init__()
        self.setWindowTitle("Curve Editor v0")
        self.setCentralWidget(ui)


class CurveEditor(QApplication):
    def __init__(self, argv) -> None:

        super().__init__(argv)
        self.mode = EditorMode()
        self.view = EditorView()
        self.scene = EditorScene(-800, -500, 1600, 1000, parent=self)
        self.view.setScene(self.scene)
        self.ui = EditorUI(self.view, self.scene)
        self.main_window = EditorWindow(self.ui)
        self.internal_counter = 0
        self.model = CurvePropertiesModel(None, self)
        self.ui.properties_widget.setModel(self.model)
        self.ui.properties_widget.setColumnWidth(0, 140)
        self.ui.properties_widget.setColumnWidth(1, 50)

        self.mode.mode_changed.connect(self.scene.update_mode)
        self.mode.mode_changed.connect(
            lambda: self.ui.mode_label.setText("MODE: " + self.mode.current_mode)
        )

        self.ui.remove_object_signal.connect(
            lambda: self.remove_object_handler(self.scene.current_object)
        )
        self.ui.add_points_signal.connect(
            lambda: self.mode.switch_mode("Add curve points")
        )
        self.ui.edit_points_signal.connect(
            lambda: self.mode.switch_mode("Edit curve points")
        )
        self.ui.remove_points_signal.connect(
            lambda: self.mode.switch_mode("Remove curve points")
        )
        self.ui.elevate_degree_signal.connect(lambda: self.elevate_degree_handler())
        self.ui.reduce_degree_signal.connect(lambda: self.reduce_degree_handler())
        self.ui.add_curve_signal.connect(lambda: self.curve_added())
        self.ui.objects_widget.itemSelectionChanged.connect(
            self.change_object_selection
        )
        self.ui.move_signal.connect(self.move_signal_handler)
        self.ui.split_signal.connect(self.split_handler)
        self.ui.merge_signal.connect(self.merge_handler)
        self.ui.join_signal.connect(self.join_handler)

        self.scene.update_occured.connect(self.move_handler)

        self.mode.switch_mode("None")
        self.main_window.setWindowState(Qt.WindowState.WindowMaximized)
        self.main_window.show()
        sys.exit(self.exec())

    def move_signal_handler(self):
        self.mode.switch_mode("Move")

    def remove_object_handler(self, obj):
        current_object = obj
        if current_object:
            # name = current_object.name
            self.model.setCurve(None)
            self.mode.switch_mode("None")
            self.ui.update()
            self.scene.remove_object(current_object)

    def elevate_degree_handler(self):
        if self.scene.current_object != None:
            if self.scene.current_object.name.split("-")[1] in [
                "Bezier",
                "WeightedBezier",
            ]:
                self.scene.current_object.elevate_degree()

    def reduce_degree_handler(self):
        if self.scene.current_object != None:
            if self.scene.current_object.name.split("-")[1] in [
                "Bezier",
                "WeightedBezier",
            ]:
                self.scene.current_object.reduce_degree()

    def split_handler(self):
        if self.scene.current_object != None:
            if self.scene.current_object.name.split("-")[1] == "Bezier":
                num, ok = QInputDialog.getDouble(
                    self.view,
                    "Split value",
                    f"Select split",
                    value=0.5,
                    min=0.0,
                    max=1.0,
                    step=0.01,
                )
                left, right = self.scene.current_object.get_split_points(u=num)
                self.remove_object_handler(self.scene.current_object)
                name1 = str(self.internal_counter) + "-Bezier"
                name2 = str(self.internal_counter + 1) + "-Bezier"
                self.scene.add_object(name1, left)
                self.scene.add_object(name2, right)
                self.model.setCurve(self.scene.current_object)
                self.internal_counter += 2

    def merge_handler(self):
        if self.scene.current_object != None:
            if self.scene.current_object.name.split("-")[1] == "Bezier":
                items = list(self.scene.object_mapping.keys())
                items.remove(self.scene.current_object.name)
                selected_item, ok = QInputDialog.getItem(
                    self.view,
                    "Select Item",
                    f"Select curve to merge {self.scene.current_object.name} with:",
                    items,
                    0,
                    False,
                )
                num, ok = QInputDialog.getInt(
                    self.view,
                    "Select value",
                    f"Select continuity",
                    value=0,
                    min=0,
                    max=2,
                    step=1,
                )
                if ok and selected_item:
                    if selected_item.split("-")[1] != "Bezier":
                        return
                n1, n2 = self.scene.current_object.name, selected_item
                b1, b2 = self.scene.object_mapping[n1], self.scene.object_mapping[n2]

                new_points = b1.merge_bezier_curves(b2, num)
                self.remove_object_handler(self.scene.object_mapping[n1])
                self.remove_object_handler(self.scene.object_mapping[n2])
                name1 = str(self.internal_counter) + "-Bezier"
                self.scene.add_object(name1, new_points)
                self.model.setCurve(self.scene.current_object)
                self.internal_counter += 1

    def join_handler(self):
        if self.scene.current_object != None:
            if self.scene.current_object.name.split("-")[1] == "Bezier":
                items = list(self.scene.object_mapping.keys())
                items.remove(self.scene.current_object.name)
                selected_item, ok = QInputDialog.getItem(
                    self.view,
                    "Select Item",
                    f"Select curve to merge {self.scene.current_object.name} with:",
                    items,
                    0,
                    False,
                )
                num, ok = QInputDialog.getInt(
                    self.view,
                    "Select value",
                    f"Select continuity",
                    value=0,
                    min=0,
                    max=2,
                    step=1,
                )
                if ok and selected_item:
                    if selected_item.split("-")[1] != "Bezier":
                        return
                n1, n2 = self.scene.current_object.name, selected_item
                b1, b2 = self.scene.object_mapping[n1], self.scene.object_mapping[n2]

                new_points = b1.join_bezier_curves(b2, num)

    def move_handler(self):
        self.model.setCurve(self.scene.current_object)
        self.model.layoutChanged.emit()

    def change_object_selection(self):
        if len(self.scene.object_mapping.keys()) > 0:
            obj = None
            if len(self.ui.objects_widget.selectedIndexes()):
                obj = self.scene.object_mapping[
                    self.ui.objects_widget.selectedIndexes()[0].data()
                ]
                self.scene.current_object = obj
                self.model.setCurve(self.scene.current_object)
                self.model.layoutChanged.emit()
                self.mode.switch_mode("Move")

    def curve_added(self):
        name = str(self.internal_counter) + "-" + self.ui.curve_selection.currentText()
        self.scene.add_object(name)
        self.mode.switch_mode("Add curve points")
        self.internal_counter += 1
        self.model.setCurve(self.scene.current_object)
        self.model.layoutChanged.emit()


if __name__ == "__main__":
    app = CurveEditor(sys.argv)
