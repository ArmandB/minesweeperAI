from enum import Enum
from collections import deque
class Cell:
    def __init__(self,r,c):
        self.r = r
        self.c = c
        self.data = CellState.UNCLICKED
        self.numRemainingBorderMines = None
    
    def getId(self):
        return (self.r, self.c)


class CellState(Enum):
    UNCLICKED = 1000
    MINE = 999
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8

def cvtToCellState(val):
    if val == 0:
        return CellState.ZERO
    elif val == 1:
        return CellState.ONE
    elif val == 2:
        return CellState.TWO
    elif val == 3:
        return CellState.THREE
    elif val == 4:
        return CellState.FOUR
    elif val == 5:
        return CellState.FIVE
    elif val == 6:
        return CellState.SIX
    elif val == 7:
        return CellState.SEVEN
    elif val == 8:
        return CellState.EIGHT
    elif val == 'unclicked':
        return CellState.UNCLICKED
    else:
        raise ValueError(f"Invalid cell state value: {val}")

class GameManager:
    def __init__(self, boardShape):
        self.numRows = boardShape[0]
        self.numCols = boardShape[1]

        self.frontier = deque()

        self.progressPrevTick = True

        self.board = [[Cell(r,c) for c in range(self.numCols)] for r in range(self.numRows)]
        print(f"Game Manager board shape: ({len(self.board)},{len(self.board[0])})")

    def setCellValue(self, val, r, c):
        # print(f"Setting cell ({r}, {c})")
        if r < 0 or r >= self.numRows or c < 0 or c >= self.numCols:
            print(f"Invalid cell coordinates: ({r}, {c})")
            return

        cell = self.board[r][c]
        val = cvtToCellState(val)
        assert cell.data == CellState.UNCLICKED or cell.data == val
        if cell.data == CellState.UNCLICKED:
            cell.data = val
            cell.numRemainingBorderMines = val.value - self.getNumNeighMines(r,c)

            if val != CellState.ZERO:
                # print(f"Enqueuing cell ({r}, {c}) to {val.value}")
                # print("cells r,c: ", self.board[r][c].r, self.board[r][c].c)
                self.frontier.append(self.board[r][c])

    def getCellNeighborIds(self,r,c):
        tryNodes = [(r-1,c),   (r-1,c-1), (r-1,c+1), #look up 
                    (r,  c-1), (r,  c+1), 
                    (r+1,c-1), (r+1,c),   (r+1,c+1)] #look down

        outNodes = []
        for node in tryNodes:
            r, c = node
            if r < 0 or r >= self.numRows or c < 0 or c >= self.numCols:
                continue
            outNodes.append(node)
        return outNodes

    def getUnclickedNeighIds(self, r, c):
        outIds = []
        tryNodes = self.getCellNeighborIds(r,c)
        
        for node in tryNodes:
            r, c = node
            cell = self.board[r][c]
            if cell.data == CellState.UNCLICKED:
                outIds.append((r,c))

        return outIds

    def getNumericalNeighIds(self, r, c):
        outIds = []
        tryNodes = self.getCellNeighborIds(r,c)
        
        for node in tryNodes:
            r, c = node
            cell = self.board[r][c]
            if cell.data != CellState.UNCLICKED and cell.data != CellState.ZERO and cell.data != CellState.MINE:
                outIds.append((r,c))

        return outIds

    def getFrontierNeighIds(self, r, c):
        outIds = []
        tryNodes = self.getCellNeighborIds(r,c)

        for node in tryNodes:
            r, c = node
            cell = self.board[r][c]
            if cell.numRemainingBorderMines is not None and cell.numRemainingBorderMines > 0:
                outIds.append((r,c))

        return outIds            

    def getNumNeighMines(self, r, c):
        numMines = 0
        tryNodes = self.getCellNeighborIds(r,c)
        
        for node in tryNodes:
            r, c = node
            cell = self.board[r][c]
            if cell.data == CellState.MINE:
                numMines += 1

        return numMines

    # This function is called when we find a cell that's a mine.
    # It should update the board and frontier accordingly.
    def handleSetMine(self, nodeId, mineCellIds):
        mine_r, mine_c = nodeId
        mineCell = self.board[mine_r][mine_c]
        assert mineCell.data == CellState.UNCLICKED
        mineCell.data = CellState.MINE
        mineCellIds.append((mine_r, mine_c))

        # tell adjacent cells that they have one less border mine
        mineNeighIds = self.getNumericalNeighIds(mine_r,mine_c)
        for mineNeighId in mineNeighIds:
            mineNeighCell = self.board[mineNeighId[0]][mineNeighId[1]]
            mineNeighCell.numRemainingBorderMines -= 1    
    """
    we are setting mines incorrectly.
    When we have a 2 that's bordering 2 mines AND 2 unclicked cells, we are adding 2 flags 
    ^This is happening when we are uncovering something that is immediately clickable.

    When we uncover a cell, we need to check if it is bordering any mines.
    """
    # TODO if you found mines
    def getNextClick(self, mineCellIds):
        print(f"getNextClick - Frontier size: {len(self.frontier)}")
        clickCellIds = []
        clickCellIdSet = set()

        frontierSize = len(self.frontier)
        for i in range(frontierSize):
            cell = self.frontier.popleft()
            # print("Frontier - ({},{})".format(cell.r, cell.c))

            assert cell.data != CellState.UNCLICKED and cell.data != CellState.ZERO and cell.data != CellState.MINE
            unclickedNeighIds = self.getUnclickedNeighIds(cell.r, cell.c)
            if len(unclickedNeighIds) == 0:
                continue

            # TODO can this make it so that something that was previously a frontier cell is no longer a frontier cell
            if not self.progressPrevTick:
                # Subset Inference
                currCell = cell
                currCellFrontierNeighIds = self.getFrontierNeighIds(currCell.r, currCell.c)
                currCellUnclickedNeighIdsSet = set(unclickedNeighIds)
                for frontierNeighId in currCellFrontierNeighIds:
                    frontierCell = self.board[frontierNeighId[0]][frontierNeighId[1]]
                    frontierCellUnclickedNeighIdsSet = set(self.getUnclickedNeighIds(frontierCell.r, frontierCell.c))

                    if frontierCellUnclickedNeighIdsSet < currCellUnclickedNeighIdsSet or currCellUnclickedNeighIdsSet < frontierCellUnclickedNeighIdsSet: #check subset
                        difference = currCellUnclickedNeighIdsSet ^ frontierCellUnclickedNeighIdsSet # ^ is symmetric difference
                        diffMines = abs(frontierCell.numRemainingBorderMines - currCell.numRemainingBorderMines)
                        if diffMines == 0: # the difference cell(s) cannot be a mine.
                            for nodeId in difference:
                                clickCellIdSet.add(nodeId)
                        else:
                            if len(difference) == diffMines: # the difference cell(s) must be a mine.
                                for nodeId in difference:
                                    self.handleSetMine(nodeId, mineCellIds)
                
                unclickedNeighIds = self.getUnclickedNeighIds(cell.r, cell.c) #conservative update in case board was updated
            

            # All neighbors MUST be mines
            if cell.numRemainingBorderMines == len(unclickedNeighIds):
                for nodeId in unclickedNeighIds:
                    self.handleSetMine(nodeId, mineCellIds)

            # Neighbors CANNOT be mines. CLICK them.
            unclickedNeighIds = self.getUnclickedNeighIds(cell.r, cell.c) # b/c may have found some mines
            if cell.numRemainingBorderMines == 0:
                for neigh in unclickedNeighIds:
                    clickCellIdSet.add(neigh)
                # remove from frontier (by not appending).
            else:
                self.frontier.append(cell)

        for cellId in clickCellIdSet:
            clickCellIds.append(cellId)

        self.progressPrevTick = len(clickCellIds) > 0 or len(mineCellIds) > 0
        return clickCellIds


    def printBoard(self):
        for r in range(self.numRows):
            for c in range(self.numCols):
                cell = self.board[r][c]
                if cell.data == CellState.MINE:
                    print("X", end=" ")
                elif cell.data == CellState.UNCLICKED:
                    print("u", end=" ")
                else:
                    print(cell.data.value, end=" ")
            print()
        print()

    def reset_game(): # Clicks on the smiley face to reset the game.
        click(729, 252)