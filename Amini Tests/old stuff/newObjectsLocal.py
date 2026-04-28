from __future__ import print_function
import cv2
import numpy as np
import argparse
import time

# NOTE: All comments with "##" is code for resizing the camera.

# Colours
red = (0, 0, 255)
green = (0, 255, 0)
white = (255, 255, 255)
blue = (255, 0, 0)
black = (0, 0, 0)

# Camera (incl. its width and height) initialisation
capture = cv2.VideoCapture(0)

width = int(capture.get(3))
height = int(capture.get(4))
blurSize = 3

# The added margin for the object view
margin = 35

# How quickly the position and size of the object updates (0 < speed =< 1)
speed_position = 0.99
speed_size = 0.3

# region FG Mask Initialisation
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

# Camera Properties; resized dimensions, horizon, center of horizon 
resizeFactor = 2 # Camera resolution is divided by this number
##width = int(width / resizeFactor); height = int(height / resizeFactor)
##resizedDimensions = (width, height)
horizon = int(height * 0.4)
centerFloor = [int(width / 2), int(horizon * 1.5)]

# Captures first background image
ret_bg, background = capture.read()
background = cv2.flip(background, 1)

# Blurs + resizes background image
##background = cv2.resize(background, resizedDimensions, interpolation=cv2.INTER_LINEAR)
background_blurred = cv2.GaussianBlur(background, (5, 5), 5) 

# Threshold for new colours (increase for less sensitivity)
thresholdValue = 10

# Timer stuff
start_time_bg = time.time()
interval_bg = 0.1 # how often the background image is updated (in seconds)
interval_obj_id = 2 # how long an object should be in frame before it is IDed as The Object
found_an_object = False # becomes true when an object has first been detected (prevents errors)
object_identified = False # becomes true once The Object has been identified
center_object_initialised = False

# Maybe I should only run the code block with the "found_an_object = True" once.
# So that once the object is found, then the object's center coordinates become the black dot on the screen.
# And The Object is considered to be the object nearest to the center of the screen
# So findObject() is only run once, when found_an_object is still equal to False

# Maybe it should wait until the object has been "still" for 3 seconds before it is locked in as The Object.
# Or it could even just 
# And then bcs "determinedObject" is True, it no longer runs the "looking for object" code?

