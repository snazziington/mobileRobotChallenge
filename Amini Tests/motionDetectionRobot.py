from __future__ import print_function
import cv2
from picamera2 import Picamera2
import numpy as np
import argparse

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

with Picamera2() as camera:
    print("start edge detect")
    camera.preview_configuration.main.size = (320,240)
    camera.preview_configuration.main.format = "RGB888"
    camera.preview_configuration.align()
    camera.configure("preview")
    camera.start()

    background = camera.capture_array() #frame.array

    # Blurs the background image
    background_blurred = cv2.GaussianBlur(background, (5, 5), 5) 

    while True:
        frame = camera.capture_array() #frame.array
        
        # Captures current camera view and blurs it
        frame_blurred = cv2.GaussianBlur(frame, (5, 5), 5) 

        # This highlights the difference between subsequent frames
        fgMask = backSub.apply(frame_blurred)
        cv2.imshow('FG Mask', fgMask)

        k = cv2.waitKey(1) & 0xFF
        # 27 is the ESC key, which means that if you press the ESC key to exit
        if k == 27:
            break

    print('quit ...') 
    cv2.destroyAllWindows()
    camera.close()  