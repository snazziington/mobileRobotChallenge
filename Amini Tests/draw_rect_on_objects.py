import numpy as np
import cv2

cam = cv2.VideoCapture(1)
while True:
    # Captures current camera view and blurs it
    ret, frame = cam.read()
    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    ret, thresh = cv2.threshold(img_gray, 127, 255, 0)
    im2, contours = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    print("cont", contours)
    cnt = contours[0]
    cv2.drawContours(img_gray, [cnt], 4, (0, 255, 0), 3)

    keyboard = cv2.waitKey(30)
    if keyboard == 'q' or keyboard == 27:
        break