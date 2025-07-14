from shared_vars import debugImgId
import pyautogui
import cv2
import numpy as np

#TODO ensure all horizontal lines are horizontal and all vertical lines are vertical
#TODO ensure that no other windows are open (or take a screenshot of all windows to maximize the right one) and that mouse is not blocking anything. don't think mouse is an issue
class boardVars:
    def __init__(self, cellSize, BBTopLeft, BBBottomRight):
        self.cellSize = cellSize
        self.BBTopLeft = BBTopLeft
        self.BBBottomRight = BBBottomRight

        self.numXCells = (BBBottomRight[0]-BBTopLeft[0])/cellSize[0]
        self.numYCells = (BBBottomRight[1]-BBTopLeft[1])/cellSize[1]
        print("numXCells: ", self.numXCells)
        print("numYCells: ", self.numYCells)
        self.numXCells = int(self.numXCells)
        self.numYCells = int(self.numYCells)

    def getCellSize(self):
        return self.cellSize
    def getTopLeft(self):
        return self.BBTopLeft
    def getBotRight(self):
        return self.BBBottomRight
    def getShape(self):
        return (self.numYCells, self.numXCells)

def drawLines(img, lines):
    i = 0
    if lines is not None:
        for line in lines:
            # print(line)
            x1, y1, x2, y2 = line
            cv2.line(img, (x1, y1), (x2, y2), (128, 0, 128), 1)
            # if i == 2:
            #     break
            # i += 1
def drawCells(img, BBTopLeft, cellSize):
    global debugImgId
    for r in range(0, 16):
        colors = [(0,0,0), (255,255,255)]
        idx = r % 2
        for c in range(0, 30):
            cellTopLeft = (BBTopLeft[0] + c*cellSize[0], BBTopLeft[1] + r*cellSize[1])
            cellBottomRight = (BBTopLeft[0] + (c+1)*cellSize[0], BBTopLeft[1] + (r+1)*cellSize[1])
            cv2.rectangle(img, cellTopLeft, cellBottomRight, colors[idx], -1)
            idx = (idx + 1) % 2

    cv2.imwrite('{:02}_minesweeper_cells.png'.format(debugImgId), img)
    debugImgId += 1

def getCellSize(filtered_horizontal_lines, filtered_vertical_lines):
    cellSizeY = (filtered_horizontal_lines[1][1] - filtered_horizontal_lines[0][1]) #vertical lines will by X distance apart [x1 y1 x2 y2]
    cellSizeX = (filtered_vertical_lines[1][0] - filtered_vertical_lines[0][0]) #horizontal lines will by Y distance apart [x1 y1 x2 y2]
    #TODO better checking for robustness. make sure all lines are the same distance apart
    return (cellSizeX, cellSizeY)

""" Get bounding box for minesweeper cells aray"""
def getCellsBB(filtered_hlines, filtered_vlines):
    # print("horizontal")
    # print(filtered_hlines[0])
    # print(filtered_hlines[-1])
    # print("vertical")
    # print(filtered_vlines[0])
    # print(filtered_vlines[-1])

    yUpper = filtered_hlines[0][1]
    yLower = filtered_hlines[-1][1]

    xLeft = filtered_vlines[0][0]
    xRight = filtered_vlines[-1][0]
    print("y range: [{}, {}]".format(yUpper, yLower)) #640. 16 boxes
    print("x range: [{}, {}]".format(xLeft, xRight)) #1200. 30 boxes
    return (xLeft, yUpper, xRight, yLower)

def getSortedGridlines(screenshotName):
    global debugImgId
    img = cv2.imread(screenshotName)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blurred, 50, 150)
    cv2.imwrite('{:02}_edges.png'.format(debugImgId), edges)
    debugImgId += 1

    # Hough Transform (Probabilistic)
    lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=100, minLineLength=50, maxLineGap=5)

    horizontal_lines = []
    vertical_lines = []
    for line in lines:
        x1, y1, x2, y2 = line[0] #[[ 223  609 1229  609]]
        if abs(y2 - y1) < abs(x2 - x1):  # horizontal line
            horizontal_lines.append(line[0]) # [x1 y1 x2 y2]
        else:  # vertical line
            vertical_lines.append(line[0])

    horizontal_lines.sort(key=lambda line: line[1]) #sort based on y value
    vertical_lines.sort(key=lambda line: line[0]) #sort based on x value

    print(horizontal_lines[0])
    drawLines(img, horizontal_lines)
    drawLines(img, vertical_lines)
    cv2.imwrite('{:02}_lines_unfiltered.png'.format(debugImgId), img)
    debugImgId += 1
    return horizontal_lines, vertical_lines

