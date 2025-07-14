import pyautogui
import cv2
import numpy as np
import os
import shutil
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
        print("maxX, maxY: ", MAX_X, MAX_Y)

        self.templateDict = {
            'unclicked' : cv2.imread(f'templates/unclicked.png'),
            0 : cv2.imread(f'templates/0.png'),
            1 : cv2.imread(f'templates/1.png'),
            2 : cv2.imread(f'templates/2.png'),
            3 : cv2.imread(f'templates/3.png'),
            4 : cv2.imread(f'templates/4.png'),
            5 : cv2.imread(f'templates/5.png'),
            6 : cv2.imread(f'templates/6.png'),
            7 : cv2.imread(f'templates/7.png'),
            8 : cv2.imread(f'templates/8.png'),
        }
        for key in self.templateDict.keys():
            self.templateDict[key] = cv2.cvtColor(self.templateDict[key], cv2.COLOR_BGR2GRAY)

        self.debugColorDict = { #bgr. colors to put squares around the numbers
            'unclicked' : (255,255,255),
            0 : (255, 0, 255),
            1 : (255, 0, 0),
            2 : (0,255,0),
            3 : (0, 0, 255),
            4 : (204,0,102),
            5 : (34, 114, 195),
            6 : (153, 153, 0),
            7 : (0,0,0),
            8 : (192,192,192),
        }

        debug_moves_dir = os.path.join(os.getcwd(),'debug_moves') 
        if os.path.exists(debug_moves_dir):
            shutil.rmtree(debug_moves_dir)
        os.makedirs(debug_moves_dir)
        self.debugMoves = 0

    def setGameManager(self, gameManager):
        self.gameManager = gameManager

    def calcPosHelper(self, r, c):
        x = self.BBTopLeft[0] + c*self.cellSize[0] + self.cellSize[0]//2
        y = self.BBTopLeft[1] + r*self.cellSize[1] + self.cellSize[1]//2
        return x,y

    def clickCell(self, r, c):
        x, y = self.calcPosHelper(r, c)
        pyautogui.click(x,y)

    def rightClickCell(self, r, c):
        x, y = self.calcPosHelper(r, c)
        pyautogui.click(x,y, button='right')

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

    def getCellFromPixelCoords(self, px_x, px_y):
        # pyautogui.moveTo(px_x, px_y)
        px_x -= self.BBTopLeft[0]
        px_y -= self.BBTopLeft[1]
        r = px_y // self.cellSize[1]
        c = px_x // self.cellSize[0]
        # print("bbtopleft: ",self.BBTopLeft)
        # print("cell: (%d, %d)" % (r, c))
        return (r, c)


    def fullScreenshot(self):
        img = pyautogui.screenshot(region=(0,0, self.MAX_X, self.MAX_Y))
        img_cv2 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR) # Convert to OpenCV format (rgb -> bgr)
        return img_cv2

    def boardScreenshot(self):
        return pyautogui.screenshot(region=(self.BBTopLeft[0], self.BBTopLeft[1], self.BBBottomRight[0], self.BBBottomRight[1]))

    # TODO For debugging save the screenshot to a file!
    def interpretScreenshot(self, img):
        
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        w = h = self.cellSize[0]
        print(self.templateDict.keys())

        for key,templateImg in self.templateDict.items():
            # template = cv2.resize(template, (cellSize[0], cellSize[1])) #TODO resize needed for other resolutions? I think we're using 39x39 though
            res = cv2.matchTemplate(img_gray, templateImg, cv2.TM_CCOEFF_NORMED)
            threshold = 0.9
            loc = np.where( res >= threshold)
            # print("{} - loc size: {}".format(key, loc[0].shape))

            for pt in zip(*loc[::-1]):
                cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), self.debugColorDict[key], 2)

            # update the game board with the cell value
            if key == 'unclicked':
                continue
            if loc[0].shape == (0,): #empty index array
                continue
            #This function is called multiple times for each cell (b/c overlapping matches)
            for pt in zip(*loc[::-1]):
                # match is top left corner of the template. want middle of the cell to avoid one-off errors
                r,c = self.getCellFromPixelCoords(pt[0]+w//2, pt[1]+h//2)
                self.gameManager.setCellValue(key, r, c)





        cv2.imwrite('debug_moves/ss_move_{:04}.png'.format(self.debugMoves), img)
        self.debugMoves += 1

        pass