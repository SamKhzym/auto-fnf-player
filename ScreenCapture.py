import time, cv2, mss
from pynput.keyboard import Key, Controller
import numpy as np

keyboard = Controller()

left = [886, 252]
down = [1005, 252]
up = [1120, 252]
right = [1239, 252]
GRAY = [173, 163, 135, 255]

GRAY_LOW = np.array([80, 50, 20])
GRAY_HIGH = np.array([100, 100, 255])

state = [False, False, False, False]

class Arrow:

    box = [0,0,0,0]
    order = -1
    key = ""

    def __init__(self, box, order, key):
        self.box = box
        self.order = order
        self.key = key

    def __repr__(self):
        return str([self.box, self.order, self.key])

    def get_roi(self, img):
        return img[self.box[0]:self.box[1],self.box[2]:self.box[3]]

    #def get_color(self, img):
        #img[self.]

def press_release(key):

    PRESS_TIME = 0.03
    
    keyboard.press(key)
    time.sleep(PRESS_TIME)
    keyboard.release(key)

def filter_contours(img):
    
    MIN_SIZE = 30
    filtered = []

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, GRAY_LOW, GRAY_HIGH)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        if len(contour) > MIN_SIZE: filtered.append(contour)

    return filtered

def get_contour_square(contour):

    x_vals = []
    y_vals = []

    for i in range(len(contour)):
        x_vals.append(contour[i][0][0])
        y_vals.append(contour[i][0][1])

    return [min(y_vals), max(y_vals), min(x_vals), max(x_vals)]
        
def get_arrows():
    
    width = 1600
    height = 900
    
    monitor = {"top": 0, "left": 0, "width": width, "height": height}
    
    with mss.mss() as sct:
        img = np.array(sct.grab(monitor))
        contours = filter_contours(img)

        print(len(contours))

        boxes = []
        for contour in contours:
            boxes.append(get_contour_square(contour))

        print(boxes)

        arrows = []
        for i in range(len(boxes)):
            
            if len(arrows) == 0:
                arrows.append(boxes[i])
                continue

            else:
                for j in range(len(arrows)):
                    if j == 0 and boxes[i][2] < arrows[j][2]:
                        arrows.insert(0, boxes[i])
                    elif j == len(arrows)-1 and boxes[i][2] > arrows[j][2]:
                        arrows.insert(j+1, boxes[i])
                    elif boxes[i][2] > arrows[j-1][2] and boxes[i][2] < arrows[j][2]:
                        arrows.insert(j, boxes[i])

        final_arrows = []
        final_arrows.append(Arrow(arrows[-4], 1, "a"))
        final_arrows.append(Arrow(arrows[-3], 2, "s"))
        final_arrows.append(Arrow(arrows[-2], 3, "w"))
        final_arrows.append(Arrow(arrows[-1], 4, "d"))

        return final_arrows

# Display the picture
#cv2.imshow("OpenCV/Numpy normal", img)

#print("fps: {}".format(1 / (time.time() - last_time)))

"""if list(img[left[1]][left[0]]) != GRAY:
    print("LEFT NOTE")
    press_release("a")
    state[0] = True
else:
    state[0] = False
    
if list(img[down[1]][down[0]]) != GRAY:
    print("DOWN NOTE")
    press_release("s")
    state[1] = True
else:
    state[1] = False
    
if list(img[up[1]][up[0]]) != GRAY:
    print("UP NOTE")
    press_release("w")
    state[2] = True
else:
    state[2] = False
    
if list(img[right[1]][right[0]]) != GRAY:
    print("RIGHT NOTE")
    press_release("d")
    state[3] = True
else:
    state[3] = False"""

"""def color_equals(c1, c2):

    TOLERANCE = 3

    if (abs(c1[0] - c2[0]) < TOLERANCE and
        abs(c1[1] - c2[1]) < TOLERANCE and
        abs(c1[2] - c2[2]) < TOLERANCE and
        abs(c1[3] - c2[3]) < TOLERANCE):
        return True
    else:
        return False"""
