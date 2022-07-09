import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import sys

from UserInterface.MainWindow import MainWindow

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv) 

    w = MainWindow()
    w.show()

    sys.exit(app.exec_())