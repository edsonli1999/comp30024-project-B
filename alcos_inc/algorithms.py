from queue import PriorityQueue
from unittest.mock import _patch_dict
from numpy import array, roll

# colourDict for our int representation of colours
colourDict = {'red': 1, "blue":-1, "open":0}

# Neighbour hex steps in clockwise order
_HEX_STEPS = array([(1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1)], 
    dtype="i,i")

# Utility function to add two coord tuples
_ADD = lambda a, b: (a[0] + b[0], a[1] + b[1])

# Map between player token types
_SWAP_PLAYER = { 0: 0, 1: -1, -1: 1 }

_CAPTURE_PATTERNS = [[_ADD(n1, n2), n1, n2] 
    for n1, n2 in 
        list(zip(_HEX_STEPS, roll(_HEX_STEPS, 1))) + 
        list(zip(_HEX_STEPS, roll(_HEX_STEPS, 2)))]

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

    if board[start[0]][start[1]] == colourDict[colour]:
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
    for x in bestPaths[0]:
        for y in x:
            bestNodes.add(y)
    return (list(bestNodes), bestPaths[1])

# Algorithm that tests path length
def costTest(action, colour, board, n, currCost):
    board[action[0]][action[1]] = colourDict[colour]
    if colour == 'red':
        cost = optimalPathSearch(board,n,'blue')[1]
    else:
         cost = optimalPathSearch(board,n,'red')[1]
    return cost

def blockStrat(board, n, colour):
    bestNodes = pathAggregator(optimalPathSearch(board, n, colour))[0]
    moveWeights = dict((x,0) for x in bestNodes)
    for futureMove in bestNodes:
        # Find initial enemy cost
        if colour == 'red':
            enemyNodes, enemyCostOriginal = pathAggregator(optimalPathSearch(board, n, 'blue'))
        else:
            enemyNodes, enemyCostOriginal = pathAggregator(optimalPathSearch(board, n, 'red'))
        
        # Apply one move
        board[futureMove[0]][futureMove[1]] = colourDict[colour]
        nodeundo = _apply_captures(board, n, (futureMove[0],futureMove[1]))

        # Find delta enemy cost
        if colour == 'red':
            enemyNodes, enemyCostNew = pathAggregator(optimalPathSearch(board, n, 'blue'))
        else:
            enemyNodes, enemyCostNew = pathAggregator(optimalPathSearch(board, n, 'red'))
        
        # Save and reset board
        moveWeights[futureMove] = enemyCostNew - enemyCostOriginal
        board[futureMove[0]][futureMove[1]] = 0
        if nodeundo:
            for node in nodeundo:
                board[node[0]][node[1]] = -colourDict[colour]


    maxDamage = max(moveWeights.values())
    bestMoves = []
    for move in moveWeights.keys():
        if moveWeights[move] == maxDamage:
            bestMoves.append(move)
    return bestMoves

def _apply_captures(board, n, coord):
    """
    Check coord for diamond captures, and apply these to the board
    if they exist. Returns a list of captured token coordinates.
    """
    # opp_type = self._data[coord]
    opp_type = board[coord[0]][coord[1]]
    mid_type = _SWAP_PLAYER[opp_type]
    captured = set()

    # Check each capture pattern intersecting with coord
    for pattern in _CAPTURE_PATTERNS:
        coords = [_ADD(coord, s) for s in pattern]
        # No point checking if any coord is outside the board!
        if all(inside_bounds(x,n) for x in coords):
            # tokens = [self._data[coord] for coord in coords]
            tokens = [board[coord[0]][coord[1]] for coord in coords]
            if tokens == [opp_type, mid_type, mid_type]:
                # Capturing has to be deferred in case of overlaps
                # Both mid cell tokens should be captured
                captured.update(coords[1:])

    # Remove any captured tokens
    for coord in captured:
        # self[coord] = None
        r = coord[0]
        q = coord[1]
        board[r][q] = colourDict['open']

    return list(captured)

def inside_bounds(coord, n):
    """
    True iff coord inside board bounds.
    """
    r, q = coord
    return r >= 0 and r < n and q >= 0 and q < n

def miniMax(board, n, colour, func, depth):
    
    return 0