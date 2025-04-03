import cv2
import numpy as np
from enum import Enum
from PIL import Image
from board_dimensions import getBoardDimensions
from debug_vars import debugImgId
import ScreenManager as sm
"""
Building code to beat minesweeper at this url:
https://minesweeperonline.com/#200

Put the game on your laptop screen

With mouse, top-left corner of the game board should be at (x, y) = (0, 0)
"""
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

# pyautogui.displayMousePosition() # Run this to get the current mouse position as mouse moves


def main():
    boardVars = getBoardDimensions()
    # boardVars = getDebugBoardDimensions()
    cellSize = boardVars.getCellSize()
    topLeftScreenCoords = boardVars.getTopLeft()
    bottomRightScreenCoords = boardVars.getBotRight()
    screenManager = sm.ScreenManager(cellSize, topLeftScreenCoords, bottomRightScreenCoords)





    exit()
    screenManager.clickCell(8, 15) #8,15 in middle


    fullScreenshot = screenManager.fullScreenshot()

    fullScreenshot_cv2 = cv2.cvtColor(np.array(fullScreenshot), cv2.COLOR_RGB2BGR) # Convert to OpenCV format (rgb -> bgr)
    fullScreenshot_gray = cv2.cvtColor(fullScreenshot_cv2, cv2.COLOR_BGR2GRAY)

    colors = [(0,0,0), (255, 0, 0), (0,255,0), (0, 0, 255), (130,0,75), (42,42,165)] #bgr 
    w = h = 39
    for i in range(0, 6):
        template = cv2.imread(f'templates/{i}.png')
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        # template = cv2.resize(template, (cellSize[0], cellSize[1])) #TODO resize needed for other resolutions? I think we're using 39x39 though

        res = cv2.matchTemplate(fullScreenshot_gray,template,cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where( res >= threshold)
        for pt in zip(*loc[::-1]):
            cv2.rectangle(fullScreenshot_cv2, pt, (pt[0] + w, pt[1] + h), colors[i], 2)
    
    template = cv2.imread(f'templates/unclicked.png')
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(fullScreenshot_gray,template,cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where( res >= threshold)
    for pt in zip(*loc[::-1]):
        cv2.rectangle(fullScreenshot_cv2, pt, (pt[0] + w, pt[1] + h), (255,255,255), 2)




    cv2.imwrite('template_debug.png', fullScreenshot_cv2)

    print(fullScreenshot_cv2.shape) #fullScreenshot_np.shape: (640, 1200, 3)
    # screenManager.getCellPixels(fullScreenshot_cv2, 1, 1) #blank





    # gameGrid = [[CellState.UNCLICKED.value for _ in range(30)] for _ in range(16)]
    
    """
    Create a grid
    Recognize the difference between: 1-8, unclicked, searched
    """
    exit()




if __name__ == '__main__':
    main()


