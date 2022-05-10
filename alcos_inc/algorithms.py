from queue import PriorityQueue
from unittest.mock import _patch_dict

# colourDict for our int representation of colours
colourDict = {'red': 1, "blue":-1, "open":0}

'Heuristic function which calculates node distance to goal based on row and column distance'
def distance(location,goal):
    locationCube = offsetToCube(location)
    goalCube = offsetToCube(goal)
    return (abs(locationCube[0] -goalCube[0]) + abs(locationCube[1] - goalCube[1]) + abs (locationCube[2] - goalCube[2]))/2

'Generates children based on an offset list and board location/proximity'
def generateChildren(board, location, n, colour):
    children = []
    offsets = [(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1)]
    for x,y in offsets:
        if ((location[0] + x in range(0,n) and location[1] + y in range(0,n)) and (board[location[0] + x][location[1] + y] != -colourDict[colour])):
            children.append((location[0] + x, location[1] + y))
    return children

def cubeToOffset(node):
    q = node[0] - (node[1] - node[1]&1)/2
    r = node[1]
    return [r,q]

def offsetToCube(node):
    q = node[1] - (node[0] - node[0]&1)/2
    r = node[0]
    return [q,r, -q-r]


# A slightly altered implementation of Dijkstra's algorithm with a heuristic function.
# This algorithm  creates a priority queue, a dictionary of previous paths, and a dictionary of
# current path costs for each given grid tile. It starts at the start location and generates a series
# of possible paths via the generateChildren() function. It then iterates over each child location. 
# If the child has not yet been visited or if the current child node has a cheaper cost to visit a 
# previously known child node, then the algorithm will build the path by inserting the current node
# as the previously visited node for the child node in the previous paths dictionary. It will then 
# insert the cost of the path so far into the cost dictionary for the child node. Lastly it will
# push this child node to the priority queue, adding it to the list of nodes to visit once the current
# set of children has finished iterating.
# The algorithm will then pop the next node and iterate based on the priority value which is generated
# using the current path length (i.e. g(n)) plus the heuristic value (h(n)). It will continue generating
# children and checking paths until it has found the goal node

# Note that some of the specific structure of the algorithm was adapted from the A* algorithm implemented at the following website:
# https://www.redblobgames.com/pathfinding/a-star/implementation.html#python-astar

def lineHeuristicAlgo(board, start, goal, n, colour):
    pq = PriorityQueue()
    pq.put((0,tuple(start)))
    previousDict = {}
    currCost = {}
    previousDict[tuple(start)] = None

    if board[goal[0]][goal[1]] == colourDict[colour]:
        currCost[tuple(start)] = 0
    else:
        currCost[tuple(start)] = 1

    while not pq.empty():
        currNode = pq.get()[1]

        if currNode == goal:
            break
        
        for nextNode in generateChildren(board, currNode, n, colour):
            if board[currNode[0]][currNode[1]] == colourDict[colour]:
                nextCost = currCost[currNode]
            else:
                nextCost = currCost[currNode] + 1
            if nextNode not in currCost or nextCost < currCost[nextNode]:
                currCost[nextNode] = nextCost
                pq.put((distance(nextNode, goal) + currCost[nextNode], nextNode))
                previousDict[nextNode] = currNode
    return previousDict, currCost

'Driver function that calls A* search on every valid start and end for the player to find the best direct path, and returns nodes along that path'
def optimalPathSearch(board, n, colour):
    bestCost = n*n
    bestPath = []
    pathList = {}
    for x in range(0,n):
        for y in range (0,n):
            if colour == 'red':
                if -colourDict[colour] in [board[0][x], board[n-1][y]]:
                    continue
                previousDict, currCost = lineHeuristicAlgo(board,(0,x),(n-1,y),n, colour)

                # If there is no valid path, lineHeuristicAlgo will return zero on whathever the goal is - must test for this:
                if (n-1,y) in currCost.keys():
                    if currCost[(n-1,y)] <= bestCost:
                        bestCost = currCost[(n-1,y)]
                        bestPath = buildPath(previousDict, (n-1,y), board)
                        pathList[bestPath] = bestCost
            else:
                if -colourDict[colour] in [board[x][0], board[y][n-1]]:
                    continue
                previousDict, currCost = lineHeuristicAlgo(board,(x,0),(y,n-1),n, colour)

                if (y,n-1) in currCost.keys():
                    if currCost[(y,n-1)] <= bestCost:
                        bestCost = currCost[(y,n-1)]
                        bestPath = buildPath(previousDict, (y,n-1), board)
                        pathList[bestPath] = bestCost

    bestPaths = []
    for x in pathList.keys():
        if pathList[x] == bestCost:
            bestPaths.append(x)
    
    return (bestPaths, bestCost)

'Small function to rebuild goal path based on the previous node dictionary, as well as the known cost'
def buildPath(previousDict: dict, goal, board):
    currNode = tuple(goal)
    path = []
    if board[goal[0]][goal[1]] == 0:
        path = [currNode]
        
    while previousDict[currNode]:
        currNode = previousDict[currNode]
        if currNode == None:
            break
        if board[currNode[0]][currNode[1]] == 0:
            path.append(currNode)

    return tuple(path)

def pathAggregator(bestPaths):
    bestNodes = set()
    for x in bestPaths:
        for y in x:
            bestNodes.add(y)
    return list(bestNodes)

# Algorithm that tests path length
def costTest(action, colour, board, n, currCost):
    board[action[0]][action[1]] = colourDict[colour]
    if colour == 'red':
        cost = optimalPathSearch(board,n,'blue')[1]
    else:
         cost = optimalPathSearch(board,n,'red')[1]
    return cost