from PyQt6.QtCore import QObject, pyqtSignal


class EditorMode(QObject):
    mode_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.current_mode = "None"

    def switch_mode(self, new_mode):
        self.current_mode = new_mode
        self.mode_changed.emit(self.current_mode)
