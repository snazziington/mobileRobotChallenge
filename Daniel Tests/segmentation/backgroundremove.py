import cv2
import numpy as np

windowTitle = "Background Removal"

cv2.namedWindow(windowTitle)
cam = cv2.VideoCapture(0)

# Creates the background subtractor
fgBg = cv2.createBackgroundSubtractorMOG2(history=100, detectShadows=False)

while True:

    ret, frame = cam.read()

    # Flips the frame to be the right orientation
    frame = cv2.flip(frame,1)

    # Applies a slight blur to reduce noise
    frame = cv2.GaussianBlur(frame, (25,25), 2)

    mask = fgBg.apply(frame)

    # Applies a threshold to the mask to ensure a clean mask
    ret, mask = cv2.threshold(mask,127,255,cv2.THRESH_BINARY)

    # Repeated erosion and dilation to remove noise and thin foreground elements in mask
    mask = cv2.erode(mask, np.ones((3,3), np.uint8), iterations = 5)

    mask = cv2.dilate(mask, np.ones((7,7), np.uint8), iterations = 5)

    mask = cv2.erode(mask, np.ones((3,3), np.uint8), iterations = 5)

    mask = cv2.dilate(mask, np.ones((9,9), np.uint8), iterations = 7)

    maskFrame = cv2.bitwise_and(frame,frame,mask = mask)

    # Detects the contours on the remaining Background Removal Mask
    contours, hierarchy = cv2.findContours(image=mask, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
    filtContours = []

    #Prints the area of the largest contour for testing/tuning
    if len(contours) != 0:
        c = max(contours, key = cv2.contourArea)
        print(cv2.contourArea(c))

    # Filters Contours by area Note: should still be tuned
    for contour in contours:
        area = cv2.contourArea(contour)

        if area > 8000 and area < 35000:
            filtContours.append(contour)

    # Draws the contours onto the frame
    cv2.drawContours(image=maskFrame, contours=filtContours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)

    # Display the processed frame
    cv2.imshow(windowTitle, maskFrame)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) == ord('q'):
        break
