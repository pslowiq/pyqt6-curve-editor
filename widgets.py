from PyQt6.QtWidgets import QPushButton


def QConnectedButton(title, function):
    btn = QPushButton(title)
    btn.clicked.connect(function)
    return btn
