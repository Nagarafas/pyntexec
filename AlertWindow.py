from platform import system
from os import path

from PyQt6 import QtWidgets, uic
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt

OPERATING_SYSTEM = system()

class AlertWindow(QtWidgets.QDialog):
    def __init__(self, msg: str = "", titleText: str = "Alert", version = "1.0.0", overide_wraplength = 200, parent=None):
        super().__init__(parent)
        uic.loadUi(path.join(path.dirname(__file__),"AlertWindow.ui"), self)
        
        self.image_label.setVisible(False)
        
        self.setWindowTitle(titleText)
        self.message = msg
        
        if OPERATING_SYSTEM == "Windows":
            self.window_icon = QIcon(path.join(path.dirname(__file__),"assets","pyntexec.ico"))
        else:
            self.window_icon = QIcon(path.join(path.dirname(__file__),"assets","pyntexec.png"))
        
        self.setWindowIcon(self.window_icon)
        
        self.message_label.setText(self.message)
        self.message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.message_label.setCursor(Qt.CursorShape.IBeamCursor)
        
        if titleText == "About":
            self.message = f"Version: {version}\n\nPyntexec is a simple GUI for PyInstaller & Nuitka to build Python scripts into executables.\n\nCreated by Nagarafas_MC"
            self.message_label.setText(self.message)
            my_image = QPixmap(path.join(path.dirname(__file__),"assets","pyntexec.png"))
            my_image = my_image.scaled(110, 110)

            self.image_label.setVisible(True)
            self.image_label.setPixmap(my_image)
    