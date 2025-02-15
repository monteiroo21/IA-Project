# Students:
# 113144 - João Viegas
# 113278 - Jorge Domingues
# 114547 - João Monteiro

"""Example client."""
import asyncio
import getpass
import json
import os
import time
import websockets
import random
from collections import deque


DirectionsKeys = {"R": "d", "L": "a", "U": "w", "D": "s"}    # directions dictionary
CoordDirections = {"R": (1,0), "L": (-1,0), "U": (0,-1), "D": (0,1)} # directions to vectors
oppositeDirections = {"R": "L", "L": "R", "U": "D", "D": "U"}   # opposite directions to avoid going back and the snake killing itself

def sumPoints(point1, point2, width, height, traverse=False):
    x, y = point1[0] + point2[0], point1[1] + point2[1]
    
    if traverse:
        x = (x + width) % width
        y = (y + height) % height
    
    return [x, y]


def multiPoint(point, mult):
    return [point[0] * mult, point[1] * mult]


def validPosition(newPosition, width, height, allBody, traverse=False):
    if traverse:
        i,j = newPosition
        if i < 0:
            i = width + i
        if j < 0:
            j = height + j
        if i >= width:
            i = i - width
        if j >= height:
            j = j - height
        newPosition = [i, j]

    return (traverse or (0 <= newPosition[0] < width and 0 <= newPosition[1] < height)
            ) and not newPosition in allBody 


def calculateDistance(point1, point2, width, height, traverse=False):
    x1, y1 = point1
    x2, y2 = point2

    if traverse:
        dx = min(abs(x2 - x1), width - abs(x2 - x1))
        dy = min(abs(y2 - y1), height - abs(y2 - y1))
        return (dx**2 + dy**2)**0.5
    else:
        return ((x2 - x1)**2 + (y2 - y1)**2)**0.5


def wallsPositions(map, traverse=False):
    coordinates = []
    for i in range(len(map)):  
        for j in range(len(map[i])):
            if map[i][j] == 1:
                if traverse:
                    map[i][j] = 0
                else:
                    coordinates.append([i, j])
    return coordinates


def isPathPossibleBySpeedGreedy(newPosition, safepoint, allBody, width, height, traverse):
    time2 = time.time()
    if newPosition == safepoint:
        return True
    openList = [newPosition]
    closeList = [i for i in allBody]

    while openList:
        atual = openList.pop(0)
        closeList.append(atual)
        for movimento in CoordDirections.values():
            neighbor = sumPoints(atual, movimento, width, height, traverse)
            if neighbor == safepoint:
                return True
            
            if validPosition(neighbor, width, height, closeList, traverse) and neighbor not in openList:
                    openList.append(neighbor)

        if (time.time()-time2)>0.01:
            return True
        openList.sort(key=lambda x:calculateDistance(x, safepoint, width, height, traverse))
    return False



def clearMap(map, traverse, width, height):
    for y in range(height):
        for x in range(width):
            if map[x][y] in [4,5,6]:
                map[x][y] = 0
            elif map[x][y] in [8,9]:
                map[x][y] -= 6
            elif traverse and  map[x][y]==1:
                map[x][y] = 0
    return map


NumOfSuperFood = [0]
def foundFood(map, head, igoneSuperFood, width, height):
    NumOfSuperFood[0] = 0
    foodList=[]
    for y in range(height):
        for x in range(width):
            if map[x][y] == 2:
                foodList.append([x, y, map[x][y]])
            if map[x][y] == 3 :
                NumOfSuperFood[0] += 1

                if not igoneSuperFood:
                    foodList.append([x, y, map[x][y]])

    if len(foodList)>0:
        foodList.sort(key=lambda x:((x[0]-head[0])**2+(x[1]-head[1])**2)**0.5)
        return foodList[0]
    
    return None


def foundSuperFoodList(map, width, height):
    foodList=[]
    for y in range(height):
        for x in range(width):
            if map[x][y] == 3:
                foodList.append([x, y])
    return foodList

def bestFoodOutBounds(point1, point2, width, height, traverse):
    list1=[]
    for i in [-width, 0, width]:
        for ii in [-height, 0, height]:
            wrapped_point = sumPoints(point2, [i, ii], width, height, traverse)
            list1.append(wrapped_point)
    list1.sort(key=lambda el:calculateDistance(point1, el, width, height, traverse))
    return list1[0]


def divideMap(width, height):
    midX = width // 2
    midY = height // 2

    top_left = ([0, midX], [0, midY])
    top_right = ([midX, width], [0, midY])
    bottom_left = ([0, midX], [midY, height])
    bottom_right = ([midX, width], [midY, height])

    return top_left, top_right, bottom_left, bottom_right