while True:
    current_time = time.time()

    # Updates the background image once "interval" time has passed
    if start_time_bg + interval_bg < current_time:
        start_time_bg = time.time()
        ret_bg, background = capture.read()
        background = cv2.flip(background, 1)
        ##background = cv2.resize(background, resizedDimensions, interpolation=cv2.INTER_LINEAR)
        background_blurred = cv2.GaussianBlur(background, (blurSize, blurSize), blurSize)

    # Captures current camera view, resizes and blurs it
    ret, frame = capture.read()
    frame = cv2.flip(frame, 1)
    ret, obj_cropped_img = capture.read()
    obj_cropped_img = cv2.flip(obj_cropped_img, 1)
    ##frame = cv2.resize(frame, resizedDimensions, interpolation=cv2.INTER_LINEAR)
    frame_blurred = cv2.GaussianBlur(frame, (blurSize, blurSize), blurSize) 
    
    # Compares colour difference between background and current view, then apply greyscale and binary values (based on thresholdValue)
    difference = cv2.absdiff(background_blurred, frame_blurred)
    difference_greyscale = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)
    
    _, mask = cv2.threshold(difference_greyscale, thresholdValue, 255, cv2.THRESH_BINARY)
    
    cv2.imshow("diff mask yes", mask)

    # Repeated erosion and dilation to remove noise and thin foreground elements in mask
    mask = cv2.erode(mask, np.ones((3,3), np.uint8), iterations = 5)
    mask = cv2.dilate(mask, np.ones((7,7), np.uint8), iterations = 5)
    mask = cv2.erode(mask, np.ones((3,3), np.uint8), iterations = 5)
    mask = cv2.dilate(mask, np.ones((9,9), np.uint8), iterations = 7)
    
    cv2.imshow("diff mask post erosion", mask)

    # Find contours from the resultant mask
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # TODO: Use diff mask post erosion instead of FG to track the robot
    # Only switch to FG if there are no contous in diff mask post erosion

    # Count the number of contours
    color_area_num = len(contours)
    
    # Initialises default distance from object to centre of horizon
    lowestDis = 1000

    # region Identifying Object
    # For each contour if the center is below the horizon, draw a white rectangle around it
    if color_area_num > 0 and object_identified == False: 
        for i in contours:
            # x, y are the top left coords, w, h are the width and height (of the contour)
            x, y, w, h = cv2.boundingRect(i)

            # Center pixels of the contour
            centerX = x + int((w / 2))
            centerY = y + int((h / 2))

            # If the contour's vertical center is on the floor (below the horizon) and is bigger than 8x8...
            if centerY > horizon + 20 and w >= 8 and h >= 8:
                # Draw green outlines around it
                cv2.drawContours(frame, i, -1, green, 1)

                # Calculate its distance to the center of the floor
                centerDis = (abs(centerFloor[0] - centerX) + abs(centerFloor[1] - centerY))

                # Find the contour with the centre-most dimensions, and save them into the global variables
                if (centerDis < lowestDis):
                    lowestDis = centerDis
                    # The coordinates of the "object" are saved into this variable
                    global xO; global yO; global wO; global hO
                    xO = x; yO = y; wO = w; hO = h
                    if found_an_object == False:
                        global start_time_obj_id
                        start_time_obj_id = time.time()
                    found_an_object = True # An object has been found, so this is now True

                    # Draw a white rectangular frame around it
                    cv2.rectangle(frame, (x, y), (x + w, y + h), white, 1) 
                    
                    # Distance = distance from lowest point to bottom of screen
                    dis = str(int(height - y + h))
                    distance = ("Distance:" + dis)
                    wS = str(w)
                    hS = str(w)
                    size = str("Width:" + wS + "Height:" + hS)
                    
                    # Add distance + size next to object
                    cv2.putText(frame, distance, (x, y), cv2.FONT_HERSHEY_SIMPLEX, .5, red, 2)
                    cv2.putText(frame, size, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, .5, red, 2)

                    # Draw small white circle on the center of object
                    cv2.circle(frame, (centerX, centerY), 5, white, -1) 
    # endregion

    # Look through fg mask2 for an object
    fg = backSub.apply(frame_blurred)
    
    # Applies threshold to get binary values of difference (based on thresholdValue)
    _, maskFG = cv2.threshold(fg, thresholdValue, 255, cv2.THRESH_BINARY)

    # Repeated erosion and dilation to remove noise and thin foreground elements in mask
    maskFG = cv2.erode(maskFG, np.ones((3,3), np.uint8), iterations = 5)
    maskFG = cv2.dilate(maskFG, np.ones((7,7), np.uint8), iterations = 5)
    maskFG = cv2.erode(maskFG, np.ones((3,3), np.uint8), iterations = 4)
    maskFG = cv2.dilate(maskFG, np.ones((4,4), np.uint8), iterations = 5)

    # region Keeping Track of Object
    # If an object has been identified as The Object
    if found_an_object == True:      
        # Create a frame of current The Object view
                                                # y1:y2                                 # x1:x2
        cv2.rectangle(obj_cropped_img, (0, 0), (max(0, xO - margin), height), black, -1) # left
        cv2.rectangle(obj_cropped_img, (xO + wO + margin, 0), (width, height), black, -1) # right
        cv2.rectangle(obj_cropped_img, (0, 0), (width, yO - margin), black, -1) # top
        cv2.rectangle(obj_cropped_img, (0, yO + hO + margin), (width, height), black, -1) # bottom
        #frame[max(0, yO - margin) : yO + hO + margin, max(0, xO - margin) : xO + wO + margin]
        
        gray = cv2.cvtColor(obj_cropped_img, cv2.COLOR_BGR2GRAY)          # Turn grayscale
        blur = cv2.GaussianBlur(gray, (5, 5), 1.4)              # Removing noise -- increasing the last number increases blur
        edges = cv2.Canny(blur, threshold1=10, threshold2=200) # Apply Canny Edge Detector -- default is 100-200

        # Draw rectangles so that only the fg view around the object is visible
        # Removes other distracting objects

        cv2.rectangle(edges, (0, 0), (max(0, xO - margin), height), black, -1) # left
        cv2.rectangle(edges, (xO + wO + margin, 0), (width, height), black, -1) # right
        cv2.rectangle(edges, (0, 0), (width, yO - margin), black, -1) # top
        cv2.rectangle(edges, (0, yO + hO + margin), (width, height), black, -1) # bottom
        cv2.imshow("edges", edges)

        # Show a cropped view of the object
        cv2.imshow("object view", obj_cropped_img)

        # Draw rectangles so that only the fg view around the object is visible
        # Removes other distracting objects
        cv2.rectangle(maskFG, (0, 0), (max(0, xO - margin), height), black, -1) # left
        cv2.rectangle(maskFG, (xO + wO + margin, 0), (width, height), black, -1) # right
        cv2.rectangle(maskFG, (0, 0), (width, horizon), black, -1) # top
        cv2.rectangle(maskFG, (0, yO + hO + margin), (width, height), black, -1) # bottom

        # Removes other distracting objects
        cv2.rectangle(maskFG, (0, 0), (max(0, xO - margin), height), black, -1) # left
        cv2.rectangle(maskFG, (xO + wO + margin, 0), (width, height), black, -1) # right
        cv2.rectangle(maskFG, (0, 0), (width, horizon), black, -1) # top
        cv2.rectangle(maskFG, (0, yO + hO + margin), (width, height), black, -1) # bottom

        # Removes other distracting objects from difference
        cv2.rectangle(difference, (0, 0), (max(0, xO - margin), height), black, -1) # left
        cv2.rectangle(difference, (xO + wO + margin, 0), (width, height), black, -1) # right
        cv2.rectangle(difference, (0, 0), (width, horizon), black, -1) # top
        cv2.rectangle(difference, (0, yO + hO + margin), (width, height), black, -1) # bottom
        difference_greyscale = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)
    
        _, obj_diff_mask = cv2.threshold(difference_greyscale, thresholdValue, 255, cv2.THRESH_BINARY)
        cv2.imshow("obj_diff_mask", obj_diff_mask)

        # TODO: If there is nothing in the fg, only then use the edge??
        # Only check the object window fore new objects!!! not everything!!!
        contoursFG, hierarchy = cv2.findContours(obj_diff_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if len(contoursFG) == 0:
            contoursFG, hierarchy = cv2.findContours(maskFG, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        color_area_num_fg = len(contoursFG)

        # Draw green outlines around contours
        cv2.drawContours(frame, contoursFG, -1, green, 1)
        
        if color_area_num_fg > 0: 
            for i in contoursFG: # Traverse all contours
                # x, y are the top left coords of the contour, w, h are the width and height
                x, y, w, h = cv2.boundingRect(i)
                
                # Center coordinates of the contour
                centerX = x + int((w / 2))
                centerY = y + int((h / 2))

                if centerY > horizon + 20 and center_object_initialised == True:
                    global center_object_x; global center_object_y
                    centerDis = (abs(center_object_x - centerX) + abs(center_object_y - centerY))
                    # The object nearest to the last known location of the object _is_ the Object
                    if (centerDis < lowestDis):
                        lowestDis = centerDis
                        # The coordinates of the "object" are saved into this variable
                        # Have them gradually move instead of instantly being equal.
                        # Hopefully prevents wrong object errors

                        # if the distance from xO to yO is bigger than like 100, it should not do it.
                        xO = int(xO + (x - xO) * speed_position)
                        yO = int(yO + (y - yO) * speed_position)
                        wO = int(wO + (w - wO) * speed_size)
                        hO = int(hO + (h - hO) * speed_size)

                    # If contour is bigger than 8x8
                    if w >= 8 and h >= 8:
                        # Draw a thin white rectangular frame around it
                        cv2.rectangle(frame, (x, y), (x + w, y + h), white, 1) 

                        # Distance = distance from lowest point to bottom of screen
                        dis = str(int(height - y + h))
                        distance = ("Distance:" + dis)
                        wS = str(w)
                        hS = str(w)
                        size = str("Width:" + wS + "Height:" + hS)
                        
                        # Add distance next to object
                        cv2.putText(frame, distance, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, red, 1)
                        cv2.putText(frame, size, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, .25, red, 1)

                        centerX = x + int((w / 2))
                        centerY = y + int((h / 2))

    # Places circle on the center floor area
    cv2.circle(frame, (centerFloor[0], centerFloor[1]), 2, (0, 0, 0), -1) 

    # Maintains a rectangle around the last known position of object
    if found_an_object == True:
        cv2.rectangle(frame, (xO, yO), (xO + wO, yO + hO), white, 2) 
        cropped_img = frame[yO:yO + hO, xO:xO + wO]
        #cv2.imshow("cropped_img", cropped_img)
        # Circles center of object
        cv2.circle(frame, (int(xO + wO / 2), int(yO + hO / 2)), 15, blue, -1)
        if start_time_obj_id + interval_obj_id < current_time:
            center_object_x = int(xO + wO / 2)
            center_object_y = int(yO + hO / 2)
            center_object_initialised = True
            cv2.circle(frame, (center_object_x, center_object_y), 60, red, 1)
            print("Perma Object Found!!!")
            object_identified = True   

    # Draws black rectangle on the non-floor section of fg (so only objects on the floor are detected)
    cv2.rectangle(maskFG, (0, 0), (width, horizon - 20), black, -1) 
    cv2.imshow('FG', maskFG)

    # Places line at the horizon (for our reference)
    cv2.line(frame, (0, horizon), (width, horizon), blue, 2)
    
    # Current view
    cv2.imshow("video", frame)
    
    # Difference between background image and current view
    cv2.imshow('difference', difference)

    # Difference between background image and current view (greyscale)
    #cv2.imshow('difference_greyscale', difference_greyscale)

    # Binary B&W output of difference
    #cv2.imshow('mask', mask)

    # Mask which allows us to see only new objects
    masked = cv2.bitwise_and(frame_blurred, frame_blurred, mask=maskFG)
    cv2.imshow("masked", masked)

    keyboard = cv2.waitKey(30)
    if keyboard == 'q' or keyboard == 27:
        break