# Canny edge bottom screen distance detection for pi cam on robot
# Using a cropped frame from the full image, assuming that the object is in the middle and bottom half

print('Please run under desktop environment (eg: vnc) to display the image window')

import cv2
from picamera2 import Picamera2
import numpy as np

kernel_5 = np.ones((5,5),np.uint8) #Define a 5×5 convolution kernel with element values of all 1.

# Open the default camera
cam = cv2.VideoCapture(1)

# Get the default frame width and height
frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))

# Define area we expect the object to be within
x_start, y_start, x_end, y_end = 50, 120, 250, 240 
cropped_height = y_end - y_start

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

        cropped = edges[y_start:y_end, x_start:x_end] # Crop the image using slicing
        coords = np.argwhere(cropped > 250) # Search for near-white values

        if coords.shape[0] > 0:
            x_positions = coords[:, 1]
            y_positions = coords[:, 0]
            lowest = cropped_height-np.max(y_positions) # because y=0 is on top
            print(lowest)

            # Drawing thick grey dots to indicate edges within cropped area
            # Comment out for actual challenge to reduce processing
            for y, x in coords:
                cv2.circle(cropped, (x, y), 5, 128, -1)

        cv2.imshow("video", edges)    # OpenCV image show
    
        k = cv2.waitKey(1) & 0xFF
        # 27 is the ESC key, which means that if you press the ESC key to exit
        if k == 27:
            break

    print('quit ...') 
    cv2.destroyAllWindows()
    camera.close()  