def safePoints(borders, walls):
    safe_points = []
    for border in borders:
        x_range, y_range = border
        valid_point_found = False
        
        while not valid_point_found:
            random_x = random.randint(x_range[0] + 2, x_range[1] - 3)
            random_y = random.randint(y_range[0] + 2, y_range[1] - 3)
            
            point_is_safe = True
            for x in range(random_x - 2, random_x + 2):
                for y in range(random_y - 2, random_y + 2):
                    if (x, y) in walls:
                        point_is_safe = False
                        break
                if not point_is_safe:
                    break
            
            if point_is_safe:
                safe_points.append([random_x, random_y])
                valid_point_found = True
    
    return safe_points


def bfs_dead_end_check(start_position, snake_body, food, map, width, height, traverse):
    visited = set(tuple(segment) for segment in snake_body) 
    queue = deque([tuple(start_position)])

    while queue:
        current = queue.popleft()
        if current == tuple(food):
            return True
        for direction, vector in CoordDirections.items():
            neighbor = sumPoints(list(current), vector, width, height, traverse)
            if 0 <= neighbor[0] < height and 0 <= neighbor[1] < width:
                if (tuple(neighbor) not in visited
                        and map[neighbor[1]][neighbor[0]] not in (1, 6)):
                    visited.add(tuple(neighbor))
                    queue.append(tuple(neighbor))
            else:
                pass
    return False


def foundFoodInColumn(map, column_index):
    for row in range(len(map)):
        if map[row][column_index] == 2:  # Assuming 2 represents food
            return [row, column_index]  # Return the position of the food found
    return None 

def nearest_safe_point(snake_head, safe_points, width, height, allBody, traverse):
    nearest_point = None
    min_distance = float('inf')
    for point in safe_points:
        distance = abs(snake_head[0] - point[0]) + abs(snake_head[1] - point[1])
        if distance < min_distance and validPosition(point,width,height,allBody,traverse):
            min_distance = distance
            nearest_point = point
    return nearest_point

def sumZeros(point, map, rangeValue,traverse,isInCombat):
    count = 0 
    x, y = point

    for dy in range(-rangeValue, rangeValue + 1):
        for dx in range(-rangeValue, rangeValue + 1):
            nx, ny = x + dx, y + dy

            if 0 <= nx < len(map) and 0 <= ny < len(map[0]):
                if map[nx][ny] != 0:
                    count += 1 
            else:
                if not traverse:
                    count += 0.5

                if nx < 0:
                    nx =  len(map) + nx
                if ny < 0:
                    ny = len(map[0]) + ny
                if nx >=  len(map):
                    nx = nx -  len(map)
                if ny >= len(map[0]):
                    ny = ny - len(map[0])
                if map[nx][ny] != 0:
                    count += 1
            if isInCombat:
                if map[nx][ny] == 1:
                    count += 1
                elif map[nx][ny] == 6:
                    count += 20
    return count

def writeBody(map,body):
    for x,y in body:
        map[x][y]=4

def calculate_future_positions(body, directions, width, height, traverse=False):
    future_body = body.copy()

    for direction in directions:
        vetor = CoordDirections[direction]
        new_head = sumPoints(future_body[0], vetor, width, height, traverse)
        future_body = [new_head] + future_body[:-1] 

    return future_body


def enemyBodyDetection(map, enemy_positions, width, height):
    for enemy in enemy_positions:
        x, y = enemy
        if 0 <= x < width and 0 <= y < height:  # Check if the enemy is within the map
            map[x][y] = 6  # Mark the enemy on the map
    return map


from snake import SnakeDomain
from tree_search import SearchTree
from queue import Queue

