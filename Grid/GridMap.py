from math import floor
from random import randint
from typing import *
import enum


class GridMatrix():
    def __init__(self, rows: int, columns: int, preset: bool = False):
        self.rows = rows
        self.columns = columns
        self._cells: List[List[int]] = [[preset for i in range(columns)] for j in range(rows)]

    
    def inBounds(self, cell: Tuple[int, int]) -> bool:
        (x, y) = cell
        return 0 <= x < self.rows and 0 <= y < self.columns
    

    def passable(self, id: Tuple[int, int]) -> bool:
        return self._cells[id[0]][id[1]] == 0


    def neighbors(self, id: Tuple[int, int]) -> Iterator[Tuple[int, int]]:
        (x, y) = id
        neighbors = [(x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)] 
        if (x + y) % 2 == 0: neighbors.reverse() 
        results = filter(self.inBounds, neighbors)
        results = filter(self.passable, results)
        return results


    def resize(self, rows: int, columns: int) -> None:
        self._cells = [[self._cells[j][i] if (j < self.rows and i < self.columns) else False for i in range(columns)] for j in range(rows)]
        self.rows = rows
        self.columns = columns


    def setCell(self, cell: Tuple[int, int]):
        self._cells[cell[0]][cell[1]] = True


    def resetCell(self, cell: Tuple[int, int]):
        self._cells[cell[0]][cell[1]] = False


    def getCell(self, cell: Tuple[int, int]) -> bool:
        return self._cells[cell[0]][cell[1]]

    
    @staticmethod
    def createMaze(rows: int, columns: int):
        result = GridMatrix(rows, columns, preset=True)

        x = randint(0, floor((result.columns - 1) / 2)) * 2 
        y = randint(0, floor((result.rows - 1) / 2)) * 2 

        result.resetCell((y, x))

        toCheck = []
        if y - 2 >= 0:
            toCheck.append((y - 2, x))
        elif y + 2 < result.rows:
            toCheck.append((y + 2, x))
        if x - 2 >= 0:
            toCheck.append((y, x - 2))
        elif x + 2 < result.columns:
            toCheck.append((y, x + 2))

        while len(toCheck) > 0:
            index = randint(0, len(toCheck) - 1) 

            y, x = toCheck[index]
            toCheck.remove((y, x))

            if result.getCell((y, x)):
                result.resetCell((y, x))
                
                if y - 2 >= 0 and result.getCell((y - 2, x)):
                    toCheck.append((y - 2, x))

                if y + 2 < result.rows and result.getCell((y + 2, x)):
                    toCheck.append((y + 2, x))
                    
                if x - 2 >= 0 and result.getCell((y, x - 2)):
                    toCheck.append((y, x - 2))

                if x + 2 < result.columns and result.getCell((y, x + 2)):
                    toCheck.append((y, x + 2))

            neighbors = list(filter(result.inBounds, [(y + 1, x), (y - 1, x), (y, x - 1), (y, x + 1)]))
            r = randint(0, len(neighbors) - 1)
            result.resetCell(neighbors[r])

        return result

