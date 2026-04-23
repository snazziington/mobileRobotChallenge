import cv2
import numpy as np

def floorMasker(frame, width, height):
    # Creates the frame for floor detection
    floorReg = frame[y1:y2, x1:x2]
    floorReg = cv2.resize(floorReg, (blurWidth, blurHeight), interpolation=cv2.INTER_LINEAR)
    blur = cv2.blur(floorReg,(blurWidth,blurHeight))
    floorColHSV = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    floorColPix = blur[blurHeight//2, blurWidth//2]
    floorPixHSV = floorColHSV[blurHeight//2, blurWidth//2]

    # Splits the frame into its HSV components and blurs the Value component
    h,s,v = cv2.split(cv2.cvtColor(frame, cv2.COLOR_BGR2HSV))
    vblur = blur = cv2.blur(v,(10,10))

    # Reconstructs the frame with the blurred Value
    blurFrame = cv2.cvtColor(cv2.merge([h,s,vblur]), cv2.COLOR_HSV2BGR)

    # Sets the floor color detection bounds
    lowerFloor = np.array([int(floorPixHSV[0])-15, int(floorPixHSV[1])-25, 30])
    upperFloor = np.array([int(floorPixHSV[0])+15, int(floorPixHSV[1])+25, 253])

    # Creates an image mask based off of the frame with blurred Value
    mask = cv2.inRange(cv2.cvtColor(blurFrame, cv2.COLOR_BGR2HSV), lowerFloor, upperFloor)

    return mask, floorColPix, floorPixHSV

windowTitle = "Basic Segmentation"

cv2.namedWindow(windowTitle)
cam = cv2.VideoCapture(1)

width  = cam.get(3) 
height = cam.get(4)

print(width)
print(height)

#sets coordinates for floor color detection
x1 = int(width//8)
x2 = int(width - width//8)
y1 = int(height - height//5)
y2 = int(height)

# Sets dimensions for the resized floor detect region
blurWidth = (x2-x1)//4
blurHeight = (y2-y1)//4

while True:

    ret, frame = cam.read()

    # Flips the frame to be the right orientation
    frame = cv2.flip(frame,1)

    # Returns the floor detection mask and the "average" floor color in BGR and HSV
    mask, floorColPix, floorpixHSV = floorMasker(frame, width, height)

    # Uncomment to draw rectangle around floor detect region
    cv2.rectangle(frame, (x1,y1), (x2,y2), (int(floorColPix[0]), int(floorColPix[1]), int(floorColPix[2])),3)

    # Display the captured frame
    cv2.imshow(windowTitle, frame)
    cv2.imshow("Floor Mask", mask)
    #cv2.imshow("V Blur Test", blurFrame)
    #cv2.imshow("Blur", blur)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) == ord('q'):
        break
