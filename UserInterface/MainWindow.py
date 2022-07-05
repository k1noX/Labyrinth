from UserInterface.GridWidget import SolverGridWidget

from PyQt5.QtCore import (QMetaObject, QRect, Qt)
from PyQt5.QtWidgets import *  
import PyQt5.QtWidgets as QtWidgets

from math import floor


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

        self.gridWidget = SolverGridWidget(50, 50, self.horizontalLayoutWidget)
        self.gridWidget.setObjectName(u"Grid Solver")

        self.rowLabel.setText("Количество строк: " + str(self.gridWidget.grid.rows))
        self.columnLabel.setText("Количество столбцов: " + str(self.gridWidget.grid.columns))

        self.rowSlider.valueChanged.connect(self.resizeGrid)
        self.columnSlider.valueChanged.connect(self.resizeGrid)

        self.horizontalLayout.addWidget(self.gridWidget)

        QMetaObject.connectSlotsByName(MainWindow)