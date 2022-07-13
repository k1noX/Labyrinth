from tkinter import Grid
from FileSystem.GridFileException import *
from Grid.GridMap import GridMatrix


class GridFileSaver():
    def __init__(self, grid: GridMatrix, file: str):
        self.__file = file
        self.__grid = grid

    def save(self) -> GridMatrix:
        try:
            file = open(self.__file, 'w')
        except OSError:
            raise GridFileException(f"Файл не может быть открыт!\nФайл: {self.__file}")
        else:
            file.write(f"{self.__grid.rows} {self.__grid.columns}\n")
            for i in range(self.__grid.rows):
                for j in range(self.__grid.columns):
                    file.write("1 " if self.__grid.getCell((i, j)) else "0 ")
                file.write("\n")
                
