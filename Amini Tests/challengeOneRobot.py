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

# ==Object Following Variables==
# size of edge margin for the object view
margin = 400 # bigger means code can find object if the "eye" gets lost
             # smaller means less distractions, but it could lose the object

# how quickly the position and size of the object updates (0 < speed =< 1)
speed_position = 0.5
speed_size = 0.3

# ==Camera Properties; resized dimensions, horizon, center of floor==
resizeFactor = 4 # Camera resolution is divided by this number
width = int(width / resizeFactor); height = int(height / resizeFactor)
resizedDimensions = (width, height)
horizon = int(height * 0.4)
centerFloor = [int(width / 2), int(horizon * 1.5)]

# ==Threshold for difference mask==
# This compares the previous frame to next frame (increase for less sensitivity))
threshold_diff_value = 10
threshold_diff_value_object = 20 # currently commented out

interval_bg = 0.01 # how often the background image is updated (in seconds)
interval_diff_bg = 0.01 # currently commented out
interval_wait_for_object = 0.2 # length of time to wait for an object to be placed
interval_obj_id = 3 # how long an object should be in frame before it is IDed as the object

# ==Toggles==
snapshot_diff_taken = False # becomes true once an image has been taken post-object placement
object_identified = False # becomes true once the object has been identified

# Robot Movement
speed = 40
interval_turn = 0.1 # Time spent turning
object_held_distance = 350 # Distance to maintain from object
object_distance_margin = 50
object_angle_margin = 30

def robot_movement(centerXO, centerYO, object_held_distance):
        # Object Distance Calculations
        horizontal_distance_object = width / 2 - centerXO
        vertical_distance_object = height - centerYO
        pixel_distance_to_object = math.sqrt(horizontal_distance_object ** 2 + vertical_distance_object ** 2)
        object_angle = int(math.degrees(math.asin(horizontal_distance_object / pixel_distance_to_object))  ) 

        # Exponential ratio for pixel distance
        ratio = 1.5
        distance_to_object = pixel_distance_to_object ** ratio
        difference_in_distance = distance_to_object - object_held_distance

        # Defining turning speed
        #if object_angle < 30: turning_speed = 2
        #else:
        turning_speed = min(80, np.interp(abs(object_angle), [15, 50], [1, 15]))
        
        # Defining forward speed
        forward_speed = min(120, abs(difference_in_distance / 1.2))

        print(" ")
        print("==Distance Stats==")
        print("Vertical distance:", vertical_distance_object)
        print("Horizontal distance:", horizontal_distance_object)
        print("object_held_distance", object_held_distance)
        print("distance_to_object", distance_to_object)
        print("difference_in_distance", difference_in_distance)
        print("Object angle", object_angle)
        print("turning_speed", turning_speed)
        print("forward_speed", forward_speed)

        if difference_in_distance < -(object_distance_margin): 
            print("object close")
            fc.backward(forward_speed)
        
        elif object_angle < -(object_angle_margin):
            fc.turn_left(turning_speed)
            print("turn left")

        elif object_angle > object_angle_margin:
            fc.turn_right(turning_speed)
            print("turn right")

        elif difference_in_distance > object_distance_margin: 
            print("object far")
            fc.forward(forward_speed)

        else: 
            print("object distance is perfect :)")
            fc.stop()

xT = 180; yT = 160; wT = 50; hT = 50

color_dict = {'red':[0, 4], 'orange':[5, 18], 'yellow':[22, 37], 'green':[42, 85], 'blue':[92, 110], 'purple':[115, 165], 'red_2':[165, 180]}  #Here is the range of H in the HSV color space represented by the color

def color_detect(img, color_name):
    # The blue range will be different under different lighting conditions and can be adjusted flexibly.  H: chroma, S: saturation v: lightness
    resize_img = cv2.resize(img, (width, height), interpolation=cv2.INTER_LINEAR)  # In order to reduce the amount of calculation, the size of the picture is reduced to (160, 120)
    hsv = cv2.cvtColor(resize_img, cv2.COLOR_BGR2HSV)              # Convert from BGR to HSV
    color_type = color_name
    
    mask = cv2.inRange(hsv, np.array([min(color_dict[color_type]), 60, 0]), np.array([max(color_dict[color_type]), 255, 255]) )           # inRange()：Make the ones between lower/upper white, and the rest black
    
    if color_type == 'red':
            mask_2 = cv2.inRange(hsv, (color_dict['red_2'][0], 25, 255), (color_dict['red_2'][1], 25, 255)) 
            mask = cv2.bitwise_or(mask, mask_2)

    # Find the contour in mask, and the contours are arranged according to the area from small to large.
    _tuple = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)      
    # compatible with opencv3.x and openc4.x
    if len(_tuple) == 3:
        _, contours, hierarchy = _tuple
    else:
        contours, hierarchy = _tuple
    
    color_area_num = len(contours) # Count the number of contours

    if color_area_num > 0: 
        for i in contours:    # Traverse all contours
            x, y, w, h = cv2.boundingRect(i)      # Decompose the contour into the coordinates of the upper left corner and the width and height of the recognition object

            # Draw a rectangle on the image (picture, upper left corner coordinate, lower right corner coordinate, color, line width)
            cv2.rectangle(img, (x, y), (x+ w, y+ h), (0, 255, 0), 2)  # Draw a rectangular frame
            cv2.putText(img, color_type, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)# Add character description

    return mask

