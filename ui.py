from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTreeView,
    QComboBox,
    QListWidget,
    QAbstractItemView,
    QMenuBar,
    QFileDialog,
    QMessageBox,
    QInputDialog,
    QSplitter,
    QGraphicsPixmapItem,
)
import pickle
from PyQt6.QtGui import QColor, QAction, QPixmap
from PyQt6.QtCore import pyqtSignal, Qt
from widgets import QConnectedButton
from config import NAME_TO_CURVE_CLASS


class EditorUI(QWidget):
    add_curve_signal = pyqtSignal()
    move_signal = pyqtSignal()
    add_points_signal = pyqtSignal()
    edit_points_signal = pyqtSignal()
    elevate_degree_signal = pyqtSignal()
    reduce_degree_signal = pyqtSignal()
    remove_object_signal = pyqtSignal()
    split_signal = pyqtSignal()
    merge_signal = pyqtSignal()
    join_signal = pyqtSignal()
    remove_points_signal = pyqtSignal()

    def __init__(self, view, scene):
        super().__init__()
        self.view = view
        self.scene = scene

        self.mode_label = QLabel("MODE:")
        self.add_curve_btn = QConnectedButton("Add curve", self.add_curve_signal.emit)
        self.curve_selection = QComboBox()
        self.curve_selection.addItems(NAME_TO_CURVE_CLASS.keys())
        self.menu_bar = EditorMenuBar(self)

        self.init_ui()

    def make_top_layout(self):
        self.top_layout = QVBoxLayout()
        self.top_line_1 = QHBoxLayout()
        self.top_line_1.addWidget(self.add_curve_btn)
        self.top_line_1.addWidget(self.curve_selection)
        self.top_line_1.addStretch(9)
        self.top_line_1.addWidget(self.mode_label)

        self.top_layout.addWidget(self.menu_bar)
        self.top_layout.addLayout(self.top_line_1)
        self.top_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.top_layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)

    def make_left_layout(self):
        self.left_splitter = QSplitter(Qt.Orientation.Vertical)

        self.objects_widget = QListWidget()
        self.left_splitter.addWidget(self.objects_widget)
        self.properties_widget = QTreeView()
        self.properties_widget.setHeaderHidden(True)
        self.properties_widget.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.SelectedClicked
        )
        self.left_splitter.addWidget(self.properties_widget)
        self.left_splitter.setStretchFactor(1, 5)

    def make_editor_layout(self):

        self.editor_layout = QHBoxLayout()
        self.splitter = QSplitter()
        self.splitter.addWidget(self.left_splitter)
        self.splitter.addWidget(self.view)

    def make_main_layout(self):

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.addLayout(self.top_layout)
        self.main_layout.addWidget(self.splitter)

    def init_ui(self):
        self.make_top_layout()
        self.make_left_layout()
        self.make_editor_layout()
        self.make_main_layout()

    def update_tree_view(self, curve):
        pass


class EditorAction(QAction):
    def __init__(self, name, parent, shortcut, trigger_fun):
        super().__init__(name, parent)
        self.setShortcut(shortcut)
        self.triggered.connect(trigger_fun)


