from select import select
from Grid.GridMap import *
from abc import ABC, abstractmethod
from typing import *
from queue import PriorityQueue, Queue


class SolveQueue():


    class SolveStep():
        def __init__(self, used: List[Tuple[int, int]], path: List[int], selected: Tuple[int, int]):
            self.properties = {
                'used': used,
                'cameFrom': path,
                'selected': selected
            }


    def __init__(self):
        self.queue = Queue()


    def enqueue(self, used: List[Tuple[int, int]], path: List[int], selected: Tuple[int, int]):
        self.queue.put(SolveQueue.SolveStep(used, path, selected))
    

    def dequeue(self) -> Tuple[List[Tuple[int, int]], Tuple[int, int]]:
        result = self.queue.get().properties
        return (result['used'], result['cameFrom'], result['selected'])


class PathFindingAlgorithm(ABC):

    @staticmethod
    @abstractmethod
    def solve(self, gridMap: GridMatrix, source: Tuple[int, int], target: Tuple[int, int]) -> List[Tuple[int, int]]:
        pass

    
    @staticmethod
    @abstractmethod
    def getSolveQueue(gridMatrix: GridMatrix, source: Tuple[int, int], target: Tuple[int, int]) -> SolveQueue:
        pass    


    @staticmethod
    def _reconstructPath(cameFrom: Dict[Tuple[int, int], Tuple[int, int]],
                     source: Tuple[int, int], target: Tuple[int, int]) -> List[Tuple[int, int]]:

        current: Tuple[int, int] = target
        path: List[Tuple[int, int]] = []
        while current != source: 
            path.append(current)
            current = cameFrom[current]
        path.append(source) 
        path.reverse() 
        return path


class AStarAlgorithm(PathFindingAlgorithm):
    @staticmethod
    def _heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
        (x1, y1) = a
        (x2, y2) = b
        return abs(x1 - x2) + abs(y1 - y2)


    @staticmethod
    def solve(gridMatrix: GridMatrix, source: Tuple[int, int], target: Tuple[int, int]):
        frontier = PriorityQueue()
        frontier.put((0, source))
        cameFrom: Dict[Tuple(int, int), Optional[Tuple(int, int)]] = {}
        costSoFar: Dict[Tuple(int, int), float] = {}
        cameFrom[source] = None
        costSoFar[source] = 0
        
        while not frontier.empty():
            _, current = frontier.get()
            
            if current == target:
                break
            
            for next in gridMatrix.neighbors(current):
                newCost = costSoFar[current] + 1
                if next not in costSoFar or newCost < costSoFar[next]:
                    costSoFar[next] = newCost
                    priority = newCost + AStarAlgorithm._heuristic(next, target)
                    frontier.put((priority, next))
                    cameFrom[next] = current
        


        return PathFindingAlgorithm._reconstructPath(cameFrom, source, target)


    @staticmethod
    def getSolveQueue(gridMatrix: GridMatrix, source: Tuple[int, int], target: Tuple[int, int]) -> SolveQueue:
        frontier = PriorityQueue()
        frontier.put((0, source))

        cameFrom: Dict[Tuple(int, int), Optional[Tuple(int, int)]] = {}
        costSoFar: Dict[Tuple(int, int), float] = {}

        cameFrom[source] = None
        costSoFar[source] = 0

        queue = SolveQueue()
        
        while not frontier.empty():
            _, current = frontier.get()
            
            if current == target:
                break
            
            selected = set()

            for next in gridMatrix.neighbors(current):
                newCost = costSoFar[current] + 1
                queue.enqueue(selected, cameFrom, next)
                if next not in costSoFar or newCost < costSoFar[next]:
                    selected.add(next)
                    costSoFar[next] = newCost
                    priority = newCost + AStarAlgorithm._heuristic(next, target)
                    frontier.put((priority, next))
                    cameFrom[next] = current
        


        return queue