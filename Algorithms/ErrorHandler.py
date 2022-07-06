from PyQt5.QtWidgets import *  
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtWidgets import QMessageBox

class ErrorHandler(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

    def NoPathFoundError(self):
        error_dialog = QtWidgets.QErrorMessage()
        error_dialog.showMessage('Путь не был найден! Уберите стены или поставьте цель в другое место!')
        error_dialog.exec_()