class EditorMenuBar(QMenuBar):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.make_file_menu()
        self.make_edit_menu()

    def make_edit_menu(self):
        self.edit_menu = self.addMenu("Edit")

        self.edit_add_points = self.edit_menu.addAction(
            EditorAction(
                "Add points",
                self.edit_menu,
                "Ctrl+A",
                self.parent().add_points_signal.emit,
            )
        )

        self.edit_edit_points = self.edit_menu.addAction(
            EditorAction(
                "Edit points",
                self.edit_menu,
                "Alt+E",
                self.parent().edit_points_signal.emit,
            )
        )
        self.edit_remove_points = self.edit_menu.addAction(
            EditorAction(
                "Remove points",
                self.edit_menu,
                "Alt+R",
                self.parent().remove_points_signal.emit,
            )
        )
        self.edit_move = self.edit_menu.addAction(
            EditorAction(
                "Move/Rotate", self.edit_menu, "Q", self.parent().move_signal.emit
            )
        )
        self.edit_remove_current = self.edit_menu.addAction(
            EditorAction(
                "Remove Current",
                self.edit_menu,
                "Del",
                self.parent().remove_object_signal.emit,
            )
        )
        self.edit_elevate_degree = self.edit_menu.addAction(
            EditorAction(
                "Elevate degree",
                self.edit_menu,
                "Ctrl+E",
                self.parent().elevate_degree_signal.emit,
            )
        )
        self.edit_reduce_degree = self.edit_menu.addAction(
            EditorAction(
                "Reduce degree",
                self.edit_menu,
                "Ctrl+R",
                self.parent().reduce_degree_signal.emit,
            )
        )
        self.edit_split = self.edit_menu.addAction(
            EditorAction("Split", self.edit_menu, "", self.parent().split_signal.emit)
        )
        self.edit_merge = self.edit_menu.addAction(
            EditorAction("Merge", self.edit_menu, "", self.parent().merge_signal.emit)
        )
        self.edit_merge = self.edit_menu.addAction(
            EditorAction("Join", self.edit_menu, "", self.parent().join_signal.emit)
        )
        self.hide_points = self.edit_menu.addAction(
            EditorAction("Hide all points", self.edit_menu, "", self.hide_all_points)
        )

    def make_file_menu(self):
        self.file_menu = self.addMenu("File")

        self.file_new = self.file_menu.addAction(
            EditorAction("New", self.file_menu, "Ctrl+N", self.new_project)
        )

        self.file_save = self.file_menu.addAction(
            EditorAction("Save", self.file_menu, "Ctrl+S", self.save_project)
        )
        self.file_load = self.file_menu.addAction(
            EditorAction("Load", self.file_menu, "", self.load_project)
        )
        self.image_load = self.file_menu.addAction(
            EditorAction("Load image", self.file_menu, "", self.load_image)
        )
        self.image_remove = self.file_menu.addAction(
            EditorAction("Remove image", self.file_menu, "", self.remove_image)
        )

        self.file_quit = self.file_menu.addAction("Quit")
        self.file_quit.setShortcut("Alt+F4")

    def load_project(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self.parent().view, "Open File", "", "Pickle Files (*.pkl)"
        )
        if file_name:
            with open(file_name, "rb") as f:
                dd = pickle.load(f)
                self.parent().scene.remove_all_objects()
                for name, data in dd.items():
                    control_points, props = data
                    self.parent().scene.add_object(name, control_points, props=props)
                self.parent().internal_counter = 1 + max(
                    [int(k.split("-")[0]) for k in dd.keys()]
                )

    def new_project(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Alert")
        dlg.setText("This will erase your current project.\nAre you sure?")
        dlg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        dlg.setIcon(QMessageBox.Icon.Question)
        button = dlg.exec()

        if button == QMessageBox.StandardButton.Yes:
            self.parent().scene.remove_all_objects()
            self.parent().internal_counter = 0
        else:
            pass

    def save_project(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self.parent().view, "Save File", "", "Pickle Files (*.pkl)"
        )

        dd = {
            k: (
                v.control_points,
                {
                    "point_color": v.point_pen.color().getRgb(),
                    "point_size": v.point_pen.width(),
                    "line_color": v.line_pen.color().getRgb(),
                    "line_size": v.line_pen.width(),
                },
            )
            for k, v in self.parent().scene.object_mapping.items()
        }

        if file_name:
            with open(file_name, "wb") as f:
                pickle.dump(dd, f)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self.parent().view, "Open File", "", "Image Files (*.bmp *.jpg *.png)"
        )

        pixmap = QPixmap(file_name)
        if not pixmap.isNull():
            item = QGraphicsPixmapItem(pixmap)
            item.setZValue(-1.0)
            self.parent().scene.addItem(item)

            self.parent().scene.image = item
            item.setPos(-pixmap.width() / 2, -pixmap.height() / 2)

    def remove_image(self):
        self.parent().scene.remove_image()

    def hide_all_points(self):
        for item in self.parent().scene.object_mapping.values():
            item.show_points = False
        self.parent().scene.update()
