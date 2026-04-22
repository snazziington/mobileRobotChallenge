#!/usr/bin/env python3
# Canny edge detection for pi cam on robot

print('Please run under desktop environment (eg: vnc) to display the image window')

import cv2
from picamera2 import Picamera2
import numpy as np
import time

kernel_5 = np.ones((5,5),np.uint8) #Define a 5×5 convolution kernel with element values of all 1.

with Picamera2() as camera:
    print("start edge detect")
    camera.preview_configuration.main.size = (320,240)
    camera.preview_configuration.main.format = "RGB888"
    camera.preview_configuration.align()
    camera.configure("preview")
    camera.start()

    while True:
        img = camera.capture_array() #frame.array
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #turn grayscale
        blur = cv2.GaussianBlur(gray, (5, 5), 1.4) #removing noise -- increasing the last number increases blur
        edges = cv2.Canny(blur, threshold1=100, threshold2=200) # Apply Canny Edge Detector -- default is 100-200

        cv2.imshow("video", edges)    # OpenCV image show
    
        k = cv2.waitKey(1) & 0xFF
        # 27 is the ESC key, which means that if you press the ESC key to exit
        if k == 27:
            break

    print('quit ...') 
    cv2.destroyAllWindows()
    camera.close()  
