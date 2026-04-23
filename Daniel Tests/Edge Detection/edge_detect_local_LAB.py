# Canny edge detection on laptop webcam for local testing

import cv2
import numpy as np

# Open the default camera
cam = cv2.VideoCapture(0)

# Get the default frame width and height
frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

sharpKernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])


while True:
    ret, frame = cam.read()

    frame = cv2.flip(frame, 1)

    blur = cv2.GaussianBlur(frame, (5, 5), 2)              # Removing noise -- increasing the last number increases blur
    frameLAB = cv2.cvtColor(blur, cv2.COLOR_BGR2LAB)         # Turn to LAB

    L, A, B = cv2.split(frameLAB)

    lBlur = cv2.GaussianBlur(L, (13, 13), 2.2)

    frameLAB = cv2.merge([lBlur, A, B])

    frameLABHSV = cv2.cvtColor(frameLAB, cv2.COLOR_BGR2HSV)

    edges = cv2.Canny(frameLABHSV, threshold1=60, threshold2=40)
    edges = cv2.dilate(edges, (5,5), iterations= 3)

    contours, hierarchy = cv2.findContours(image=edges, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
    filtContour = []

    # Filters out contours that are too big or too small
    for contour in contours:
        area = cv2.contourArea(contour)

        if area > 250 and area < 1500:
            filtContour.append(contour)

    #cv2.drawContours(image=frame, contours=filtContour, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)

    cv2.imshow("Orig Image", cv2.equalizeHist(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)))
    cv2.imshow("LAB Image", frameLABHSV)
    #cv2.imshow("Lab Image Gray", frameLGray)
    cv2.imshow("Edge Detect", edges)


    # Press 'q' to exit the loop
    if cv2.waitKey(1) == ord('q'):
        break

# Release the capture and writer objects
cam.release()
cv2.destroyAllWindows()