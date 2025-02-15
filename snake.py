from tree_search import *
import math

class SnakeDomain(SearchDomain):
    def __init__(self, initial_direction, initial_position, mapa,barriers, body, traverse, width, height, goal):
        # self.name = name
        self.last_direction = initial_direction # last direction snake went
        self.last_position = initial_position   # last position snake was
        self.mapa = mapa
        self.barriers = [(p[0], p[1]) for p in barriers]
        self.body = [(p[0], p[1]) for p in body]
        self.traverse = traverse
        self.width = width
        self.height = height
        self.goal = goal
        self.directions = {"R": "d", "L": "a", "U": "w", "D": "s"}    # directions dictionary
        self.opposite_directions = {"R": "L", "L": "R", "U": "D", "D": "U"}   # opposite directions to avoid going back and the snake killing itself
        self.vectors = {"R": (1,0),"L": (-1,0),"U": (0,-1),"D": (0,1)}
        self.vectorsReserse = {(1,0): "R", (-1, 0): "L",(0,-1): "U",(0,1): "D"}
    

    # Directions
    def actions(self, point, direction):
        opposite = self.vectors[self.opposite_directions[direction]]
        return [vetor for vetor in self.vectors.values() if vetor != opposite]


    # Next point
    def result(self, point, action):
        newPoint=[point[0]+action[0],point[1]+action[1]]
        return (newPoint[0],newPoint[1])

    # Cost
    def cost(self, point, action):
        return 1

    # Go to the food or secure way
    def heuristic(self, point, goal):
        (x1, y1) = point
        (x2, y2) = goal
        return abs(x2 - x1) + abs(y2 - y1)
    

    def validPoint(self,point):
        return (self.traverse or (0 <= point[0] < self.width and 0 <= point[1] < self.height and not point in self.barriers)
            ) and not point in self.body  


    # Test if the given "goal" is satisfied in "point"
    def satisfies(self, point, goal):
        return point == goal