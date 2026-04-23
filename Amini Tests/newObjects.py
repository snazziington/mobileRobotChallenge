from __future__ import print_function
import cv2
import numpy as np
import argparse

# Just messing with "new" object detection.
# When program starts, it saves a snapshot of the environment. New objects will show up on the "difference" window
# Could expanded on to have every new object outlined, and calculate likeliness that each new object is _the_ object
# Then aim to follow that specific object via edge-detection maybe

# region Uncomment this if you want to see the "fgMask" wayy below
"""parser = argparse.ArgumentParser(description='This program shows how to use background subtraction methods provided by \
                                              Opencv2. You can process both videos and images.')
parser.add_argument('--input', type=str, help='Path to a video or a sequence of image.', default='vtest.avi')
parser.add_argument('--algo', type=str, help='Background subtraction method (KNN, MOG2).', default='MOG2')
args = parser.parse_args()  

if args.algo == 'MOG2':
    backSub = cv2.createBackgroundSubtractorMOG2()
else:
    backSub = cv2.createBackgroundSubtractorKNN()
"""
# endregion
capture = cv2.VideoCapture(1)
width = capture.get(3)
height = capture.get(4)

# Determines size of image (so it's easily changeable)
# resizeFactor = 4 # Camera resolution is divided by this number
# resizedDimensions = (int(width / resizeFactor), int(height / resizeFactor))
# width /= resizeFactor, height /= resizeFactor

# Captures background image that will be compared to camera footage
    # For final, it should be a longer exposure to make up for little things moving in background/lighting etc.
    # If possible, also increase/decrease exposure and save those snapshots as background too
ret_bg, background = capture.read()

# Blurs the background image
# background = cv2.resize(background, resizedDimensions, interpolation=cv2.INTER_LINEAR)
background_blurred = cv2.GaussianBlur(background, (5, 5), 5) 

# If the new object is similar in colour, it will not be detected.

# Threshold for new colours (increase for less sensitivity)
thresholdValue = 70
 
while True:
    # Captures current camera view and blurs it
    ret, frame = capture.read()

    #frame = cv2.resize(frame, resizedDimensions, interpolation=cv2.INTER_LINEAR)
    
    # Blurs current frame
    frame_blurred = cv2.GaussianBlur(frame, (5, 5), 5) 
    
    # Compares colour difference between blurred background and blurred current view
    difference = cv2.absdiff(background_blurred, frame_blurred)

    # Makes the difference greyscale
    difference_greyscale = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)

    # Applies threshold to get binary values of difference (based on thresholdValue)
    _, thresh = cv2.threshold(difference_greyscale, thresholdValue, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Draw green outlines around contours
    cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)
    
    # Counts the number of contours
    color_area_num = len(contours) 
    
    # For each contour, draw an outline and a rect outline
    if color_area_num > 0: 
        for i in contours: # Traverse all contours
            # x, y are the top left coords of the contour, w, h are the width and height
            x, y, w, h = cv2.boundingRect(i)

            # If contour is bigger than 8x8
            if w >= 8 and h >= 8:
                # Draw a white rectangular frame around it
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2) 
                
                # Distance = distance from lowest point to bottom of screen
                dis = str(int(height - y + h))
                distance = ("Distance:" + dis)

                # Add distance next to object
                cv2.putText(frame, distance, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Current view
    cv2.imshow("video", frame)
    
    # Difference between background image and current view
    cv2.imshow('difference', difference)

    # Binary B&W output of difference
    cv2.imshow('thresh', thresh)

    # Mask which allows us to see only new objects
    masked = cv2.bitwise_and(frame_blurred, frame_blurred, mask=thresh)
    cv2.imshow("masked", masked)

    keyboard = cv2.waitKey(30)
    if keyboard == 'q' or keyboard == 27:
        break