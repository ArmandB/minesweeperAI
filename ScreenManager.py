import pyautogui

#TODO ensure r,c is valid?
class ScreenManager:
    def __init__(self, cellSize, BBTopLeft, BBBottomRight):
        self.cellSize = cellSize
        self.BBTopLeft = BBTopLeft
        self.BBBottomRight = BBBottomRight
        screenWidth, screenHeight = pyautogui.size()
        MAX_X, MAX_Y = screenWidth, screenHeight
        self.MAX_X = MAX_X
        self.MAX_Y = MAX_Y      


        self.numXCells = (BBBottomRight[0]-BBTopLeft[0])/cellSize[0]
        self.numYCells = (BBBottomRight[1]-BBTopLeft[1])/cellSize[1]
        print("numXCells: ", self.numXCells)
        print("numYCells: ", self.numYCells)
        print("maxX, maxY: ", MAX_X, MAX_Y)

    def calcPosHelper(self, r, c):
        x = self.BBTopLeft[0] + c*self.cellSize[0] + self.cellSize[0]//2
        y = self.BBTopLeft[1] + r*self.cellSize[1] + self.cellSize[1]//2
        return x,y

    def clickCell(self, r, c):
        x, y = self.calcPosHelper(r, c)
        pyautogui.click(x,y)
    
    def mouseOverCell(self, r, c):
        x, y = self.calcPosHelper(r, c)
        pyautogui.moveTo(x, y)
    
    def getCellPixels(self, screenshot_np, r, c):
        x1 = self.BBTopLeft[0]+1 + c*self.cellSize[0]
        x2 = self.BBTopLeft[0]+1 + (c+1)*self.cellSize[0]
        y1 = self.BBTopLeft[1]+1 + r*self.cellSize[1]
        y2 = self.BBTopLeft[1]+1 + (r+1)*self.cellSize[1]

        print("[%d:%d, %d:%d]" % (y1, y2, x1, x2))

        cellImage = screenshot_np[y1:y2, x1:x2, :]
        cv2.imwrite(f'cell_{r}_{c}.png', cellImage)
        cellImageGray = cv2.cvtColor(cellImage, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'cell_{r}_{c}_grayscale.png', cellImageGray)
        return cellImage

    def fullScreenshot(self):
        return pyautogui.screenshot(region=(0,0, self.MAX_X, self.MAX_Y))

    def boardScreenshot(self):
        return pyautogui.screenshot(region=(self.BBTopLeft[0], self.BBTopLeft[1], self.BBBottomRight[0], self.BBBottomRight[1]))
