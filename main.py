from ast import AST
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.Qt as Qt

from math import floor
import sys
from typing import *
from queue import PriorityQueue

from Grid.GridMap import *
from Algorithms.PathFindingAlgorithm import *

SIZE = 50

from PyQt5.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from PyQt5.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient)
from PyQt5.QtWidgets import *


class WallGrid(QtWidgets.QWidget):


    def __init__(self, rows, columns, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(600, 600)
        self.grid = GridMatrix(rows, columns)


    def setSquareSize(self):
        reference = self.width() * self.grid.rows / self.grid.columns
        if reference > self.height():
            self.squareSize = (self.height() - 1) / self.grid.rows
        else:
            self.squareSize = (self.width() - 1) / self.grid.columns


    def resizeEvent(self, event):
        self.setSquareSize()


    def _drawWalls(self, qpainter: QtGui.QPainter):
        width = self.squareSize * self.grid.columns
        height = self.squareSize * self.grid.rows

        left = (self.width() - width) / 2
        top = (self.height() - height) / 2

        objectRect = QtCore.QRectF(0, 0, self.squareSize, self.squareSize)

        qpainter.setOpacity(1)
        qpainter.setBrush(QtGui.QColor(217, 83, 79))
        for row in range(self.grid.rows):
            for column in range(self.grid.columns):
                if self.grid.getCell((row, column)) == 1:
                    qpainter.drawRect(objectRect.translated(
                        left + column * self.squareSize, top + row * self.squareSize))


    def _drawScene(self, qpainter: QtGui.QPainter):
        width = self.squareSize * self.grid.columns
        height = self.squareSize * self.grid.rows

        left = (self.width() - width) / 2
        top = (self.height() - height) / 2

        qpainter.setOpacity(0.1)
        y = top
        for row in range(self.grid.rows + 1):
            qpainter.drawLine(left, y, left + width, y)
            y += self.squareSize

        x = left
        for column in range(self.grid.columns + 1):
            qpainter.drawLine(x, top, x, top + height)
            x += self.squareSize


    def paintEvent(self, event):
        qpainter = QtGui.QPainter(self)
        qpainter.translate(.5, .5)
        qpainter.setRenderHints(qpainter.Antialiasing)

        self._drawScene(qpainter)
        self._drawWalls(qpainter)
    

    def mousePressEvent(self, QMouseEvent):
        width = self.squareSize * self.grid.columns
        height = self.squareSize * self.grid.rows

        left = (self.width() - width) / 2
        top = (self.height() - height) / 2

        x = QMouseEvent.pos().x()
        y = QMouseEvent.pos().y()

        i = floor((x - left) / self.squareSize)
        j = floor((y - top) / self.squareSize)

        if (x >= left) & (x <= left + width) & (y >= top) & (y <= top + height):
            if QMouseEvent.button() == QtCore.Qt.LeftButton:
                self.grid.setCell((j, i))

            if QMouseEvent.button() == QtCore.Qt.RightButton:
                self.grid.resetCell((j, i))    
            
            self.update()


class SolverGrid(WallGrid):
    colors: Dict[str, QtGui.QColor] = {
        'target': QtGui.QColor(66,139,202), 
        'source': QtGui.QColor(91,192,222), 
        'selected': QtGui.QColor(192,255,201), 
        'used': QtGui.QColor(32,178,170)
    }


    class DrawMode(enum.Enum):
        walls = 1
        source = 2
        target = 3


    class State(enum.Enum):
        viewing = 1
        solving = 2
        solved = 3



    def __init__(self, rows: int, columns: int, *args, **kwargs):
        super().__init__(rows, columns, *args, **kwargs)
        self.target = (0, 0)
        self.source = (42, 34)
        self.algorithm = AStarAlgorithm()
        self.interval = 100

        self.drawMode = SolverGrid.DrawMode.walls
        self.state = SolverGrid.State.viewing

        self.timer = QtCore.QTimer(self, timeout = self._dequeueSolveStep, interval = self.interval)


    def setAlgorithm(self, algorithm: PathFindingAlgorithm):
        self.algorithm = algorithm
        self.setAlgorithmSolveQueue()


    def setAlgorithmSolveQueue(self):
        self.solveQueue = self.algorithm.getSolveQueue(self.grid, self.source, self.target)
        self.used = []
        self.currentPath = Queue()


    def resizeGrid(self, rows, columns):
        self.grid._cells = [[self.grid._cells[j][i] if (j < self.grid.rows and i < self.grid.columns) else 0 for i in range(columns)] for j in range(rows)]
        self.grid.rows = rows
        self.grid.columns = columns

        if self.target[0] >= self.grid.rows or self.target[1] >= self.grid.columns:
            self.target = (self.grid.rows - 1, self.grid.columns - 1)


        if self.source[0] >= self.grid.rows or self.source[1] >= self.grid.columns:
            self.source = (self.grid.rows - 1, self.grid.columns - 1)

        self.setSquareSize()
        self.update()


    def solve(self):
        return self.algorithm.solve(self.grid, self.source, self.target)


    def startSolving(self):
        self.setAlgorithmSolveQueue()

        self.timer.start()

        self.state = SolverGrid.State.solving


    def stopSolving(self):
        self.setAlgorithmSolveQueue()

        self.timer.stop()
        self.timer.deleteLater()

        self.state = SolverGrid.State.solved
        self.timer = QtCore.QTimer(self, timeout = self._dequeueSolveStep, interval = self.interval)
        self.update()


    def _dequeueSolveStep(self):
        if self.solveQueue.queue.empty():
            self.stopSolving()
        else:
            used, selected, current = self.solveQueue.dequeue()
            self.used = {*self.used, *used}
            self.currentPath.put((selected, current))
            self.update()


    def _drawScene(self, qpainter: QtGui.QPainter):
        super()._drawScene(qpainter)
        
        width = self.squareSize * self.grid.columns
        height = self.squareSize * self.grid.rows

        left = (self.width() - width) / 2
        top = (self.height() - height) / 2

        objectRect = QtCore.QRectF(0, 0, self.squareSize, self.squareSize)

        qpainter.setOpacity(1)
        qpainter.setBrush(SolverGrid.colors['target'])
        qpainter.drawRect(objectRect.translated(
            left + self.target[1] * self.squareSize, top + self.target[0] * self.squareSize))

        qpainter.setBrush(SolverGrid.colors['source'])
        qpainter.drawRect(objectRect.translated(
            left + self.source[1] * self.squareSize, top + self.source[0] * self.squareSize))


    def _drawSolveQueue(self, qpainter: QtGui.QPainter):
        width = self.squareSize * self.grid.columns
        height = self.squareSize * self.grid.rows

        left = (self.width() - width) / 2
        top = (self.height() - height) / 2

        objectRect = QtCore.QRectF(0, 0, self.squareSize, self.squareSize)
        
        qpainter.setOpacity(0.25)
        qpainter.setBrush(SolverGrid.colors['used'])

        for x, y in self.used:
            qpainter.drawRect(objectRect.translated(
                left + y * self.squareSize, top + x * self.squareSize))

        qpainter.setOpacity(1)
        qpainter.setBrush(SolverGrid.colors['selected'])

        if self.currentPath.empty():
            pass
        elif self.state == SolverGrid.State.solved:
            for x, y in self.solve():
                qpainter.drawRect(objectRect.translated(
                    left + y * self.squareSize, top + x * self.squareSize))
        else:
            path, current = self.currentPath.get()

            for x, y in PathFindingAlgorithm._reconstructPath(path, self.source, current):
                qpainter.drawRect(objectRect.translated(
                    left + y * self.squareSize, top + x * self.squareSize))

    
    def _drawResult(self, qpainter: QtGui.QPainter):
        width = self.squareSize * self.grid.columns
        height = self.squareSize * self.grid.rows

        left = (self.width() - width) / 2
        top = (self.height() - height) / 2

        objectRect = QtCore.QRectF(0, 0, self.squareSize, self.squareSize)

        qpainter.setOpacity(1)
        qpainter.setBrush(SolverGrid.colors['selected'])

        for x, y in self.solve():
            qpainter.drawRect(objectRect.translated(
                left + y * self.squareSize, top + x * self.squareSize))


    def paintEvent(self, event):
        qpainter = QtGui.QPainter(self)
        qpainter.translate(.5, .5)
        qpainter.setRenderHints(qpainter.Antialiasing)

        self._drawScene(qpainter)
        self._drawWalls(qpainter)

        if self.state == SolverGrid.State.solving:
            self._drawSolveQueue(qpainter)
        elif self.state == SolverGrid.State.solved:
            self._drawResult(qpainter)

        qpainter.end()

    def mousePressEvent(self, QMouseEvent):
        width = self.squareSize * self.grid.columns
        height = self.squareSize * self.grid.rows

        left = (self.width() - width) / 2
        top = (self.height() - height) / 2

        x = QMouseEvent.pos().x()
        y = QMouseEvent.pos().y()

        i = floor((x - left) / self.squareSize)
        j = floor((y - top) / self.squareSize)

        if (x >= left) & (x <= left + width) & (y >= top) & (y <= top + height):
            if self.drawMode == SolverGrid.DrawMode.walls:
                if QMouseEvent.button() == QtCore.Qt.LeftButton and self.source != (j, i) and self.target != (j, i):
                    self.grid.setCell((j, i))

                if QMouseEvent.button() == QtCore.Qt.RightButton:
                    self.grid.resetCell((j, i))  

            elif self.drawMode == SolverGrid.DrawMode.target:
                if QMouseEvent.button() == QtCore.Qt.LeftButton:
                    if self.grid.getCell((j, i)) == 0:
                        self.target = (j, i)

            elif self.drawMode == SolverGrid.DrawMode.source:
                if QMouseEvent.button() == QtCore.Qt.LeftButton:
                    if self.grid.getCell((j, i)) == 0:
                        self.source = (j, i)
            
            self.update()


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()  
        self.setupUi(self)


    def disableGridEditing(self):
        self.rowSlider.setEnabled(False)
        self.columnSlider.setEnabled(False)
        self.wallsRadioButton.setEnabled(False)
        self.sourceRadioButton.setEnabled(False)
        self.targetRadioButton.setEnabled(False)
        self.randomWallsButton.setEnabled(False)


    def enableGridEditing(self):
        self.rowSlider.setEnabled(True)
        self.columnSlider.setEnabled(True)
        self.wallsRadioButton.setEnabled(True)
        self.sourceRadioButton.setEnabled(True)
        self.targetRadioButton.setEnabled(True)
        self.randomWallsButton.setEnabled(True)


    def startSolving(self):
        self.startButton.setText("Завершить")
        self.gridWidget.startSolving()
        self.startButton.clicked.connect(self.stopSolving)

        self.disableGridEditing()


    def stopSolving(self):
        self.startButton.setText("Вернуться")
        self.gridWidget.stopSolving()
        self.startButton.clicked.connect(self.continueSolving)


    def continueSolving(self):
        self.startButton.setText("Запуск")
        self.gridWidget.state = SolverGrid.State.viewing
        self.startButton.clicked.connect(self.startSolving)

        self.enableGridEditing()


    def resizeGrid(self):
        self.gridWidget.resizeGrid(floor(self.rowSlider.value() / 100 * 90) + 10, 
            floor(self.columnSlider.value() / 100 * 90) + 10)
        
        self.rowLabel.setText("Количество столбцов: " + str(self.gridWidget.grid.rows))
        self.columnLabel.setText("Количество столбцов: " + str(self.gridWidget.grid.columns))


    def generateRandomGrid(self):
        self.gridWidget.grid.setRandom(k=0.25)

        if self.gridWidget.grid.getCell(self.gridWidget.target) == 1:
            self.gridWidget.grid.resetCell(self.gridWidget.target)

        if self.gridWidget.grid.getCell(self.gridWidget.source) == 1:
            self.gridWidget.grid.resetCell(self.gridWidget.source)

        self.update()


    def setWallsDrawMode(self):
        self.gridWidget.drawMode = SolverGrid.DrawMode.walls

    def setTargetDrawMode(self):
        self.gridWidget.drawMode = SolverGrid.DrawMode.target

    def setSourceDrawMode(self):
        self.gridWidget.drawMode = SolverGrid.DrawMode.source


    def setupUi(self, MainWindow):
        if MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(816, 616)

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        self.horizontalLayoutWidget = QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(8, 8, 800, 600))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(8, 8, 8, 8)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")

        self.settingsGroupBox = QGroupBox(self.horizontalLayoutWidget)
        self.settingsGroupBox.setObjectName(u"groupBox")
        self.settingsGroupBox.setTitle("Параметры сетки лабиринта")

        self.settingsLayoutWidget = QWidget(self.settingsGroupBox)
        self.settingsLayoutWidget.setObjectName(u"settingsLayoutWidget")
        self.settingsLayoutWidget.setGeometry(QRect(8, 16, 160, 128))

        self.settingsLayout = QVBoxLayout(self.settingsLayoutWidget)
        self.settingsLayout.setObjectName(u"settingsLayout")
        self.settingsLayout.setContentsMargins(8, 8, 8, 8)
        self.verticalLayout.addWidget(self.settingsGroupBox)

        self.rowLabel = QLabel(self.settingsLayoutWidget)
        self.rowLabel.setObjectName(u"rowLabel")
        self.settingsLayout.addWidget(self.rowLabel)

        self.rowSlider = QSlider(self.settingsLayoutWidget)
        self.rowSlider.setObjectName(u"rowSlider")
        self.rowSlider.setOrientation(Qt.Horizontal)
        self.rowSlider.setValue(45)
        self.settingsLayout.addWidget(self.rowSlider)

        self.columnLabel = QLabel(self.settingsLayoutWidget)
        self.columnLabel.setObjectName(u"columnLabel")
        self.settingsLayout.addWidget(self.columnLabel)

        self.columnSlider = QSlider(self.settingsLayoutWidget)
        self.columnSlider.setObjectName(u"columnSlider")
        self.columnSlider.setOrientation(Qt.Horizontal)
        self.columnSlider.setValue(45)
        self.settingsLayout.addWidget(self.columnSlider)

        self.randomWallsButton = QPushButton(self.settingsLayoutWidget)
        self.randomWallsButton.setObjectName(u"randomWallsButton")
        self.randomWallsButton.setText("Сгенерировать стены")
        self.randomWallsButton.clicked.connect(self.generateRandomGrid)
        self.settingsLayout.addWidget(self.randomWallsButton)

        self.paintGroupBox = QGroupBox(self.horizontalLayoutWidget)
        self.paintGroupBox.setObjectName(u"paintGroupBox")
        self.paintGroupBox.setTitle("Рисование")

        self.paintLayoutWidget = QWidget(self.paintGroupBox)
        self.paintLayoutWidget.setObjectName(u"paintLayoutWidget")
        self.paintLayoutWidget.setGeometry(QRect(8, 16, 128, 128))

        self.paintLayout = QVBoxLayout(self.paintLayoutWidget)
        self.paintLayout.setObjectName(u"paintLayout")
        self.paintLayout.setContentsMargins(8, 8, 8, 8)

        self.wallsRadioButton = QRadioButton(self.paintLayoutWidget)
        self.wallsRadioButton.setObjectName(u"wallsRadioButton")
        self.wallsRadioButton.setText("Стены")
        self.wallsRadioButton.setChecked(True)
        self.wallsRadioButton.clicked.connect(self.setWallsDrawMode)
        self.paintLayout.addWidget(self.wallsRadioButton)
        
        self.targetRadioButton = QRadioButton(self.paintLayoutWidget)
        self.targetRadioButton.setObjectName(u"targetRadioButton")
        self.targetRadioButton.setText("Цель")
        self.targetRadioButton.clicked.connect(self.setTargetDrawMode)
        self.paintLayout.addWidget(self.targetRadioButton)
        
        self.sourceRadioButton = QRadioButton(self.paintLayoutWidget)
        self.sourceRadioButton.setObjectName(u"sourceRadioButton")
        self.sourceRadioButton.setText("Старт")
        self.sourceRadioButton.clicked.connect(self.setSourceDrawMode)
        self.paintLayout.addWidget(self.sourceRadioButton)

        self.verticalLayout.addWidget(self.paintGroupBox)

        self.algorithmGroupBox = QGroupBox(self.horizontalLayoutWidget)
        self.algorithmGroupBox.setObjectName(u"algorithmGroupBox")
        self.algorithmGroupBox.setTitle("Управление алгоритмом")
        
        self.algorithmButtonsVLW = QWidget(self.algorithmGroupBox)
        self.algorithmButtonsVLW.setObjectName(u"algorithmButtonsVLW")
        self.algorithmButtonsVLW.setGeometry(QRect(8, 16, 128, 256))

        self.algorithmButtonsLayout = QVBoxLayout(self.algorithmButtonsVLW)
        self.algorithmButtonsLayout.setObjectName(u"algorithmButtonsVL")
        self.algorithmButtonsLayout.setContentsMargins(0, 0, 0, 0)

        self.startButton = QPushButton(self.algorithmButtonsVLW)
        self.startButton.setObjectName(u"Start")
        self.startButton.setText("Запуск")
        self.startButton.clicked.connect(self.startSolving)
        self.algorithmButtonsLayout.addWidget(self.startButton)

        self.verticalLayout.addWidget(self.algorithmGroupBox)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.gridWidget = SolverGrid(50, 50, self.horizontalLayoutWidget)
        self.gridWidget.setObjectName(u"Grid Solver")

        self.rowLabel.setText("Количество строк: " + str(self.gridWidget.grid.rows))
        self.columnLabel.setText("Количество столбцов: " + str(self.gridWidget.grid.columns))

        self.rowSlider.valueChanged.connect(self.resizeGrid)
        self.columnSlider.valueChanged.connect(self.resizeGrid)

        self.horizontalLayout.addWidget(self.gridWidget)

        QMetaObject.connectSlotsByName(MainWindow)

    
    

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    w = MainWindow()
    w.show()

    sys.exit(app.exec_())