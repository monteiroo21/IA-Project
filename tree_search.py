# Module: tree_search
# 
# This module provides a set o classes for automated
# problem solving through tree search:
#    SearchDomain  - problem domains
#    SearchProblem - concrete problems to be solved
#    SearchNode    - search tree nodes
#    SearchTree    - search tree with the necessary methods for searhing
#
#  (c) Luis Seabra Lopes
#  Introducao a Inteligencia Artificial, 2012-2020,
#  Inteligência Artificial, 2014-2023

from itertools import count
from abc import ABC, abstractmethod
# Dominios de pesquisa
# Permitem calcular
# as accoes possiveis em cada estado, etc
class SearchDomain(ABC):

    # construtor
    @abstractmethod
    def __init__(self):
        pass

    # lista de accoes possiveis num estado
    @abstractmethod
    def actions(self, point):
        pass

    # resultado de uma accao num estado, ou seja, o estado seguinte
    @abstractmethod
    def result(self, point, action):
        pass

    # custo de uma accao num estado
    @abstractmethod
    def cost(self, point, action):
        pass

    # custo estimado de chegar de um estado a outro
    @abstractmethod
    def heuristic(self, point, goal):
        pass

    # test if the given "goal" is satisfied in "point"
    @abstractmethod
    def satisfies(self, point, goal):
        pass


# Nos de uma arvore de pesquisa
class SearchNode:
    def __init__(self, point, parent, cost, heuristic, action): 
        self.point = point
        self.parent = parent
        self.depth = parent.depth + 1 if parent != None else 0
        self.cost = cost
        self.heuristic = heuristic
        self.action = action

    def __str__(self):
        return "no(" + str(self.point) + "," + str(self.parent) + ")"
    def __repr__(self):
        return str(self)
    
    def in_parent(self, newpoint):
        if self.parent == None:
            return False
        if self.parent.point == newpoint:
            return True
        
        return self.parent.in_parent(newpoint)

# Arvores de pesquisa
class SearchTree:

    # construtor
    def __init__(self,problem, strategy='breadth'): 
        self.problem = problem
        root = SearchNode(problem.last_position, None, 0, self.problem.heuristic(problem.last_position, problem.goal), self.problem.vectors[self.problem.last_direction])
        self.close_nodes=[]
        self.strategy = strategy
        self.solution = None
        self.counter = count()
        self.non_terminals = 0
        self.highest_cost_nodes = [root]
        self.sum_depths = root.depth
        self.open_nodes = [root]

    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self,node):
        if node.parent == None:
            return [node.point]
        path = self.get_path(node.parent)
        path += [node.point]
        return(path)
    
    @property
    def plan(self):
        return self.get_plan(self.solution)

    def get_plan(self, node):
        if node.parent == None:
                return []
        plan = self.get_plan(node.parent)
        plan += [node.action]
        return plan
    
    def get_planDirection(self, node):
        if node.parent == None:
                return []
        plan = self.get_planDirection(node.parent)
        plan += [self.problem.vectorsReserse[node.action]]
        return plan
    
    @property
    def average_depth(self):
        return self.sum_depths / (self.non_terminals + self.terminals)
    
    @property
    def length(self):
        return self.solution.depth if self.solution else 0
    
    @property 
    def terminals(self):
        return len(self.open_nodes) + 1
    
    @property
    def avg_branching(self):
        return (self.terminals + self.non_terminals - 1) / self.non_terminals
    
    @property
    def cost(self):
        return self.solution.cost

    # procurar a solucao
    def search(self, limit=100):
        try:
            while self.open_nodes != []:
                
                node = self.open_nodes.pop(0)

                if self.problem.satisfies(node.point,self.problem.goal):
                    self.solution = node
                    return self.get_planDirection(node)
                
                self.non_terminals += 1
                
                if limit != None and node.depth >= limit:
                    continue

                lnewnodes = []
                for a in self.problem.actions(node.point,self.problem.vectorsReserse[node.action]):
                    newpoint = self.problem.result(node.point, a)

                    if node.in_parent(newpoint):
                        continue
                    if not self.problem.validPoint(newpoint):
                        continue
                    cost = node.cost + self.problem.cost(node.point, a)
                    heuristic = self.problem.heuristic(newpoint, self.problem.goal)
                    newnode = SearchNode(newpoint, node, cost, heuristic, a)
                    lnewnodes.append(newnode)

                self.close_nodes.append(node.point)
                self.add_to_open(lnewnodes)
        except KeyboardInterrupt:
            return

        return None

    # juntar novos nos a lista de nos abertos de acordo com a estrategia
    def add_to_open(self,lnewnodes):
        if self.strategy == 'breadth':
            self.open_nodes.extend(lnewnodes)
        elif self.strategy == 'depth':
            self.open_nodes[:0] = lnewnodes
        elif self.strategy == 'uniform':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key=lambda n: n.cost)
        elif self.strategy == "greedy":
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key=lambda n: n.heuristic)
        elif self.strategy == "a*":
            lnewnodes.sort(key=lambda n: n.cost + n.heuristic)
            self.open_nodes = lnewnodes
            

