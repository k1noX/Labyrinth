from tkinter import filedialog
from typing import Dict
from Algorithms.PathFindingAlgorithm import AStarAlgorithm, BreadthFirstSearchAlgorithm, DijkstraSearchAlgorithm, PathFindingAlgorithm
from UserInterface.GridWidget import SolverGridWidget
from Grid.GridMap import *
from Grid.MazeGeneratingAlgorithm import *
from FileSystem.GridFileException import *
from FileSystem.GridFileLoader import *
from FileSystem.GridFileSaver import *

from PyQt5.QtCore import (QMetaObject, QRect, Qt)
from PyQt5.QtWidgets import *  
import PyQt5.QtWidgets as QtWidgets

from math import floor
from typing import Dict


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()  
        self.algorithms: Dict[str, PathFindingAlgorithm] = {"A*": AStarAlgorithm, "Dijkstra Search": DijkstraSearchAlgorithm, "Breadth-first Search": BreadthFirstSearchAlgorithm}
        self.setupUi(self)

        self.gridWidget.addStateCallback(self.onStateChanged)


    def disableGridEditing(self):
        self.rowSlider.setEnabled(False)
        self.columnSlider.setEnabled(False)
        self.randomWallsButton.setEnabled(False)
        self.drawModeComboBox.setEnabled(False)
        self.algorithmComboBox.setEnabled(False)
        self.intervalSlider.setEnabled(False)
        self.filepickerLoadButton.setEnabled(False)
        self.filepickerSaveButton.setEnabled(False)


    def enableGridEditing(self):
        self.rowSlider.setEnabled(True)
        self.columnSlider.setEnabled(True)
        self.randomWallsButton.setEnabled(True)
        self.drawModeComboBox.setEnabled(True)
        self.algorithmComboBox.setEnabled(True)
        self.intervalSlider.setEnabled(True)
        self.filepickerLoadButton.setEnabled(True)
        self.filepickerSaveButton.setEnabled(True)


    def onStateChanged(self) -> None:
        if self.gridWidget.state == SolverGridWidget.State.solving:
            self.startButton.setText("Пропустить")
            self.disableGridEditing()
        elif self.gridWidget.state == SolverGridWidget.State.solved:
            self.startButton.setText("Завершить")
        elif self.gridWidget.state == SolverGridWidget.State.viewing:
            self.startButton.setText("Запуск")
            self.enableGridEditing()


    def processStartButton(self) -> None:
        if self.gridWidget.state == SolverGridWidget.State.solving:
            self.gridWidget.state = SolverGridWidget.State.solved
        elif self.gridWidget.state == SolverGridWidget.State.solved:
            self.gridWidget.state = SolverGridWidget.State.viewing
        elif self.gridWidget.state == SolverGridWidget.State.viewing:
            self.gridWidget.state = SolverGridWidget.State.solving


    def resizeGrid(self):
        self.gridWidget.resizeGrid(floor(self.rowSlider.value() / 100 * 90) + 10, 
            floor(self.columnSlider.value() / 100 * 90) + 10)
        
        self.rowLabel.setText("Количество строк: " + str(self.gridWidget.grid.rows))
        self.columnLabel.setText("Количество столбцов: " + str(self.gridWidget.grid.columns))


    def generateRandomGrid(self):
        self.gridWidget.grid = DfsMazeGenerator.generate(self.gridWidget.grid.rows, self.gridWidget.grid.columns)

        if self.gridWidget.grid.getCell(self.gridWidget.target):
            self.gridWidget.grid.tryResetCell(self.gridWidget.target)

        if self.gridWidget.grid.getCell(self.gridWidget.source):
            self.gridWidget.grid.tryResetCell(self.gridWidget.source)

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


    def changeInterval(self):
        self.gridWidget.interval = floor(self.intervalSlider.value() / 100 * 990) + 10

    
    def saveFile(self):
        fileDialog = QFileDialog(self)
        fileDialog.setFileMode(QFileDialog.FileMode.AnyFile)
        fileDialog.setNameFilter("Текстовые файлы (*.txt)")

        if fileDialog.exec():
            filename = fileDialog.selectedFiles()[0]
            saver = GridFileSaver(self.gridWidget.grid, filename)
            
            try:
                saver.save()
            except GridFileException as e:
                messageBox = QtWidgets.QMessageBox()
                messageBox.setIcon(QtWidgets.QMessageBox.Warning)
                messageBox.setText("Ошибка сохранения файла!")
                messageBox.setInformativeText(str(e))
                messageBox.setWindowTitle("Ошибка!")
                messageBox.exec()


    def loadFile(self):
        fileDialog = QFileDialog(self)
        fileDialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        fileDialog.setNameFilter("Текстовые файлы (*.txt)")

        if fileDialog.exec():
            filename = fileDialog.selectedFiles()[0]
        
            loader = GridFileLoader(filename)
                
            try:
                self.gridWidget.grid = loader.load()
                self.gridWidget.resizeGrid(self.gridWidget.grid.rows, self.gridWidget.grid.columns)
                self.update()
                
                self.rowSlider.setValue(floor(10 * self.gridWidget.grid.rows - 100) / 9)
                self.columnSlider.setValue(floor(10 * self.gridWidget.grid.columns - 100) / 9)

            except GridFileException as e:
                messageBox = QtWidgets.QMessageBox(fileDialog)
                messageBox.setIcon(QtWidgets.QMessageBox.Warning)
                messageBox.setText("Ошибка загрузки файла!")
                messageBox.setInformativeText(str(e))
                messageBox.setWindowTitle("Ошибка!")
                messageBox.exec_()



    def setupFileGroupBox(self):
        self.filepickerGroupBox = QGroupBox(self.settingsGroupBox)
        self.filepickerGroupBox.setTitle("Файловая система")
        
        self.filepickerLayoutWidget = QWidget(self.filepickerGroupBox)
        self.filepickerLayoutWidget.setObjectName(u"filepickerLayoutWidget")
        self.filepickerLayoutWidget.setGeometry(QRect(8, 16, 150, 128))

        layout = QVBoxLayout(self.filepickerLayoutWidget)
        self.settingsLayout.addWidget(self.filepickerGroupBox)

        self.filepickerLoadButton = QPushButton()
        self.filepickerLoadButton.setObjectName(u"filepickerLoadButton")
        self.filepickerLoadButton.setText("Загрузить")
        self.filepickerLoadButton.clicked.connect(self.loadFile)
        layout.addWidget(self.filepickerLoadButton)

        self.filepickerSaveButton = QPushButton()
        self.filepickerSaveButton.setObjectName(u"filepickerSaveButton")
        self.filepickerSaveButton.setText("Сохранить")
        self.filepickerSaveButton.clicked.connect(self.saveFile)
        layout.addWidget(self.filepickerSaveButton)

        self.filepickerGroupBox.setLayout(layout)


    def setupGridSizeGroupBox(self):
        self.gridSizeGroupBox = QGroupBox(self.settingsGroupBox)
        self.gridSizeGroupBox.setObjectName(u"groupBox")
        self.gridSizeGroupBox.setTitle("Размеры")

        self.gridSizeLayoutWidget = QWidget(self.gridSizeGroupBox)
        self.gridSizeLayoutWidget.setObjectName(u"gridSizeLayoutWidget")
        self.gridSizeLayoutWidget.setGeometry(QRect(8, 16, 150, 128))

        self.gridSizeLayout = QVBoxLayout(self.gridSizeLayoutWidget)
        self.gridSizeLayout.setObjectName(u"gridSizeLayout")
        self.gridSizeLayout.setContentsMargins(8, 8, 8, 8)
        self.settingsLayout.addWidget(self.gridSizeGroupBox)

        self.rowLabel = QLabel(self.gridSizeLayoutWidget)
        self.rowLabel.setObjectName(u"rowLabel")
        self.gridSizeLayout.addWidget(self.rowLabel)

        self.rowSlider = QSlider(self.gridSizeLayoutWidget)
        self.rowSlider.setObjectName(u"rowSlider")
        self.rowSlider.setOrientation(Qt.Horizontal)
        self.rowSlider.setValue(45)
        self.gridSizeLayout.addWidget(self.rowSlider)

        self.columnLabel = QLabel(self.gridSizeLayoutWidget)
        self.columnLabel.setObjectName(u"columnLabel")
        self.gridSizeLayout.addWidget(self.columnLabel)

        self.columnSlider = QSlider(self.settingsLayoutWidget)
        self.columnSlider.setObjectName(u"columnSlider")
        self.columnSlider.setOrientation(Qt.Horizontal)
        self.columnSlider.setValue(45)
        self.gridSizeLayout.addWidget(self.columnSlider)
        self.gridSizeGroupBox.setMinimumHeight(144)


    def setupMazeGenerationGroupBox(self):
        self.mazeGenerationGroupBox = QGroupBox(self.settingsLayoutWidget)
        self.mazeGenerationGroupBox.setObjectName(u"mazeGenerationGroupBox")
        self.mazeGenerationGroupBox.setTitle("Генерация лабиринта")

        self.mazeGenerationLayoutWidget = QWidget(self.mazeGenerationGroupBox)
        self.mazeGenerationLayoutWidget.setObjectName(u"settingsLayoutWidget")
        self.mazeGenerationLayoutWidget.setGeometry(QRect(8, 8, 150, 64))

        self.mazeGenerationLayout = QVBoxLayout(self.mazeGenerationLayoutWidget)
        self.mazeGenerationLayout.setObjectName(u"settingsLayout")
        self.mazeGenerationLayout.setContentsMargins(8, 8, 8, 8)
        self.settingsLayout.addWidget(self.mazeGenerationGroupBox)

        self.randomWallsButton = QPushButton(self.mazeGenerationGroupBox)
        self.randomWallsButton.setObjectName(u"randomWallsButton")
        self.randomWallsButton.setText("Сгенерировать стены")
        self.randomWallsButton.clicked.connect(self.generateRandomGrid)
        self.mazeGenerationLayout.addWidget(self.randomWallsButton)


    def setupSettingsGroupBox(self):
        self.settingsGroupBox = QGroupBox(self.centralwidget)
        self.settingsGroupBox.setObjectName(u"groupBox")
        self.settingsGroupBox.setTitle("Редактирование сетки лабиринта")
        self.settingsGroupBox.setFixedHeight(410)

        self.settingsLayoutWidget = QWidget(self.settingsGroupBox)
        self.settingsLayoutWidget.setObjectName(u"settingsLayoutWidget")
        self.settingsLayoutWidget.setGeometry(QRect(8, 16, 176, 390))

        self.settingsLayout = QVBoxLayout(self.settingsLayoutWidget)
        self.settingsLayout.setObjectName(u"settingsLayout")
        self.settingsLayout.setContentsMargins(8, 8, 8, 8)
        self.verticalLayout.addWidget(self.settingsGroupBox)

        self.setupFileGroupBox()
        self.setupGridSizeGroupBox()
        self.setupMazeGenerationGroupBox()
        self.setupPaintGroupBox()


    def setupPaintGroupBox(self):
        self.paintGroupBox = QGroupBox(self.centralwidget)
        self.paintGroupBox.setObjectName(u"paintGroupBox")
        self.paintGroupBox.setTitle("Рисование")

        self.paintLayoutWidget = QWidget(self.paintGroupBox)
        self.paintLayoutWidget.setObjectName(u"paintLayoutWidget")
        self.paintLayoutWidget.setGeometry(QRect(8, 8, 150, 64))

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

        self.settingsLayout.addWidget(self.paintGroupBox)


    def setupAlgorithmGroupBox(self):
        self.algorithmGroupBox = QGroupBox(self.centralwidget)
        self.algorithmGroupBox.setObjectName(u"algorithmGroupBox")
        self.algorithmGroupBox.setTitle("Управление алгоритмом")
        
        self.algorithmLayoutWidget = QWidget(self.algorithmGroupBox)
        self.algorithmLayoutWidget.setObjectName(u"algorithmLayoutWidget")
        self.algorithmLayoutWidget.setGeometry(QRect(8, 16, 166, 128))
        self.algorithmLayoutWidget.setFixedHeight(128)

        self.algorithmLayout = QVBoxLayout(self.algorithmLayoutWidget)
        self.algorithmLayout.setObjectName(u"algorithmLayout")
        self.algorithmLayout.setContentsMargins(8, 8, 8, 8)
        
        self.algorithmLabel = QLabel(self.algorithmLayoutWidget)
        self.algorithmLabel.setObjectName(u"algorithmLabel")
        self.algorithmLabel.setText("Алгоритм:")
        self.algorithmLayout.addWidget(self.algorithmLabel)

        self.algorithmComboBox = QComboBox(self.algorithmLayoutWidget)

        for e in self.algorithms.keys():
            self.algorithmComboBox.addItem(e)

        self.algorithmComboBox.setObjectName(u"algorithmComboBox")
        self.algorithmComboBox.currentIndexChanged.connect(self.algorithmChangeHandler)
        self.algorithmLayout.addWidget(self.algorithmComboBox)

        self.intervalLabel = QLabel(self.algorithmLayoutWidget)
        self.intervalLabel.setObjectName(u"algorithmLabel")
        self.intervalLabel.setText("Задержка:")
        self.algorithmLayout.addWidget(self.intervalLabel)

        self.intervalSlider = QSlider(self.algorithmLayoutWidget)
        self.intervalSlider.setObjectName(u"intervalSlider")
        self.intervalSlider.setOrientation(Qt.Horizontal)
        self.intervalSlider.setValue(45)
        self.algorithmLayout.addWidget(self.intervalSlider)
        self.intervalSlider.valueChanged.connect(self.changeInterval)

        self.startButton = QPushButton(self.algorithmLayoutWidget)
        self.startButton.setObjectName(u"Start")
        self.startButton.setText("Запуск")
        self.startButton.clicked.connect(self.processStartButton)
        self.algorithmLayout.addWidget(self.startButton)

        self.verticalLayout.addWidget(self.algorithmGroupBox)
        self.horizontalLayout.addWidget(self.verticalLayoutWidget)


    def setupUi(self, MainWindow: QtWidgets.QMainWindow):
        if MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setMinimumSize(824, 624)

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(8, 8, 8, 8)
        self.horizontalLayout.setAlignment(Qt.AlignCenter)

        self.verticalLayoutWidget = QWidget(self.centralwidget)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(0, 0, 210, 582))
        self.verticalLayoutWidget.setFixedSize(210, 582)

        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")

        self.setupSettingsGroupBox()
        self.setupAlgorithmGroupBox()

        self.gridWidget = SolverGridWidget(50, 50, self.centralwidget)
        self.gridWidget.setObjectName(u"Grid Solver")

        self.rowLabel.setText("Количество строк: " + str(self.gridWidget.grid.rows))
        self.columnLabel.setText("Количество столбцов: " + str(self.gridWidget.grid.columns))

        self.rowSlider.valueChanged.connect(self.resizeGrid)
        self.columnSlider.valueChanged.connect(self.resizeGrid)

        self.horizontalLayout.addWidget(self.gridWidget)

        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        QMetaObject.connectSlotsByName(MainWindow)
