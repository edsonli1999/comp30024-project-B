from test_random.algorithms import optimalPathSearch
from numpy import array, roll, zeros, vectorize

# borrowed code from board.py
# Utility function to add two coord tuples
_ADD = lambda a, b: (a[0] + b[0], a[1] + b[1])

# Neighbour hex steps in clockwise order
_HEX_STEPS = array([(1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1)], 
    dtype="i,i")

# Pre-compute diamond capture patterns - each capture pattern is a 
# list of offset steps:
# [opposite offset, neighbour 1 offset, neighbour 2 offset]
#
# Note that the "opposite cell" offset is actually the sum of
# the two neighbouring cell offsets (for a given diamond formation)
#
# Formed diamond patterns are either "longways", in which case the
# neighbours are adjacent to each other (roll 1), OR "sideways", in
# which case the neighbours are spaced apart (roll 2). This means
# for a given cell, it is part of 6 + 6 possible diamonds.
_CAPTURE_PATTERNS = [[_ADD(n1, n2), n1, n2] 
    for n1, n2 in 
        list(zip(_HEX_STEPS, roll(_HEX_STEPS, 1))) + 
        list(zip(_HEX_STEPS, roll(_HEX_STEPS, 2)))]

# Maps between player string and internal token type
_TOKEN_MAP_OUT = { 0: None, 1: "red", 2: "blue" }
_TOKEN_MAP_IN = {v: k for k, v in _TOKEN_MAP_OUT.items()}

# Map between player token types
_SWAP_PLAYER = { 0: 0, 1: -1, -1: 1 }


class Player:
    def __init__(self, player, n):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.

        The parameter player is the string "red" if your player will
        play as Red, or the string "blue" if your player will play
        as Blue. The parameter n denotes the size of the board being used.  
        """
        self.colour = player
        self.boardSize = n
        # create internal board representation of n x n
        # Open tiles = 0, red = 1, blue = -1
        n_row, n_col = (n,n)
        self.board = [[0 for x in range(n_col)] for y in range(n_row)]

        # colourDict for our int representation of colours
        self.colourDict = {'red': 1, "blue":-1, "open":0}

        # BORROWED FROM BOARD.PY
        self._data = zeros((n, n), dtype=int)
        

    def action(self):
        """
        Called at the beginning of your turn. Based on the current state
        of the game, select and returns an action to play.

        The action must be represented based on the instructions for representing actions
        """

        # action representation: 
        # ("STEAL", ) -> only playable if BLUE as their first move of the game
        # ("PLACE", r, q) -> played by both RED and BLUE, r:row(x) , q:column(y)

        action = ("PLACE", 0 , 0)
        blueFlag = False
        if (self.colour == 'blue'):
            blueFlag = True

        # 1. Get bestPath from helper function
        bestPath = optimalPathSearch(self.board, self.boardSize)

        # 2. IF we are blue, consider our best path vs red's first tile 
        if (blueFlag == True):
            numRedTiles, redTiles = self.getTiles('red')
            # if red has only placed 1 tile, and that reflected(tile) is in our best path
            if(numRedTiles == 1) & (self.reflected(redTiles[0]) in bestPath):
                action = ("STEAL",)
            else:
                action = ("PLACE", bestPath[0][0], bestPath[0][1])
        else:
            action = ("PLACE", bestPath[0][0], bestPath[0][1])

        return action

    def turn(self, player, action):
        """
        Called at the end of each player's turn to inform this player of
        their chosen action. Update your internal representation of the
        game state based on this. The parameter action is the chosen
        action itself.

        Note: At the end of your player's turn, the action parameter is
        the same as what your player returned from the action method
        above. However, the referee has validated it at this point.
        """
        # updates internal state of the game by marking the board with the colour
        # of the player that played the action

        # if opponent chooses to steal, that means we are red
        # now if we are red, we need to change that 1 tile to blue
        if action[0] == 'STEAL':
            numRedTiles, redTiles = self.getTiles('red')
            r = redTiles[0][0]
            q = redTiles[0][1]
            self.board[q][r] = self.colourDict['blue']
            self.board[r][q] = self.colourDict['open']

        else:
            # x = action[1]
            # y = action[2]
            # self.board[x][y] = self.colourDict[player]
            # NEED TO CHECK FOR DIAMOND CAPTURES, AND UPDATE INTERNAL REPRESENTATION
            self.place(player, (action[1], action[2]))

        return

    def getTiles(self, colour):
        """returns number of tiles of a given colour and their coordinates"""
        counter=0
        tiles=[]
        for x in range(self.boardSize):
            for y in range(self.boardSize):
                if (self.board[x][y] == self.colourDict[colour]):
                    counter+=1
                    tiles.append((x,y))
        return (counter , tiles)

    def reflected(self, coordinate):
        """ Given (x,y) coordinates, returns (y,x) """
        return (coordinate[1], coordinate[0])

    

    # borrowed code from board.py
    def place(self, token, coord):
        """
        Place a token('red' or 'blue') on the board and apply captures if they exist.
        Return coordinates of captured tokens.
        """
        # self[coord] = token
        self.board[coord[0]][coord[1]]=self.colourDict[token]
        return self._apply_captures(coord)

    def inside_bounds(self, coord):
        """
        True iff coord inside board bounds.
        """
        r, q = coord
        return r >= 0 and r < self.boardSize and q >= 0 and q < self.boardSize

    def _apply_captures(self, coord):
        """
        Check coord for diamond captures, and apply these to the board
        if they exist. Returns a list of captured token coordinates.
        """
        # opp_type = self._data[coord]
        opp_type = self.board[coord[0]][coord[1]]
        mid_type = _SWAP_PLAYER[opp_type]
        captured = set()

        # Check each capture pattern intersecting with coord
        for pattern in _CAPTURE_PATTERNS:
            coords = [_ADD(coord, s) for s in pattern]
            # No point checking if any coord is outside the board!
            if all(map(self.inside_bounds, coords)):
                # tokens = [self._data[coord] for coord in coords]
                tokens = [self.board[coord[0]][coord[1]] for coord in coords]
                if tokens == [opp_type, mid_type, mid_type]:
                    # Capturing has to be deferred in case of overlaps
                    # Both mid cell tokens should be captured
                    captured.update(coords[1:])

        # Remove any captured tokens
        for coord in captured:
            # self[coord] = None
            r = coord[0]
            q = coord[1]
            self.board[r][q] = self.colourDict['open']

        return list(captured)