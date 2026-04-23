# Canny edge detection on laptop webcam for local testing

import cv2
from skimage.metrics import structural_similarity
import numpy as np

# Open the default camera
cam = cv2.VideoCapture(0)

# Get the default frame width and height
frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Captures an initial frame
initRet, initFrame = cam.read()
initFrame = cv2.flip(initFrame, 1)

initGray = cv2.cvtColor(initFrame, cv2.COLOR_BGR2GRAY) 
initGray = cv2.bilateralFilter(initGray, 7, 100, 100)


while True:
    ret, frame = cam.read()

    frame = cv2.flip(frame, 1)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)          # Turn grayscale
    gray = cv2.bilateralFilter(gray, 7, 100, 100)

    ssim, diffMask = structural_similarity(initGray, gray, full=True)

    diffMask = (diffMask * 255).astype("uint8")

    


    cv2.imshow("Gray", diffMask)
    #cv2.imshow("fasdf", gray)
    #cv2.imshow("video", edges)    # OpenCV image show

    # Press 'c' to retake the reference picture
    if cv2.waitKey(1) == ord('c'):
        initRet, initFrame = cam.read()
        initFrame = cv2.flip(initFrame, 1)

        initGray = cv2.cvtColor(initFrame, cv2.COLOR_BGR2GRAY) 
        initGray = cv2.bilateralFilter(initGray, 7, 100, 100)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) == ord('q'):
        break

# Release the capture and writer objects
cam.release()
cv2.destroyAllWindows()