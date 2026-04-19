import cv2
import numpy as np

windowTitle = "Basic Segmentation"

cv2.namedWindow(windowTitle)
cam = cv2.VideoCapture(0)

width  = cam.get(3) 
height = cam.get(4)

print(width)
print(height)

#sets coordinates for floor color detection
x1 = int(width//8)
x2 = int(width - width//8)
y1 = int(height - height//4)
y2 = int(height)

# Sets dimensions for the resized floor detect region
blurWidth = (x2-x1)//4
blurHeight = (y2-y1)//4

while True:

    ret, frame = cam.read()

    #Flips the frame to be the right orientation
    frame = cv2.flip(frame,1)

    #creates the frame for floor detection
    floorReg = frame[y1:y2, x1:x2]
    floorReg = cv2.resize(floorReg, (blurWidth, blurHeight), interpolation=cv2.INTER_LINEAR)
    blur = cv2.blur(floorReg,(blurWidth,blurHeight))
    floorColHSV = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    floorColPix = blur[blurHeight//2, blurWidth//2]
    floorPixHSV = floorColHSV[blurHeight//2, blurWidth//2]

    # Sets the floor color detection bounds
    lowerFloor = np.array([int(floorPixHSV[0])-15, 50, 50])
    upperFloor = np.array([int(floorPixHSV[0])+15, 253, 253])

    # Creates an image mask
    mask = cv2.inRange(cv2.cvtColor(frame, cv2.COLOR_BGR2HSV), lowerFloor, upperFloor)

    # Uncomment to draw rectangle around floor detect region
    cv2.rectangle(frame, (x1,y1), (x2,y2), (int(floorColPix[0]), int(floorColPix[1]), int(floorColPix[2])),3)

    # Display the captured frame
    cv2.imshow(windowTitle, frame)
    cv2.imshow("Floor Mask", mask)
    #cv2.imshow("Blur", blur)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) == ord('q'):
        break
