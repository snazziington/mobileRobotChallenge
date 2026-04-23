from __future__ import print_function
import cv2
import numpy as np
import argparse

# Just messing with "new" object detection.
# When program starts, it saves a snapshot of the environment. New objects will show up on the "difference" window
# Could expanded on to have every new object outlined, and calculate likeliness that each new object is _the_ object
# Then aim to follow that specific object via edge-detection maybe

# region Uncomment this if you want to see the "fgMask" wayy below
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

capture = cv2.VideoCapture(0)
color_dict = {'red':[0,4],'orange':[5,18],'yellow':[22,37],'green':[42,85],'blue':[92,110],'purple':[115,165],'red_2':[165,180]}  #Here is the range of H in the HSV color space represented by the color

kernelSize = 20
kernel = np.ones((kernelSize, kernelSize), np.uint8) #Define a kernelSize x kernelSize convolution kernel with element values of all 1.
valueLow = 20

# Captures background image that will be compared to camera footage
    # Has to be a longer exposure to make up for little things moving in background/lighting etc.
    # If possible, also increase/decrease exposure and save those snapshots as background too
ret_bg, background = capture.read()

# Blurs the background image
background_blurred = cv2.GaussianBlur(background, (5, 5), 5) 

# what if we first apply threshold and then look at difference?
    # but if the new object is similar in colour, it will not be detected.
    # also maybe instead of doing binary we should do like, 8 levels of brightness.

def color_detect(img, color_name):

    # In order to reduce the amount of calculation, the size of the picture is reduced from (640, 480) to (160, 120)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) # Convert from BGR to HSV
    color_type = color_name
    
    mask = cv2.inRange(hsv,np.array([min(color_dict[color_type]), valueLow, valueLow]), np.array([max(color_dict[color_type]), 255, 255])) # inRange()：Make the ones between lower/upper white, and the rest black
    if color_type == 'red':
            mask_2 = cv2.inRange(hsv, (color_dict['red_2'][0], valueLow, valueLow), (color_dict['red_2'][1],255,255))
            mask = cv2.bitwise_or(mask, mask_2)

    else:
            mask_2 = cv2.inRange(hsv, (color_dict[color_name][0], valueLow, valueLow), (color_dict[color_name][1],255,255))
            mask = cv2.bitwise_or(mask, mask_2)

    morphologyEx_img = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1) # Perform an open operation on the image 

    # Find the contour in morphologyEx_img, and the contours are arranged according to the area from small to large.
    _tuple = cv2.findContours(morphologyEx_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    
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
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)  # Draw a rectangular frame
                cv2.putText(img,color_type,(x,y), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),2)# Add character description

    return img,mask,morphologyEx_img

while True:
    # Captures current camera view and blurs it
    ret, frame = capture.read()
    frame_blurred = cv2.GaussianBlur(frame, (5, 5), 5) 

    # Compares colour difference between background and video
    difference = cv2.absdiff(background_blurred, frame_blurred)
    
    # Makes difference greyscale
    difference_greyscale = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)

    # Applies threshold to get binary values of difference
    _, difference_greyscale_threshold = cv2.threshold(difference_greyscale, 50, 255, cv2.THRESH_BINARY)
    
    _, difference_greyscale_threshold = cv2.threshold(difference_greyscale, 50, 255, cv2.THRESH_BINARY)

    _, thresh = cv2.threshold(difference_greyscale_threshold, 50, 255, cv2.THRESH_BINARY)
    binary = cv2.threshold(difference, 127, 255, cv2.THRESH_BINARY)

    
    #cv2.imshow('Background Image Blurred', background_blurred)
    #cv2.imshow('Frame Blurred', frame_blurred)
    cv2.imshow('difference', difference)
    cv2.imshow('thresh', thresh)

    img, img_2, img_3 = color_detect(frame_blurred, 'red')  # Color detection function
    cv2.imshow("video", img)    # OpenCV image show
    #cv2.imshow("morphologyEx_img", img_3)    # OpenCV image show
    morph2 = cv2.morphologyEx(img_2, cv2.MORPH_OPEN, kernel, iterations=1) # Perform an open operation on the image 

    maskDiff = cv2.inRange(cv2.cvtColor(img, cv2.COLOR_BGR2HSV), (255, 255, 255), (255, 255, 255))

    masked = cv2.bitwise_and(frame_blurred, frame_blurred, mask=thresh)
    cv2.imshow("masked", masked)
    # This highlights the difference between subsequent frames
    fgMask = backSub.apply(frame)
    cv2.imshow('FG Mask', fgMask)

    keyboard = cv2.waitKey(30)
    if keyboard == 'q' or keyboard == 27:
        break