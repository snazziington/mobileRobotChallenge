import picar_4wd as fc
import cv2
import numpy as np
from picamera2 import Picamera2
import argparse
import time
import math
import sys
import tty
import termios

# TODO
    # Maybe it should wait until the object has been "still" for 3 seconds before it is locked in as the object?

# TODO: Filter out contours that are too big

# ==Colours==
red = (0, 0, 255)
green = (0, 255, 0)
white = (255, 255, 255)
magenta = (255, 0, 255)
blue = (255, 0, 0)
black = (0, 0, 0)

# ==Camera (incl. its width and height) initialisation==
width = 640
height = 480
blurSize = 0
blurArea = (15, 15)
speed = 1

# ==Object Following Variables==
# size of edge margin for the object view
margin = 400 # bigger means code can find object if the "eye" gets lost
             # smaller means less distractions, but it could lose the object
object_margin = 10

# how quickly the position and size of the object updates (0 < speed =< 1)
speed_position = 0.4
speed_size = 0.2

# ==Foreground (FG) Mask Initialisation (detects movement)==
learning_rate = 0.01
parser = argparse.ArgumentParser(description='This program shows how to use background subtraction methods provided by \
                                              Opencv2. You can process both videos and images.')
parser.add_argument('--input', type=str, help='Path to a video or a sequence of image.', default='vtest.avi')
parser.add_argument('--algo', type=str, help='Background subtraction method (KNN, MOG2).', default='MOG2')
args = parser.parse_args()

if args.algo == 'MOG2':
    backSub = cv2.createBackgroundSubtractorMOG2()
else:
    backSub = cv2.createBackgroundSubtractorKNN()

# ==Camera Properties; resized dimensions, horizon, center of floor==
resizeFactor = 2 # Camera resolution is divided by this number
width = int(width / resizeFactor); height = int(height / resizeFactor)
resizedDimensions = (width, height)
horizon = int(height * 0.4)
centerFloor = [int(width / 2), int(horizon * 1.5)]

# ==Threshold for difference mask==
# This compares the previous frame to next frame (increase for less sensitivity))
threshold_diff_value = 10
threshold_fg_value = 150
threshold_diff_value_object = 20 # currently commented out

interval_bg = 0.01 # how often the background image is updated (in seconds)
interval_diff_bg = 0.01 # currently commented out
interval_wait_for_object = 0.2 # length of time to wait for an object to be placed
interval_obj_id = 3 # how long an object should be in frame before it is IDed as the object

# ==Toggles==
snapshot_diff_taken = False # becomes true once an image has been taken post-object placement
object_identified = False # becomes true once the object has been identified

# Covers the image with rectnagles so that only the object is visible
def hide_background(image, xO, yO, wO, hO):
    cv2.rectangle(image, (0, 0), (max(0, xO - margin), height), black, -1) # left
    cv2.rectangle(image, (xO + wO + margin, 0), (width, height), black, -1) # right
    cv2.rectangle(image, (0, 0), (width, horizon), black, -1) # top
    cv2.rectangle(image, (0, yO + hO + margin), (width, height), black, -1) # bottom

<<<<<<< Updated upstream
def robot_movement(centerXO, centerYO, object_held_distance):
        # Horizontal turns
        distance_to_object = math.sqrt(centerXO ** 2 + centerYO ** 2)
        difference_in_distance = object_held_distance - distance_to_object
        print(" ")
        print("==Distance Stats==")
        print("object_held_distance", object_held_distance)
        print("distance_to_object", distance_to_object)
        print("difference_in_distance", difference_in_distance)

        if centerXO >= width / 2 + object_margin:
            print("turn left")
            fc.turn_left(speed)

        elif centerXO <= width / 2 - object_margin:
            print("turn right")
            fc.turn_right(speed)
        
        elif difference_in_distance > 10: 
            print("object in front")
            fc.forward(speed)

        elif difference_in_distance < -10: 
            print("object in front")
            fc.backward(speed)

        """
        # TODO: Forward speed
        if centerYO >= height / 2 + 10:
            print("forward")
            fc.forward(speed)

        elif centerYO <= height / 2 - 10:
            print("backward")
            fc.backward(speed)

        else: 
            print("object in front")
            fc.forward(speed)"""
=======
def robot_movement(centerXO, centerYO):
    # Horizontal turns
    if centerXO >= width / 2 + 10:
        print("turn left")
        fc.turn_left(speed)

    elif centerXO <= width / 2 - 10:
        print("turn right")
        fc.turn_right(speed)

    else: 
        print("object in front")
        fc.forward(speed)

    # TODO: Forward speed
>>>>>>> Stashed changes

