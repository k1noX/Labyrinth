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

        rectangle = QtCore.QRectF(0, 0, self.squareSize, self.squareSize)

        qpainter.setOpacity(1)
        qpainter.setBrush(QtGui.QColor(32, 32, 32))
        for row in range(self.grid.rows):
            for column in range(self.grid.columns):
                if self.grid.getCell((row, column)):
                    qpainter.drawRect(rectangle.translated(
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



class SolverGridWidget(WallGridWidget):
    colors: Dict[str, QtGui.QColor] = {
        'target': QtGui.QColor(66, 139, 202), 
        'source': QtGui.QColor(91, 192, 222), 
        'selected': QtGui.QColor(192, 255, 201), 
        'used': QtGui.QColor(32, 178, 170)
    }


    class DrawMode(enum.Enum):
        walls = 1
        source = 2
        target = 3


    class State(enum.Enum):
        viewing = 1
        drawing = 2
        erasing = 3
        solving = 4
        solved = 5


    def __init__(self, rows: int, columns: int, *args, **kwargs):
        super().__init__(rows, columns, *args, **kwargs)
        self.target = (0, 0)
        self.source = (rows - 1, columns - 1)
        self.algorithm = AStarAlgorithm()

        self._interval = 100

        self.drawMode = SolverGridWidget.DrawMode.walls
        self.installEventFilter(self)

        self._state = SolverGridWidget.State.viewing
        self._stateChanged = []

        self.timer = QtCore.QTimer(self, timeout = self.__dequeueSolveStep, interval = self._interval)


    def setAlgorithm(self, algorithm: PathFindingAlgorithm) -> None:
        self.algorithm = algorithm


    def setAlgorithmSolveQueue(self) -> None:
        self.solveQueue = self.algorithm.getSolveQueue(self.grid, self.source, self.target)
        self.used = []
        self.currentPath = []


    def resizeGrid(self, rows, columns) -> None:
        self.grid.resize(rows, columns)

        if self.target[0] >= self.grid.rows or self.target[1] >= self.grid.columns:
            self.target = (0, 0)
            self.grid.resetCell(self.target)

        if self.source[0] >= self.grid.rows or self.source[1] >= self.grid.columns:
            self.source = (self.grid.rows - 1, self.grid.columns - 1)
            self.grid.resetCell(self.source)

        self.setSquareSize()
        self.update()


    def solve(self):
        return self.algorithm.solve(self.grid, self.source, self.target)


    def addStateCallback(self, callback):
        if callable(callback):
            self._stateChanged.append(callback)


    @property
    def interval(self):
        return self._interval


    @interval.setter
    def interval(self, newValue):
        if self.state == SolverGridWidget.State.viewing:
            self._interval = newValue
            self.timer.deleteLater()
            self.timer = QtCore.QTimer(self, timeout = self.__dequeueSolveStep, interval = self._interval)


    @property
    def stateChanged(self):
        return self._stateChanged


    @stateChanged.setter
    def stateChanged(self, newStateChanged):
        for i in self.newStateChanged:
            if callable(i):
                self._stateChanged.append(i)


    @property
    def state(self):
        return self._state


    @state.setter
    def state(self, newState):
        if self._state == SolverGridWidget.State.solving:
            if newState == SolverGridWidget.State.solved:
                self.__stopSolving()
            elif newState == SolverGridWidget.State.viewing:
                self.__stopSolving()
                self._state = newState

        elif self._state == SolverGridWidget.State.solved:
            if newState == SolverGridWidget.State.solving:
                self.__startSolving()
            elif newState == SolverGridWidget.State.viewing:
                self._state = newState

        elif self._state == SolverGridWidget.State.viewing:
            if newState == SolverGridWidget.State.solved:
                self.__startSolving()
                self.__stopSolving()
            elif newState == SolverGridWidget.State.solving:
                self.__startSolving()
            else:
                self._state = newState
        
        else:
            if newState == SolverGridWidget.State.solving:
                self._state == newState

        for i in self._stateChanged:
            i()

        self.update()


    def __startSolving(self):
        self.setAlgorithmSolveQueue()

        self.timer.start()
        self._state = SolverGridWidget.State.solving


    def __stopSolving(self) -> None:
        self.timer.stop()
        self._state = SolverGridWidget.State.solved
        self.update()


    def __dequeueSolveStep(self) -> None:
        if self.solveQueue.queue.empty():
            self.state = SolverGridWidget.State.solved
        else:
            used, selected, current = self.solveQueue.dequeue()
            self.used = {*self.used, *used}
            self.currentPath = [selected, current]
            self.update()


    def __drawSourceAndTarget(self, painter: QtGui.QPainter) -> None:
        left, top = self.getCanvasOrigin()
        rectangle = QtCore.QRectF(0, 0, self.squareSize, self.squareSize)

        painter.setOpacity(1)
        painter.setBrush(SolverGridWidget.colors['target'])
        painter.drawRect(rectangle.translated(
            left + self.target[1] * self.squareSize, top + self.target[0] * self.squareSize))

        painter.setBrush(SolverGridWidget.colors['source'])
        painter.drawRect(rectangle.translated(
            left + self.source[1] * self.squareSize, top + self.source[0] * self.squareSize))


    def __drawCurrentSolveStep(self, painter: QtGui.QPainter) -> None:
        left, top = self.getCanvasOrigin()

        rectangle = QtCore.QRectF(0, 0, self.squareSize, self.squareSize)
        
        painter.setOpacity(0.25)
        painter.setBrush(SolverGridWidget.colors['used'])

        for x, y in self.used:
            painter.drawRect(rectangle.translated(
                left + y * self.squareSize, top + x * self.squareSize))

        painter.setOpacity(1)
        painter.setBrush(SolverGridWidget.colors['selected'])

        if len(self.currentPath) == 0:
            pass
        else:
            path, current = self.currentPath
            self.currentPath = []

            for x, y in PathFindingAlgorithm._reconstructPath(path, self.source, current):
                painter.drawRect(rectangle.translated(
                    left + y * self.squareSize, top + x * self.squareSize))

    
    def __drawResult(self, painter: QtGui.QPainter):
        left, top = self.getCanvasOrigin()

        rectangle = QtCore.QRectF(0, 0, self.squareSize, self.squareSize)

        painter.setOpacity(1)
        painter.setBrush(SolverGridWidget.colors['selected'])

        result = self.solve()

        if result is not None:
            for x, y in result:
                painter.drawRect(rectangle.translated(
                    left + y * self.squareSize, top + x * self.squareSize))

        else: # `result` might be None
            self.state = SolverGridWidget.State.viewing

            messageBox = QtWidgets.QMessageBox()
            messageBox.setIcon(QtWidgets.QMessageBox.Warning)
            messageBox.setText("Невозможно выйти из лабиринта!")
            messageBox.setInformativeText(f"Пути из точки {self.source} в {self.target} не существует!")
            messageBox.setWindowTitle("Ошибка!")
            messageBox.exec()


    def paintEvent(self, event: QtCore.QEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.translate(.5, .5)
        painter.setRenderHints(painter.Antialiasing)

        self._drawScene(painter)
        self._drawWalls(painter)
        self.__drawSourceAndTarget(painter)

        if self.state == SolverGridWidget.State.solving:
            self.__drawCurrentSolveStep(painter)
        elif self.state == SolverGridWidget.State.solved:
            self.__drawResult(painter)
        
        painter.end()   


    def eventFilter(self, source: QtWidgets.QWidget, event: QtCore.QEvent) -> bool:
        if self.state == SolverGridWidget.State.viewing:
            if event.type() == QtCore.QEvent.MouseButtonPress:
                if event.button() == QtCore.Qt.LeftButton:
                    self._state = SolverGridWidget.State.drawing

                elif event.button() == QtCore.Qt.RightButton:
                    self._state = SolverGridWidget.State.erasing

        elif self.state == SolverGridWidget.State.drawing or self.state == SolverGridWidget.State.erasing:
            if event.type() == QtCore.QEvent.MouseButtonRelease:
                self._state = SolverGridWidget.State.viewing

        return super().eventFilter(source, event)


    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        left, top = self.getCanvasOrigin()
        width, height = self.getCanvasSize()

        x = event.pos().x()
        y = event.pos().y()

        i = floor((x - left) / self.squareSize)
        j = floor((y - top) / self.squareSize)

        if (x >= left) & (x <= left + width) & (y >= top) & (y <= top + height):
            if self.drawMode == SolverGridWidget.DrawMode.walls:
                if self.state == SolverGridWidget.State.drawing:
                    self.grid.setCell((j, i))
                elif self.state == SolverGridWidget.State.erasing:
                    self.grid.resetCell((j, i))  

            elif self.drawMode == SolverGridWidget.DrawMode.target:
                if self.state == SolverGridWidget.State.drawing:
                    if not self.grid.getCell((j, i)):
                        self.target = (j, i)

            elif self.drawMode == SolverGridWidget.DrawMode.source:
                if self.state == SolverGridWidget.State.drawing:
                    if not self.grid.getCell((j, i)):
                        self.source = (j, i)
                
            self.update()
        
        return super().mouseMoveEvent(event)

