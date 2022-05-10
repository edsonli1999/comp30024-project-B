"""
COMP30024 Artificial Intelligence, Semester 1, 2022
Project Part A: Searching

This script contains the entry point to the program (the code in
`__main__.py` calls `main()`). Your solution starts here!
"""

import sys
import json
from test_random.algorithms import buildPath, lineHeuristicAlgo
import test_random.util as util

def main():
    # Import input
    try:
        with open(sys.argv[1]) as file:
            data = json.load(file)
    except IndexError:
        print("usage: python3 -m search path/to/input.json", file=sys.stderr)
        sys.exit(1)

    # search(start, goal, n, board)
    # start = [4,2]
    # goal = [0,0]
    # n = 5
    # board = [  [0,0,1,0,0],
    #            [0,0,-1,0,0],
    #            [0,0,0,0,0],
    #            [-1,-1,0,-1,0],
    #            [2,0,0,0,0]      ]
    # 1 -> start point
    # 2 -> end goal
    # (-1) -> obstacles (or opponent)
    
    # board_dict stores the coordinates of the important structures
    # (x,y): enemy(b)/start(1)/goal(2)
    board_dict = dict()
    for obstacle in data['board']:
        board_dict[(obstacle[1], obstacle[2])] = obstacle[0]
    board_dict[tuple(data['start'])] = '1'
    board_dict[tuple(data['goal'])] = '2'


    start = data['start']
    goal = data['goal']
    n = data['n']

    n_row, n_col = (n,n)
    board = [[0 for x in range(n_col)] for y in range(n_row)]

    # Generate 2D Board array
    for coords in list(board_dict.keys()):
        if board_dict[coords] == 'b':
            board[coords[0]][coords[1]] = -1
        if board_dict[coords] == 'r':
            board[coords[0]][coords[1]] = 1
        if board_dict[coords] == '2':
            board[coords[0]][coords[1]] = 2

    # Call A* search
    previousDict, CurrCost = lineHeuristicAlgo(board, start, goal, n)
    buildPath(previousDict, CurrCost, goal, start)