with Picamera2() as camera:
    camera.preview_configuration.main.size = (320,240)
    camera.preview_configuration.main.format = "RGB888"
    camera.preview_configuration.align()
    camera.configure("preview")
    camera.start()

    # Captures the first background image
    background_initial = camera.capture_array()
    
    # ==Timers==
    start_time_bg = time.time()
    update_bg_time = time.time()
    diff_bg_time = time.time()

    # Blurs + resizes background image
    background_initial = cv2.resize(background_initial, resizedDimensions, interpolation=cv2.INTER_LINEAR)
    background_initial = cv2.GaussianBlur(background_initial, (5, 5), 5) 

    while True: # Runs until key is pressed to close
        current_time = time.time() # Updates the current time so the timer can be used

        # Initialise current view
        frame = camera.capture_array()
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, resizedDimensions, interpolation=cv2.INTER_LINEAR)
        frame = cv2.GaussianBlur(frame, blurArea, blurSize)

        # This capture will show the cropped object view once the object is found
        obj_cropped_img = camera.capture_array()

        obj_cropped_img = cv2.flip(obj_cropped_img, 1)
        obj_cropped_img = cv2.resize(obj_cropped_img, resizedDimensions, interpolation=cv2.INTER_LINEAR)
        obj_cropped_img = cv2.GaussianBlur(obj_cropped_img, blurArea, blurSize) 

        # If "O" key is pressed in terminal or cv2 view
        if cv2.waitKey(1) == ord('o'):
            # Saves an image of the view so the contour of the new objects can be found
            if snapshot_diff_taken == False:
                snapshot_diff = camera.capture_array()
                snapshot_diff = cv2.flip(snapshot_diff, 1)
                snapshot_diff = cv2.resize(snapshot_diff, resizedDimensions, interpolation=cv2.INTER_LINEAR)
                snapshot_diff = cv2.GaussianBlur(snapshot_diff, blurArea, blurSize)
                print("'O' key pressed. Detecting object in the current snapshot...")
            
            # Compares difference between initial background photo and current view,
            # then apply greyscale and apply binary filter (based on threshold value)
            difference = cv2.absdiff(background_initial, snapshot_diff)
            #cv2.imshow("difference", difference)
            difference_greyscale = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)
            _, difference_mask = cv2.threshold(difference_greyscale, threshold_diff_value, 255, cv2.THRESH_BINARY)
            #cv2.imshow("difference_mask", difference_mask)

            # ==DIFFERENCE==
            # Erosion and dilation removes noise and thin foreground elements in mask
            difference_mask = cv2.erode(difference_mask, np.ones((3, 3), np.uint8), iterations = 6)
            difference_mask = cv2.dilate(difference_mask, np.ones((7, 7), np.uint8), iterations = 5)
            difference_mask = cv2.erode(difference_mask, np.ones((3, 3), np.uint8), iterations = 5)
            difference_mask = cv2.dilate(difference_mask, np.ones((9, 9), np.uint8), iterations = 6)
            #cv2.imshow("difference_mask_processed", difference_mask)

            # Find contours from the resultant mask
            contours, hierarchy = cv2.findContours(difference_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # Count the number of contours in the mask
            color_area_num = len(contours)
            
            if color_area_num > 0:
                print("An object has been found :)")
                snapshot_diff_taken = True

                # Initialises default distance from object to centre of horizon
                lowestDis = 1000

                # For each contour, make a bounding box
                for i in contours:
                    # x, y are the top left coords, w, h are the width and height (of the contour)
                    x, y, w, h = cv2.boundingRect(i)

                    # Center pixels of the contour
                    centerX = x + int((w / 2))
                    centerY = y + int((h / 2))

                    area = w * h

                    # If the contour's vertical center is on the floor (below the horizon) and it's bigger than 20x20...
                    if centerY > horizon and w >= 10 and h >= 10:
                        # Calculate its distance to the center of the floor
                        centerDis = (abs(centerFloor[0] - centerX) + abs(centerFloor[1] - centerY))

                        # Find the contour on the floor with the centre-most dimensions,
                        # and save them into the global variables
                        if (centerDis < lowestDis):
                            lowestDis = centerDis
                            # The coordinates of the "object" are saved into these variables
                            global xO; global yO; global wO; global hO
                            xO = x; yO = y; wO = w; hO = h

                            # Calculate center of the object
                            centerXO = xO + int((wO / 2))
                            centerYO = yO + int((hO / 2))

                            print("Object Coords:", centerXO, centerYO)

                            object_held_distance = math.sqrt(centerXO * centerXO + centerYO * centerYO)
                            print("Maintain object distance at:", object_held_distance, "pls. Thank you.")
                            object_identified = True # An object has been found, so this is now True

            else:
                print("No object found :( pls try again.")          
        
        # Tracks Object
        if object_identified == True:
            # Updates the background image once "interval" time has passed
            # This does not overwrite the original background image! Maybe it should lmao.
            if update_bg_time + interval_bg < current_time:
                update_bg_time = time.time()
                background = camera.capture_array()
                background = cv2.flip(background, 1)
                background = cv2.resize(background, resizedDimensions, interpolation=cv2.INTER_LINEAR)
                background_blurred = cv2.GaussianBlur(background, blurArea, blurSize)
            
            # Create a frame of the current object view
            hide_background(obj_cropped_img, xO, yO, wO, hO)
            #cv2.imshow("obj_cropped_img", obj_cropped_img)
            
            # === FOREGROUND ====
            # Detects changes in the camera view
            fg = backSub.apply(frame, learningRate = learning_rate)
            #cv2.imshow("fg", fg)

            _, fg = cv2.threshold(fg, threshold_fg_value, 255, cv2.THRESH_BINARY)
            #cv2.imshow("fg_thresh", fg)

            # Removes noise/thin objects/ropes
            fg = cv2.erode(fg, np.ones((3, 3), np.uint8), iterations = 3)
            fg = cv2.dilate(fg, np.ones((7, 7), np.uint8), iterations = 3)
            #hide_background(fg, xO, yO, wO, hO)
            #cv2.imshow("fg_processed", fg)

            # Finds contours of the moving objects
            fg_contours, hierarchy = cv2.findContours(fg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            filter_contours = [] 

            # Count the number of contours in the mask
            color_area_num = len(fg_contours)

            # Initialises default distance from contours to known centre of object
            lowestDis = 100000000

            if color_area_num > 0:
                for i in fg_contours:
                    # x, y are the top left coords, w, h are the width and height (of the contour)
                    x, y, w, h = cv2.boundingRect(i)

                    # Center pixels of the contour
                    centerX = x + int((w / 2))
                    centerY = y + int((h / 2))

                    area = cv2.contourArea(i)
                    areaStr = str(cv2.contourArea(i))
                    if centerY > horizon and w >= 10 and h >= 10 and area < 10000:

                        # Calculate distance from contour to known center of object
                        centerDis = (abs(centerXO - centerX) + abs(centerYO - centerY))

                        cv2.putText(frame, areaStr, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (0, 0, 255), 1)
                        # Find the contour with the centre nearest to the object's centre, and save them into the object variables
                        if (centerDis < lowestDis):
                            lowestDis = centerDis
                            # These are the target values for the object
                            xT = x; yT = y; wT = w; hT = h

                            filter_contours.append(i)

                # Draw the contours of objects below the horizon
                cv2.drawContours(frame, filter_contours, -1, blue, 7)
                
                # create black frame the size of the camera
                filter_contour_mask = np.zeros(frame.shape, np.uint8)
                #filter_contour_mask = cv2.threshold(filter_contour_mask, threshold_diff_value, 255, cv2.THRESH_BINARY)
                filter_contour_mask = cv2.cvtColor(filter_contour_mask, cv2.COLOR_BGR2GRAY)

                cv2.drawContours(filter_contour_mask, filter_contours, -1, white, -1) ####

                mask_frame = cv2.bitwise_and(frame, frame, mask = filter_contour_mask)
                cv2.circle(mask_frame, (centerXO, centerYO), 30, magenta, 2)

                #cv2.imshow("filter_contour_mask", filter_contour_mask)  
                #cv2.imshow("mask_frame", mask_frame)

                # Once the object's new position has been found, the properties of the object gradually change to
                # those new properties
                xO = int(xO + (xT - xO) * speed_position)
                yO = int(yO + (yT - yO) * speed_position)
                wO = int(wO + (wT - wO) * speed_size)
                hO = int(hO + (hT - hO) * speed_size)

                # Updates center of the object
                centerXO = xO + int((wO / 2))
                centerYO = yO + int((hO / 2))
                print("Center Objetc:", centerXO)
                
            # Draw small white circle on the center of object; this is the object tracker!
            cv2.circle(frame, (centerXO, centerYO), 10, magenta, -1)
            
            robot_movement(centerXO, centerYO, object_held_distance)

        # Places line at the horizon (for our reference)
        cv2.line(frame, (0, horizon), (width, horizon), blue, 1)
        cv2.imshow("frame_blurred", frame)
        # Press 'q' to exit the loop
        if cv2.waitKey(1) == ord('q'):
            fc.stop()
            break

    # For Martina:
    # centerXO, centerYO