def filterGridlines(horizontal_lines, vertical_lines):
    horizontal_lines = horizontal_lines[1:-1] #remove the top and bottom lines
    vertical_lines = vertical_lines[1:-1] #remove the left and right lines

    filtered_horizontal_lines = horizontal_lines
    filtered_vertical_lines = vertical_lines

    filtered_horizontal_lines = []
    for i in range(0,len(horizontal_lines)-1):
        x1, y1, x2, y2 = horizontal_lines[i]
        nx1, ny1, nx2, ny2 = horizontal_lines[i+1]

        if ny1 - y1 <= 10:
            continue
        
        filtered_horizontal_lines.append(horizontal_lines[i])
    filtered_horizontal_lines.append(horizontal_lines[-1])

    filtered_vertical_lines = []
    for i in range(0,len(vertical_lines)-1):
        x1, y1, x2, y2 = vertical_lines[i]
        nx1, ny1, nx2, ny2 = vertical_lines[i+1]

        if nx1 - x1 <= 10:
            continue
        
        filtered_vertical_lines.append(vertical_lines[i])
    filtered_vertical_lines.append(vertical_lines[-1])

    return filtered_horizontal_lines, filtered_vertical_lines

#TODO some of this stuff is still hardcoded
#TODO boundaries between this and screen manager are not clear. goal was to have this create the stuff to initialize screen manager.
def getBoardDimensions():
    global debugImgId
    # Capture an image that contains the game board 
    screenshotTopLeft = (334, 303)
    screenshotBottomRight = (1555, 965)
    screenshot = pyautogui.screenshot(region=(screenshotTopLeft[0], screenshotTopLeft[1], 
                screenshotBottomRight[0]-screenshotTopLeft[0], screenshotBottomRight[1]-screenshotTopLeft[1])) #region=(left, top, width, height)

    screenshotName = '{:02}_minesweeper.png'.format(debugImgId)
    debugImgId += 1
    screenshot.save(screenshotName)

    # Detect all lines in the image
    sorted_hlines, sorted_vlines = getSortedGridlines(screenshotName)

    # Filter out all lines except those for the game grid
    filtered_hlines, filtered_vlines = filterGridlines(sorted_hlines, sorted_vlines)

    # Suggest placement of game cells and draw them on the image
    cellSize = getCellSize(filtered_hlines, filtered_vlines)
    cellsBB = getCellsBB(filtered_hlines, filtered_vlines)
    BBTopLeft = (cellsBB[0], cellsBB[1])
    BBBottomRight = (cellsBB[2], cellsBB[3])
    img = cv2.imread(screenshotName)
    drawCells(img, BBTopLeft, cellSize)

    # Overlay the filtered lines on the image
    drawLines(img, filtered_hlines)
    drawLines(img, filtered_vlines)
    cv2.imwrite('{:02}_minesweeper_grid.png'.format(debugImgId), img)
    debugImgId += 1

    MAX_X, MAX_Y = pyautogui.size()
    screenshotFull = pyautogui.screenshot(region=(0,0, MAX_X, MAX_Y))
    screenshotNameFull = '{:02}_minesweeper.png'.format(debugImgId)
    debugImgId += 1
    screenshotFull.save(screenshotNameFull)
    img = cv2.imread(screenshotNameFull)

    filtered_hlines = [[line[0]+screenshotTopLeft[0], line[1]+screenshotTopLeft[1], line[2]+screenshotTopLeft[0], line[3]+screenshotTopLeft[1]] for line in filtered_hlines]
    filtered_vlines = [[line[0]+screenshotTopLeft[0], line[1]+screenshotTopLeft[1], line[2]+screenshotTopLeft[0], line[3]+screenshotTopLeft[1]] for line in filtered_vlines]
    drawLines(img, filtered_hlines)
    drawLines(img, filtered_vlines)
    cv2.imwrite('{:02}_minesweeper_grid_full.png'.format(debugImgId), img)
    debugImgId += 1

    print("topleft (screenshot): {}".format(BBTopLeft))
    print("bottomright (screenshot): {}".format(BBBottomRight))

    topLeftScreenCoords = (screenshotTopLeft[0] + BBTopLeft[0], screenshotTopLeft[1] + BBTopLeft[1])
    bottomRightScreenCoords = (screenshotTopLeft[0] + BBBottomRight[0], screenshotTopLeft[1] + BBBottomRight[1])

    print("top left screen coords: {}".format(topLeftScreenCoords))
    print("bottom right screen coords: {}".format(bottomRightScreenCoords))
    print("cell size: {}".format(cellSize)) #cell size: (40, 40)    
    return boardVars(cellSize, topLeftScreenCoords, bottomRightScreenCoords)

""" For testing. The other needs a completely empty board. This does not """
def getDebugBoardDimensions():
    # Copied from print statements when running get board dims
    topLeftScreenCoords = (345, 316)
    bottomRightScreenCoords = (1545, 956)
    cellSize = (40,40)
    return boardVars(cellSize, topLeftScreenCoords, bottomRightScreenCoords)    

# TODO can maybe use this later to make things more robust. For now, we will just hardcode the values.
# def detect_game_bounds():
#     """
#     Detects the bounds of the Minesweeper game board by locating the corners of the game window.
#     Returns the top-left and bottom-right coordinates of the game board.
#     """
#     try:
#         # Locate the game board on the screen
#         game_region = pyautogui.locateOnScreen('game_board_image.png', confidence=0.8)
#         if game_region:
#             top_left = (game_region.left, game_region.top)
#             bottom_right = (game_region.left + game_region.width, game_region.top + game_region.height)
#             return top_left, bottom_right
#         else:
#             print("Game board not found. Ensure the game is visible and the reference image is correct.")
#             return None, None
#     except Exception as e:
#         print(f"Error detecting game bounds: {e}")
#         return None, None    