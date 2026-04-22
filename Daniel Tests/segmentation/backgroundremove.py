import cv2
import numpy as np

windowTitle = "Background Removal"

cv2.namedWindow(windowTitle)
cam = cv2.VideoCapture(0)

fgBg = cv2.createBackgroundSubtractorMOG2(history=100)

# Setup SimpleBlobDetector parameters
params = cv2.SimpleBlobDetector_Params()
 
# Thresholds for binarization
params.minThreshold = 10
params.maxThreshold = 200
 
# Filter by Area
params.filterByArea = True
params.minArea = 500
 
# Filter by Circularity
params.filterByCircularity = False
params.minCircularity = 0.1
 
# Filter by Convexity
params.filterByConvexity = False
params.minConvexity = 0.87
 
# Filter by Inertia
params.filterByInertia = True
params.minInertiaRatio = 0.01

detector = cv2.SimpleBlobDetector_create(params)

while True:

    ret, frame = cam.read()

    #Flips the frame to be the right orientation
    frame = cv2.flip(frame,1)

    #mask = fgBg.apply(frame)

    # Detect blobs
    keypoints = detector.detect(frame)
 
    # Draw blobs as red circles
    output = cv2.drawKeypoints(frame, keypoints, np.array([]), (0, 0, 255),
                                cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    # Display the captured frame
    cv2.imshow(windowTitle, output)
    #cv2.imshow("Foreground Mask", mask)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) == ord('q'):
        break
