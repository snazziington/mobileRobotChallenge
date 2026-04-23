from __future__ import print_function
import cv2
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

capture = cv2.VideoCapture(0)

ret_bg, background = capture.read()

# Blurs the background image
background_blurred = cv2.GaussianBlur(background, (5, 5), 5) 

while True:
    # Captures current camera view and blurs it
    ret, frame = capture.read()
    frame_blurred = cv2.GaussianBlur(frame, (5, 5), 5) 

    # This highlights the difference between subsequent frames
    fgMask = backSub.apply(frame_blurred)
    cv2.imshow('FG Mask', fgMask)

    keyboard = cv2.waitKey(30)
    if keyboard == 'q' or keyboard == 27:
        break