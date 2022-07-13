from math import floor
from random import randint
from typing import *


class GridMatrix():
    def __init__(self, rows: int, columns: int, preset: bool = False):
        self.rows = rows
        self.columns = columns
        self._cells: List[List[int]] = [[preset for i in range(columns)] for j in range(rows)]

    
    def inBounds(self, cell: Tuple[int, int]) -> bool:
        (x, y) = cell
        return 0 <= x < self.rows and 0 <= y < self.columns


    def neighbors(self, id: Tuple[int, int]) -> Iterator[Tuple[int, int]]:
        (x, y) = id
        neighbors = [(x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)] 
        if (x + y) % 2 == 0: neighbors.reverse() 
        results = filter(self.inBounds, neighbors)
        results = filter(lambda x: not self.getCell(x), results)
        return results


    def tryResize(self, rows: int, columns: int) -> bool:
        if rows > 9 and columns > 9:
            self._cells = [[self._cells[j][i] if (j < self.rows and i < self.columns) else False for i in range(columns)] for j in range(rows)]
            self.rows = rows
            self.columns = columns
            return True
        else:
            return False


    def trySetCell(self, cell: Tuple[int, int]) -> bool:
        if self.inBounds(cell):
            self._cells[cell[0]][cell[1]] = True
            return True
        else:
            return False


    def tryResetCell(self, cell: Tuple[int, int]) -> bool:
        if self.inBounds(cell):
            self._cells[cell[0]][cell[1]] = False
            return True
        else:
            return False


    def getCell(self, cell: Tuple[int, int]) -> bool:
        if self.inBounds(cell):
            return self._cells[cell[0]][cell[1]]
        else:
            return False

