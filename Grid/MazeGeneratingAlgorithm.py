from math import floor
from random import randint, random
from Grid.GridMap import GridMatrix
from abc import ABC, abstractmethod
from typing import Tuple, List


class MazeGeneratingAlgorithm(ABC):
    @staticmethod
    def isOnGrid(node: Tuple[int, int], rows: int, columns: int) -> bool:
        return node[1] >= 0 and node[0] >= 0 and node[0] < rows and node[1] < columns


    @staticmethod
    def isNotCorner(node: Tuple[int, int], x: int, y: int) -> bool:
        return node[0] == x or node[1] == y
 

    @staticmethod
    def isNotNode(node: Tuple[int, int], x: int, y: int) -> bool:
        return not(node[0] == x and node[1] == y)


    @staticmethod
    @abstractmethod
    def generate(rows: int, columns: int) -> GridMatrix:
        pass 


class DfsMazeGenerator(MazeGeneratingAlgorithm):

    @staticmethod
    def __findNeighbors(node: Tuple[int, int], rows: int, columns: int):
        neighbors = []

        for y in range(node[1] - 2, node[1] + 3, 2):
            for x in range(node[0] - 2, node[0] + 3, 2):
                if MazeGeneratingAlgorithm.isOnGrid((x, y), rows, columns) and (
                        MazeGeneratingAlgorithm.isNotCorner(node, x, y) and (
                            MazeGeneratingAlgorithm.isNotNode(node, x, y))):
                    neighbors.append((x, y))

        return neighbors


    @staticmethod
    def generate(rows: int, columns: int) -> GridMatrix:
        result = GridMatrix(rows, columns, preset=True)

        for x in range(floor((result.rows - 1) / 2) * 2 + 1, result.rows):
            for y in range(result.columns):
                result.tryResetCell((x, y))

        for y in range(floor((result.columns - 1) / 2) * 2 + 1, result.columns):
            for x in range(result.rows):
                result.tryResetCell((x, y))
                

        x = randint(0, floor((result.rows - 1) / 2)) * 2 
        y = randint(0, floor((result.columns - 1) / 2)) * 2

        visited = set() 

        pathStack = [(x, y)]
        visited.add((x, y))

        while len(pathStack) > 0:
            cell = pathStack.pop()
            neighbors = list(filter(lambda x: not (x in visited), DfsMazeGenerator.__findNeighbors(cell, rows, columns)))

            if len(neighbors) > 0:
                randomIndex = randint(0, len(neighbors) - 1)

                for i in range(len(neighbors)):
                    result.tryResetCell(neighbors[i])
                    visited.add(neighbors[i])

                    if neighbors[i][0] == cell[0]:
                        if neighbors[i][1] < cell[1]:
                            result.tryResetCell((neighbors[i][0], neighbors[i][1] + 1))
                            
                        elif neighbors[i][1] > cell[1]:
                            result.tryResetCell((neighbors[i][0], neighbors[i][1] - 1))
                        
                    elif neighbors[i][1] == cell[1]:
                        if neighbors[i][0] < cell[0]:
                            result.tryResetCell((neighbors[i][0] + 1, neighbors[i][1]))
                            
                        elif neighbors[i][0] > cell[0]:
                            result.tryResetCell((neighbors[i][0] - 1, neighbors[i][1]))

                    if i != randomIndex:
                        
                        pathStack.append(neighbors[i])
            
                pathStack.append(neighbors[randomIndex])


        return result