with Picamera2() as camera:
    camera.preview_configuration.main.size = (640, 480)
    camera.preview_configuration.main.format = "RGB888"
    camera.preview_configuration.align()
    camera.configure("preview")
    camera.start()

    # Captures the first background image
    background_initial = camera.capture_array()
    background_initial = cv2.flip(background_initial, 1)

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
        frame_current = camera.capture_array()
        frame_current = cv2.flip(frame_current, 1)
        frame_current = cv2.resize(frame_current, resizedDimensions, interpolation=cv2.INTER_LINEAR)
        frame_current = cv2.GaussianBlur(frame_current, blurArea, blurSize) 

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
            difference_mask = cv2.erode(difference_mask, np.ones((2, 2), np.uint8), iterations = 2)
            difference_mask = cv2.dilate(difference_mask, np.ones((4, 4), np.uint8), iterations = 2)
            #cv2.imshow("difference_mask_processed", difference_mask)

            # Find contours from the resultant mask
            contours, hierarchy = cv2.findContours(difference_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # Count the number of contours in the mask
            color_area_num = len(contours)
            
            if color_area_num > 0:
                print("An object has been found :)")
                snapshot_diff_taken = True

                # Initialises default distance from object to centre of horizon
                lowestDis = 1000000

                # For each contour, make a bounding box
                for i in contours:
                    # x, y are the top left coords, w, h are the width and height (of the contour)
                    x, y, w, h = cv2.boundingRect(i)
                    print("Coords of new objects:", x, y, w, h)
                    # Center pixels of the contour
                    centerX = x + int((w / 2))
                    centerY = y + int((h / 2))

                    area = w * h

                    # If the contour's vertical center is on the floor (below the horizon) and it's bigger than 20x20...
                    if centerY > horizon:
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
                            centerXO = xO + wO // 2
                            centerYO = yO + hO // 2

                            print("Object Coords:", centerXO, centerYO)

                            #object_held_distance = math.sqrt(centerXO ** 2 + centerYO ** 2)
                            print("Maintain object distance at:", object_held_distance, "pls. Thank you.")
                            object_identified = True # An object has been found, so this is now True

            else:
                print("No object found :( pls try again.")          
        
        # Tracks Object
        if object_identified == True:
            red_mask = color_detect(frame, 'red')  # Color detection function
            cv2.imshow("red_mask", red_mask)    # OpenCV image show
        
            # Finds contours of the moving objects
            red_contours, hierarchy = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            filter_contours = [] 

            # Count the number of contours in the mask
            color_area_num = len(red_contours)

            # Initialises default distance from contours to known centre of object
            lowestDis = 100000000

            if color_area_num > 0:
                for i in red_contours:
                    # x, y are the top left coords, w, h are the width and height (of the contour)
                    x, y, w, h = cv2.boundingRect(i)

                    # Center pixels of the contour
                    centerX = x + int((w / 2))
                    centerY = y + int((h / 2))

                    area = cv2.contourArea(i)
                    areaStr = str(cv2.contourArea(i))
                    if centerY > horizon:
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
                print("Center Objetc:", centerXO, centerYO)
                
            # Draw small white circle on the center of object; this is the object tracker!
            cv2.circle(frame_current, (centerXO, centerYO), 10, magenta, -1)
            robot_movement(centerXO, centerYO, object_held_distance)

        # Places line at the horizon (for our reference)
        cv2.line(frame, (0, horizon), (width, horizon), blue, 1)
        frame = cv2.flip(frame, 1)

        cv2.imshow("mask_frame", frame) # Shows colour mask
        cv2.imshow("frame_current", frame_current) # Shows current frame w/ dot on object

        # Press 'q' to exit the loop
        if cv2.waitKey(1) == ord('q'):
            fc.stop()
            break