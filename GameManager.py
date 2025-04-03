

class Cell:
    def __init__(self):
        self.known = False
        self.data = CellState.UNCLICKED
        self.isMine = False
        self.numKnownBorderMines = None

        self.frontier = False


class CellState(Enum):
    UNCLICKED = 1000
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8

class GameManager:
    def __init__(self, numRows, numCols):
        self.board = [[CellState.UNCLICKED for _ in range(numCols)] for _ in range(numRows)]

    
    def reset_game(): # Clicks on the smiley face to reset the game.
        click(729, 252)