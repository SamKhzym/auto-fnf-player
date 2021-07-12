import time, cv2, mss
from pynput.keyboard import Key, Controller
import numpy as np

keyboard = Controller()

GRAY_LOW = np.array([80, 50, 20])
GRAY_HIGH = np.array([100, 100, 255])

PURPLE_LOW = np.array([147, 138, 149])
PURPLE_HIGH = np.array([168, 188, 255])

BLUE_LOW = np.array([74, 225, 200])
BLUE_HIGH = np.array([103, 255, 255])

GREEN_LOW = np.array([23, 213, 211])
GREEN_HIGH = np.array([62, 255, 255])

RED_LOW = np.array([160, 177, 220])
RED_HIGH = np.array([180, 216, 255])

class AutoPlayer:

    arrows = []

    def __init__(self):
        self.arrows = get_arrows()

    def play_game(self):

        width = 1600
        height = 900
        
        monitor = {"top": 0, "left": 0, "width": width, "height": height}

        with mss.mss() as sct:
            
            while True:
                img = np.array(sct.grab(monitor))

                for arrow in self.arrows:
                    if arrow.check_for_color(img):
                        print(arrow.key)
                        arrow.press_key()

class Arrow:

    box = [0,0,0,0]
    order = -1
    key = ""
    color_low = [0,0,0]
    color_high = [180,255,255]
    area_pixels = 0

    def __init__(self, box, order, key, color_low, color_high):
        self.box = box
        self.order = order
        self.key = key
        self.color_low = color_low
        self.color_high = color_high
        self.area_pixels = (self.box[1]-self.box[0]) * (self.box[3]-self.box[2])

    def __repr__(self):
        return str([self.box, self.order, self.key])

    def get_roi(self, img):
        return img[self.box[0]:self.box[1],self.box[2]:self.box[3]]

    def press_key(self):

        PRESS_TIME = 0.03
        
        keyboard.press(self.key)
        time.sleep(PRESS_TIME)
        keyboard.release(self.key)

    def check_for_color(self, img):

        PIXEL_PERCENT_THRESHOLD = 0.15
        
        roi = self.get_roi(img)

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.color_low, self.color_high)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        color_pixels = 0
        for contour in contours: color_pixels += len(contours)

        if color_pixels/self.area_pixels > PIXEL_PERCENT_THRESHOLD: return True
        else: return False

def take_screenshot():
    width = 1600
    height = 900
    
    monitor = {"top": 0, "left": 0, "width": width, "height": height}
    
    with mss.mss() as sct:
        img = np.array(sct.grab(monitor))
        return img

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

def remove_nonsquare_boxes(boxes):
    new_boxes = []

    for box in boxes:
        width = box[3] - box[2]
        height = box[1] - box[0]

        if abs(height-width)/height < 0.1:
            new_boxes.append(box)

    return new_boxes
        
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

        boxes = remove_nonsquare_boxes(boxes)
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
                        
        try:
            final_arrows = []
            final_arrows.append(Arrow(arrows[-4], 1, "a", PURPLE_LOW, PURPLE_HIGH))
            final_arrows.append(Arrow(arrows[-3], 2, "s", BLUE_LOW, BLUE_HIGH))
            final_arrows.append(Arrow(arrows[-2], 3, "w", GREEN_LOW, GREEN_HIGH))
            final_arrows.append(Arrow(arrows[-1], 4, "d", RED_LOW, RED_HIGH))

            return final_arrows
        
        except IndexError:
            print("Can't find enough arrows! :(")

def main():
    play = AutoPlayer()
    play.play_game()

if __name__ == "__main__":
    main()
