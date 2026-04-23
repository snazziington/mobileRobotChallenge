#!/usr/bin/env python3

print('Please run under desktop environment (eg: vnc) to display the image window')

import cv2
from picamera2 import Picamera2
import numpy as np
import time

# Range of H (hue) in the HSV color space represented by the color
    # Hue ranges from 0 to 180
color_dict = {'red': [0, 4], 'orange': [5, 18], 'yellow': [22, 37], 'green': [42, 85], 
              'blue': [92, 110], 'purple': [115, 165], 'red_2': [165, 180]} 

# Define a 5×5 convolution kernel (array(?)), all values are 1
kernel_5 = np.ones((5, 5), np.uint8) # np.uint8; 8-bit integers (max value = 255)

# Determines size of image (so it's easily changeable)
resizeFactor = 4 # Camera resolution is divided by this number
resizedDimensions = (640 / resizeFactor, 480 / resizeFactor)

def color_detect(img, color_name):

    # Blue range will be different under different lighting conditions + can be adjusted flexibly.
    # H: chroma, S: saturation v: lightness

    # In order to reduce the amount of calculation, the size of the picture is reduced from (640, 480) to (160, 120) (divided by "resizeFactor")
    resize_img = cv2.resize(img, resizedDimensions, interpolation=cv2.INTER_LINEAR)

    # Convert colour space from BGR to HSV
    hsv = cv2.cvtColor(resize_img, cv2.COLOR_BGR2HSV) 

    # Color type is equal to the Color name parameter from this function
    color_type = color_name
    
    # Creates a mask with following specifications
        # If a pixel's H value is between the lower and upper bound of said colour, and the S and L ranges between 60 and 255,
        # create a mask of those pixels
    mask = cv2.inRange(hsv,
                       np.array([min(color_dict[color_type]), 60, 60]),   
                       np.array([max(color_dict[color_type]), 255, 255])) 

    # TODO: No idea what's going on here
    if color_type == 'red':
            mask_2 = cv2.inRange(hsv,
                                 (color_dict['red_2'][0], 0, 0),
                                 (color_dict['red_2'][1], 255, 255))
            mask = cv2.bitwise_or(mask, mask_2)
    
    morphologyEx_img = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_5, iterations=1) # Perform an open operation on the image 

    # Find the contour in morphologyEx_img, and the contours are arranged according to the area from small to large.
    _tuple = cv2.findContours(morphologyEx_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)      
    
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
            if w >= 8 and h >= 8: # Because the picture is reduced to a quarter of the original size, if you want to draw a rectangle on the original picture to circle the target, you have to multiply x, y, w, h by 4.
                x = x * resizeFactor
                y = y * resizeFactor
                w = w * resizeFactor
                h = h * resizeFactor
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)  # Draw a rectangular frame
                cv2.putText(img, color_type, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2) # Add character description

    return img, mask, morphologyEx_img

with cv2.VideoCapture(0) as camera:
    print("start color detect")

    # Initialising camera
    camera.preview_configuration.main.size = (resizedDimensions)
    camera.preview_configuration.main.format = "RGB888"
    camera.preview_configuration.align()
    camera.configure("preview")
    camera.start()

    # TODO: Write out
    """
    For the first 60 seconds, look at the background and "memorise" it.
    When something new appears, memorise the colours within a certain range (range of hsl)
    Create a white mask of the object and render it
    """

    while True: # loops indefinitely until "return" or "break"
        img = camera.capture_array() # frame.array
        img, img_2, img_3 = color_detect(img, 'red') # img 1, 2 and 3 are "img", "mask", and "morphologyEx_img" respectively
        cv2.imshow("video", img)    # OpenCV image show
        cv2.imshow("mask", img_2)   # OpenCV image show
        cv2.imshow("morphologyEx_img", img_3)    # OpenCV image show
    
        k = cv2.waitKey(1) & 0xFF
        # 27 is the ESC key, which means that if you press the ESC key to exit
        if k == 27:
            break

    # Only executes these commands once the loop is broken by pressing ESC key
    print('quit ...') 
    cv2.destroyAllWindows()
    camera.close()  
