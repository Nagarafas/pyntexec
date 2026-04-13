from platform import system
from os import path

from PyQt6 import QtWidgets, uic
from PyQt6.QtGui import QIcon

OPERATING_SYSTEM = system()

class ConfirmationDialog(QtWidgets.QDialog):
    def __init__(self, msg: str, parent=None):
        super().__init__(parent)
        uic.loadUi(path.join(path.dirname(__file__),"confirmationWindow.ui"), self)
        
        self.setWindowTitle("Confirmation")
        
        self.message_label.setText(msg)
        
        if OPERATING_SYSTEM == "Windows":
            self.window_icon = QIcon(path.join(path.dirname(__file__),"assets","pyntexec.ico"))
        else:
            self.window_icon = QIcon(path.join(path.dirname(__file__),"assets","pyntexec.png"))