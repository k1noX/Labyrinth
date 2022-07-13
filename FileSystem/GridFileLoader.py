from tkinter import Grid
from FileSystem.GridFileException import *
from Grid.GridMap import GridMatrix


class GridFileLoader():
    def __init__(self, file: str):
        self.__file = file

    def load(self) -> GridMatrix:
        try:
            file = open(self.__file, 'r')
        except OSError:
            raise GridFileException(f"Файл не может быть открыт!\nФайл: {self.__file}")
        else:
            lines = file.readlines()

            if len(lines) < 2:
                raise FileFormatException(f"Файл: {self.__file}")

            try:
                rows, columns = [int(i) for i in lines[0].split()]

                result = GridMatrix(1, 1)
                
                if not result.tryResize(rows, columns):
                    raise FileFormatException(f"Неверные размеры матрицы!\nФайл: {self.__file}")

                for i in range(rows):
                    line = lines[1:][i].split()
                    for j in range(columns):
                        if int(line[j]) == 1:
                            result.trySetCell((i, j))
                            
                return result

            except ValueError:
                raise FileFormatException(f"Файл: {self.__file}")
                