async def agent_loop(server_address="localhost:8000", agent_name="student"):
    """Example client loop."""
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        count = "R"
        last = "R"
        width = 0
        height = 0
        wallsCoord = None
        map = None
        lastFood = None
        food = None
        path = Queue()
        
        rangeValue = 3
        limitFood = 3
        numFoodFound = set()
        listOfBlockFoods = []
        ignoreSuperFood = False        
        worst_time = 0
        LimitSuperFood = False
        isInCombat=False
        NumPlayers=0
        lastScore=0

        while True:
            try:
                state = json.loads(await websocket.recv())

                # Update map and size from state
                if 'map' in state:
                    wallsCoord = wallsPositions(state["map"], state.get("traverse", False))
                    map = state["map"]

                if 'size' in state:
                    width, height = state["size"]
                    divMap=divideMap(width,height)
                    safetyPoints=safePoints(divMap,wallsCoord)
                    for x, y in safetyPoints:
                        map[x][y] = 7

                if 'score' in state: 
                    if NumPlayers == 0:
                        NumPlayers = len(state["players"])

                    if state["score"] - lastScore > 90:
                        NumPlayers -= 1
                    if NumPlayers>1:
                        isInCombat=True
                    else:
                        isInCombat=False
                    lastScore=state["score"]


                if 'range' in state:
                    rangeValue = state["range"]
                    if rangeValue >= (5 if not isInCombat else 4) and state.get("traverse", False):
                        ignoreSuperFood = True

                    if state['step'] >= state['timeout'] - 300:
                        ignoreSuperFood = False

                    if rangeValue < 3:
                        pass

                    if NumOfSuperFood[0] >= 25 or LimitSuperFood:
                        ignoreSuperFood = False
                        LimitSuperFood= True
                    if NumOfSuperFood[0] == 0 or LimitSuperFood:
                        LimitSuperFood= False

                # Process sight to update the map and enemies
                enemy = []
                if 'sight' in state:
                    sight = state["sight"]
                    for x, sight_row in sight.items():
                        for y, value in sight_row.items():
                            if map[int(x)][int(y)] in [8,9]:
                                continue
                            if value == 0:
                                value = 5  # Mark unseen areas
                            if value == 4 and [int(x), int(y)] not in state["body"]:
                                value = 6
                                if [int(x), int(y)] not in enemy:
                                    enemy.append([int(x), int(y)])  # Track enemies
                            map[int(x)][int(y)] = value
                    map = enemyBodyDetection(map, enemy, width, height)

                    if not state.get("traverse", False):
                        for x,y in wallsCoord:
                            map[x][y] = 1
                if "body" not in state:
                    await websocket.send(json.dumps({"cmd": "key", "key": DirectionsKeys[count]}))
                    continue
                
                snake_head = state["body"][0]
                head = snake_head
                tail = state["body"][-1]
                allBody = state["body"] + (wallsCoord if not state.get("traverse", False) else []) + enemy + (foundSuperFoodList(map, width, height) if ignoreSuperFood else [])+listOfBlockFoods 
                food = foundFood(map, head, ignoreSuperFood, width, height)
                traverse = state.get("traverse", False)

                safePoint=nearest_safe_point(head,safetyPoints,width,height,allBody,traverse)
                if safePoint is None:
                    safePoint=tail

                # Handle food pathfinding
                if food is not None and path.empty():
                    lastFood = food
                    if food[2] == 2:
                        numFoodFound.add((food[0], food[1]))
                    if traverse:
                        food_point = (food[0], food[1])
                        food = bestFoodOutBounds(head, food_point, width, height, traverse)
                        if not validPosition(food, width, height, allBody, traverse):
                            food = food_point

                    problem = SnakeDomain(last, head, map, wallsCoord, state["body"], traverse, width, height, (food[0], food[1]))
                    search_tree = SearchTree(problem, 'a*')
                    list_path = search_tree.search()
                    if list_path is not None: 
                        path = Queue()
                        for direction in list_path:
                            path.put(direction)

                if food is not None and lastFood is not None and food != lastFood:
                    path = Queue()
                    food = foundFood(map, head, ignoreSuperFood, width, height)
                    lastFood = food
                    if food[2] == 2:
                        numFoodFound.add((food[0], food[1]))
                    problem = SnakeDomain(last, head, map, wallsCoord, state["body"], traverse, width, height, (food[0], food[1]))
                    search_tree = SearchTree(problem, 'a*')
                    list_path = search_tree.search()
                    
                    if list_path is not None:                        
                        for direction in list_path:
                            path.put(direction)
                    else:
                        food = None

                # Fallback to safe movement if no path is available
                if path.empty():
                    if lastFood is not None and len(numFoodFound)>=limitFood:
                        map = clearMap(map, traverse, width, height)
                        writeBody(map,state["body"])
                        lastFood = None
                        numFoodFound=set()

                    # count = line_scan(head, last, width, height, rangeValue)
                    points=[]
                    for direcao, vetor in CoordDirections.items():
                        if direcao == oppositeDirections[last]:
                            continue
                        newPosition = sumPoints(head, multiPoint(vetor, rangeValue), width, height, traverse)
                        if validPosition(newPosition, width, height, allBody):
                            points.append((direcao,newPosition,sumZeros(newPosition,map,rangeValue,traverse,isInCombat)))
                    if len(points) > 0:
                        points.sort(key=lambda x :x[2])
                        count = points[0][0]
                        if all((point[2] >= ((rangeValue*2+1)**2)) for point in points):
                            clearMap(map, traverse, width, height)
                            writeBody(map,state["body"])
                    else:
                        count = last
                   
                # Continue along the path if available
                if not path.empty():
                    count = path.get()

                newPosition = sumPoints(head, CoordDirections[count], width, height, traverse)
                if not validPosition(newPosition, width, height, allBody, traverse) or not isPathPossibleBySpeedGreedy(newPosition, safePoint, allBody, width, height, traverse):
                    for direcao, vetor in CoordDirections.items():
                        if direcao == oppositeDirections[last] or direcao == count:
                            continue
                        newPosition = sumPoints(head, vetor, width, height, traverse)
                        if validPosition(newPosition, width, height, allBody, traverse) and isPathPossibleBySpeedGreedy(newPosition, safePoint, allBody, width, height, traverse):
                            count = direcao
                            break
                    path = Queue()

                # Update movement key and send to the server
                key = DirectionsKeys[count]
                last = count

                await websocket.send(json.dumps({"cmd": "key", "key": key}))


            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return
            except Exception as e:
                print(f"Error occurred: {e}")
                pass
            

# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))