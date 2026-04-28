from __future__ import print_function
import cv2
import numpy as np
import argparse
import time

# NOTE: All comments with "##" is for resizing the camera.
    # If you do want the camera to be resized, uncomment all that code

# TODO
    # Maybe it should wait until the object has been "still" for 3 seconds before it is locked in as The Object.

# Colours
red = (0, 0, 255)
green = (0, 255, 0)
white = (255, 255, 255)
blue = (255, 0, 0)
black = (0, 0, 0)

# Camera (incl. its width and height) initialisation
capture = cv2.VideoCapture(1)

width = int(capture.get(3))
height = int(capture.get(4))
blurSize = 5

# The added margin for the object view
margin = 35

# How quickly the position and size of the object updates (0 < speed =< 1)
speed_position = 0.99
speed_size = 0.3

# region Foreground (FG) Mask Initialisation (detects movement)
parser = argparse.ArgumentParser(description='This program shows how to use background subtraction methods provided by \
                                              Opencv2. You can process both videos and images.')
parser.add_argument('--input', type=str, help='Path to a video or a sequence of image.', default='vtest.avi')
parser.add_argument('--algo', type=str, help='Background subtraction method (KNN, MOG2).', default='MOG2')
args = parser.parse_args()

if args.algo == 'MOG2':
    backSub = cv2.createBackgroundSubtractorMOG2()
else:
    backSub = cv2.createBackgroundSubtractorKNN()
# endregion

# Camera Properties; resized dimensions, horizon, center of floor 
resizeFactor = 2 # Camera resolution is divided by this number
##width = int(width / resizeFactor); height = int(height / resizeFactor)
##resizedDimensions = (width, height)
horizon = int(height * 0.4)
centerFloor = [int(width / 2), int(horizon * 1.5)]

# Threshold for difference mask (which compares previous frame to next frame (increase for less sensitivity))
thresholdValue = 10

# Timer stuff
start_time_bg = time.time()
interval_bg = 0.1 # how often the background image is updated (in seconds)
interval_wait = 2 # length of time to wait for an object to be placed
interval_obj_id = 3 # how long an object should be in frame before it is IDed as The Object
found_an_object = False # becomes true when an object has first been detected (prevents errors)
object_identified = False # becomes true once The Object has been identified
center_object_initialised = False # becomes true once the centre of The Object has been identified (prevents errors)

# Captures first background image
ret_bg, background = capture.read()
background = cv2.flip(background, 1)
# Blurs + resizes background image
##background = cv2.resize(background, resizedDimensions, interpolation=cv2.INTER_LINEAR)
background_blurred = cv2.GaussianBlur(background, (5, 5), 5) 

while True: # Runs until key is pressed to close
    current_time = time.time() # Updates the current time so the timer can be used

    cv2.imshow("background_blurred", background_blurred)

    keyboard = cv2.waitKey(30)
    if keyboard == 'q' or keyboard == 27:
        break