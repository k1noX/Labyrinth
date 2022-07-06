from typing import Dict
from Algorithms.PathFindingAlgorithm import *
from UserInterface.GridWidget import SolverGridWidget

from PyQt5.QtCore import (QMetaObject, QRect, Qt)
from PyQt5.QtWidgets import *  



from math import floor


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()  
        self.algorithms: Dict[str, PathFindingAlgorithm] = {"A*": AStarAlgorithm, "BFS": BreadthFirstSearch, "Dijkstra Search": DijkstraSearch}
        self.setupUi(self)


    def disableGridEditing(self):
        self.rowSlider.setEnabled(False)
        self.columnSlider.setEnabled(False)
        self.randomWallsButton.setEnabled(False)
        self.drawModeComboBox.setEnabled(False)
        self.algorithmComboBox.setEnabled(False)


    def enableGridEditing(self):
        self.rowSlider.setEnabled(True)
        self.columnSlider.setEnabled(True)
        self.randomWallsButton.setEnabled(True)
        self.drawModeComboBox.setEnabled(True)
        self.algorithmComboBox.setEnabled(True)


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
        self.gridWidget.state = SolverGridWidget.State.viewing
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
        self.gridWidget.drawMode = SolverGridWidget.DrawMode.walls

    def setTargetDrawMode(self):
        self.gridWidget.drawMode = SolverGridWidget.DrawMode.target

    def setSourceDrawMode(self):
        self.gridWidget.drawMode = SolverGridWidget.DrawMode.source


    def drawModeChangeHandler(self):
        commands = [self.setWallsDrawMode, self.setTargetDrawMode, self.setSourceDrawMode]
        return commands[self.drawModeComboBox.currentIndex()]()


    def algorithmChangeHandler(self):
        self.gridWidget.algorithm = self.algorithms[self.algorithmComboBox.currentText()]


    def setupSettingsGroupBox(self):
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


    def setupPaintGroupBox(self):
        self.paintGroupBox = QGroupBox(self.horizontalLayoutWidget)
        self.paintGroupBox.setObjectName(u"paintGroupBox")
        self.paintGroupBox.setTitle("Рисование")

        self.paintLayoutWidget = QWidget(self.paintGroupBox)
        self.paintLayoutWidget.setObjectName(u"paintLayoutWidget")
        self.paintLayoutWidget.setGeometry(QRect(8, 16, 128, 128))

        self.paintLayout = QVBoxLayout(self.paintLayoutWidget)
        self.paintLayout.setObjectName(u"paintLayout")
        self.paintLayout.setContentsMargins(8, 8, 8, 8)

        self.drawModeComboBox = QComboBox(self.paintLayoutWidget)
        self.drawModeComboBox.addItem("Стены")
        self.drawModeComboBox.addItem("Цель")
        self.drawModeComboBox.addItem("Старт")
        self.drawModeComboBox.setObjectName(u"comboBox")
        self.paintLayout.addWidget(self.drawModeComboBox)
        self.drawModeComboBox.currentIndexChanged.connect(self.drawModeChangeHandler)

        self.verticalLayout.addWidget(self.paintGroupBox)


    def setupAlgorithmGroupBox(self):
        self.algorithmGroupBox = QGroupBox(self.horizontalLayoutWidget)
        self.algorithmGroupBox.setObjectName(u"algorithmGroupBox")
        self.algorithmGroupBox.setTitle("Управление алгоритмом")
        
        self.algorithmLayoutWidget = QWidget(self.algorithmGroupBox)
        self.algorithmLayoutWidget.setObjectName(u"algorithmLayoutWidget")
        self.algorithmLayoutWidget.setGeometry(QRect(8, 16, 128, 256))

        self.algorithmLayout = QVBoxLayout(self.algorithmLayoutWidget)
        self.algorithmLayout.setObjectName(u"algorithmLayout")
        self.algorithmLayout.setContentsMargins(0, 0, 0, 0)

        self.algorithmComboBox = QComboBox(self.algorithmLayoutWidget)

        for e in self.algorithms.keys():
            self.algorithmComboBox.addItem(e)

        self.algorithmComboBox.setObjectName(u"algorithmComboBox")
        self.algorithmComboBox.currentIndexChanged.connect(self.algorithmChangeHandler)
        self.algorithmLayout.addWidget(self.algorithmComboBox)

        self.startButton = QPushButton(self.algorithmLayoutWidget)
        self.startButton.setObjectName(u"Start")
        self.startButton.setText("Запуск")
        self.startButton.clicked.connect(self.startSolving)
        self.algorithmLayout.addWidget(self.startButton)

        self.verticalLayout.addWidget(self.algorithmGroupBox)
        self.horizontalLayout.addLayout(self.verticalLayout)


    def setupUi(self, MainWindow):
        if MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(824, 624)

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        self.horizontalLayoutWidget = QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(8, 8, 816, 616))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(8, 8, 8, 8)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")

        self.setupSettingsGroupBox()
        self.setupPaintGroupBox()
        self.setupAlgorithmGroupBox()

        self.gridWidget = SolverGridWidget(50, 50, self.horizontalLayoutWidget)
        self.gridWidget.setObjectName(u"Grid Solver")

        self.rowLabel.setText("Количество строк: " + str(self.gridWidget.grid.rows))
        self.columnLabel.setText("Количество столбцов: " + str(self.gridWidget.grid.columns))

        self.rowSlider.valueChanged.connect(self.resizeGrid)
        self.columnSlider.valueChanged.connect(self.resizeGrid)

        self.horizontalLayout.addWidget(self.gridWidget)

        QMetaObject.connectSlotsByName(MainWindow)