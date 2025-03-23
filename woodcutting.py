import time
import cv2
import numpy as np
import pyautogui

# Load tree and log templates
tree_template = cv2.imread("tree.png", 0)  # You need an image of a tree from the game
log_template = cv2.imread("log.png", 0)    # You need an image of logs in inventory

def capture_screen():
    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    return frame

def find_object(template, threshold=0.8):
    screen = capture_screen()
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)
    points = list(zip(*loc[::-1]))
    return points

def move_mouse_to_tree():
    trees = find_object(tree_template)
    if trees:
        x, y = trees[0]
        pyautogui.moveTo(x + 10, y + 10, duration=0.5)  # Smooth mouse movement
        print("Tree found! Move mouse to tree.")
    else:
        print("No trees found. Adjust position.")

def check_inventory_full():
    logs = find_object(log_template)
    if len(logs) >= 28:  # Assuming full inventory has 28 slots
        print("Inventory full! Bank or drop logs.")
        return True
    return False

if __name__ == "__main__":
    while True:
        move_mouse_to_tree()
        time.sleep(2)  # Wait before next check
        if check_inventory_full():
            break
