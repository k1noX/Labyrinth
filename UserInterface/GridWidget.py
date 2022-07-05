import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui

from math import floor
from typing import *

from Grid.GridMap import *
from Algorithms.PathFindingAlgorithm import *


class WallGridWidget(QtWidgets.QWidget):


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
        return self.setSquareSize()


    def getCanvasSize(self) -> Tuple[int, int]:
        width = self.squareSize * self.grid.columns
        height = self.squareSize * self.grid.rows

        return (width, height)


    def getCanvasOrigin(self) -> Tuple[int, int]:
        width, height = self.getCanvasSize()

        left = (self.width() - width) / 2
        top = (self.height() - height) / 2

        return (left, top)


    def _drawWalls(self, qpainter: QtGui.QPainter):
        left, top = self.getCanvasOrigin()

        objectRect = QtCore.QRectF(0, 0, self.squareSize, self.squareSize)

        qpainter.setOpacity(1)
        qpainter.setBrush(QtGui.QColor(217, 83, 79))
        for row in range(self.grid.rows):
            for column in range(self.grid.columns):
                if self.grid.getCell((row, column)) == 1:
                    qpainter.drawRect(objectRect.translated(
                        left + column * self.squareSize, top + row * self.squareSize))


    def _drawScene(self, qpainter: QtGui.QPainter):
        width, height = self.getCanvasSize()
        left, top = self.getCanvasOrigin()

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
        width, height = self.getCanvasSize()
        left, top = self.getCanvasOrigin()

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



class SolverGridWidget(WallGridWidget):
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

        self.drawMode = SolverGridWidget.DrawMode.walls
        self.state = SolverGridWidget.State.viewing

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

        self.state = SolverGridWidget.State.solving


    def stopSolving(self):
        self.setAlgorithmSolveQueue()

        self.timer.stop()
        self.timer.deleteLater()

        self.state = SolverGridWidget.State.solved
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
        
        left, top = self.getCanvasOrigin()

        objectRect = QtCore.QRectF(0, 0, self.squareSize, self.squareSize)

        qpainter.setOpacity(1)
        qpainter.setBrush(SolverGridWidget.colors['target'])
        qpainter.drawRect(objectRect.translated(
            left + self.target[1] * self.squareSize, top + self.target[0] * self.squareSize))

        qpainter.setBrush(SolverGridWidget.colors['source'])
        qpainter.drawRect(objectRect.translated(
            left + self.source[1] * self.squareSize, top + self.source[0] * self.squareSize))


    def _drawCurrentSolveStep(self, qpainter: QtGui.QPainter):
        left, top = self.getCanvasOrigin()

        objectRect = QtCore.QRectF(0, 0, self.squareSize, self.squareSize)
        
        qpainter.setOpacity(0.25)
        qpainter.setBrush(SolverGridWidget.colors['used'])

        for x, y in self.used:
            qpainter.drawRect(objectRect.translated(
                left + y * self.squareSize, top + x * self.squareSize))

        qpainter.setOpacity(1)
        qpainter.setBrush(SolverGridWidget.colors['selected'])

        if self.currentPath.empty():
            pass
        elif self.state == SolverGridWidget.State.solved:
            for x, y in self.solve():
                qpainter.drawRect(objectRect.translated(
                    left + y * self.squareSize, top + x * self.squareSize))
        else:
            path, current = self.currentPath.get()

            for x, y in PathFindingAlgorithm._reconstructPath(path, self.source, current):
                qpainter.drawRect(objectRect.translated(
                    left + y * self.squareSize, top + x * self.squareSize))

    
    def _drawResult(self, qpainter: QtGui.QPainter):
        left, top = self.getCanvasOrigin()

        objectRect = QtCore.QRectF(0, 0, self.squareSize, self.squareSize)

        qpainter.setOpacity(1)
        qpainter.setBrush(SolverGridWidget.colors['selected'])

        for x, y in self.solve():
            qpainter.drawRect(objectRect.translated(
                left + y * self.squareSize, top + x * self.squareSize))


    def paintEvent(self, event):
        qpainter = QtGui.QPainter(self)
        qpainter.translate(.5, .5)
        qpainter.setRenderHints(qpainter.Antialiasing)

        self._drawScene(qpainter)
        self._drawWalls(qpainter)

        if self.state == SolverGridWidget.State.solving:
            self._drawCurrentSolveStep(qpainter)
        elif self.state == SolverGridWidget.State.solved:
            self._drawResult(qpainter)

        qpainter.end()


    def mousePressEvent(self, QMouseEvent):
        if self.state == SolverGridWidget.State.viewing:
            left, top = self.getCanvasOrigin()
            width, height = self.getCanvasSize()

            x = QMouseEvent.pos().x()
            y = QMouseEvent.pos().y()

            i = floor((x - left) / self.squareSize)
            j = floor((y - top) / self.squareSize)

            if (x >= left) & (x <= left + width) & (y >= top) & (y <= top + height):
                if self.drawMode == SolverGridWidget.DrawMode.walls:
                    if QMouseEvent.button() == QtCore.Qt.LeftButton and self.source != (j, i) and self.target != (j, i):
                        self.grid.setCell((j, i))

                    if QMouseEvent.button() == QtCore.Qt.RightButton:
                        self.grid.resetCell((j, i))  

                elif self.drawMode == SolverGridWidget.DrawMode.target:
                    if QMouseEvent.button() == QtCore.Qt.LeftButton:
                        if self.grid.getCell((j, i)) == 0:
                            self.target = (j, i)

                elif self.drawMode == SolverGridWidget.DrawMode.source:
                    if QMouseEvent.button() == QtCore.Qt.LeftButton:
                        if self.grid.getCell((j, i)) == 0:
                            self.source = (j, i)
                
                self.update()