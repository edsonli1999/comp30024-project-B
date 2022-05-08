from alcos_inc.algorithms import optimalPathSearch

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
        if (self.colour == 'blue'):
            blueFlag = True

        # 1. Get bestPath from helper function
        bestPath = optimalPathSearch(self.board, self.n)

        # 2. IF we are blue, consider our best path vs red's first tile 
        if (blueFlag):
            numRedTiles, redTiles = getNumTiles(self, 'red')
            # if red has only placed 1 tile, and that tile is in our best path
            if(numRedTiles == 1):
                if redTiles[0] in bestPath:
                    action = ("STEAL",)
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
        self.board[action[1]][action[2]] = self.colourDict[player]
        
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
        return counter , tiles
