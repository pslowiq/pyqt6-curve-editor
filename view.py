from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QGraphicsView


class EditorView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._empty = True
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            factor = 1.25
        else:
            factor = 0.75
        self.scale(factor, factor)
