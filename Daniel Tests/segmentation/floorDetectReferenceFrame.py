import cv2
import numpy as np

def floorMasker(refFrame, frame):

    width = frame.shape[1]
    height = frame.shape[0]

    #sets coordinates for floor color detection
    x1 = int(width//8)
    x2 = int(width - width//8)
    y1 = int(height - height//5)
    y2 = int(height)

    # Sets dimensions for the resized floor detect region
    blurWidth = (x2-x1)//4
    blurHeight = (y2-y1)//4

    # Creates the reference frame for floor detection
    floorReg = refFrame[y1:y2, x1:x2]
    floorReg = cv2.resize(floorReg, (blurWidth, blurHeight), interpolation=cv2.INTER_LINEAR)
    blur = cv2.blur(floorReg,(blurWidth,blurHeight))
    floorColLAB = cv2.cvtColor(blur, cv2.COLOR_BGR2LAB)
    floorColPix = blur[blurHeight//2, blurWidth//2]
    floorPixLAB = floorColLAB[blurHeight//2, blurWidth//2]

    # Splits the frame into its LAB components and blurs the Lightness component
    l,a,b = cv2.split(cv2.cvtColor(frame, cv2.COLOR_BGR2LAB))

    lblur = cv2.GaussianBlur(l, (25,25), 10)

    # Reconstructs the frame with the blurred Lightnass
    blurFrame = cv2.cvtColor(cv2.merge([lblur,a,b]), cv2.COLOR_LAB2BGR)

    # Sets the floor color detection bounds
    lowerFloor = np.array([min(40, int(floorPixLAB[0]-5)), int(floorPixLAB[1])-15, int(floorPixLAB[2])-15])
    upperFloor = np.array([max(253, int(floorPixLAB[0]+5)), int(floorPixLAB[1])+15, int(floorPixLAB[2])+15])

    # Creates an image mask based off of the frame with blurred Lightness
    mask = cv2.inRange(cv2.cvtColor(blurFrame, cv2.COLOR_BGR2LAB), lowerFloor, upperFloor)

    # Denoise a little with dilation and erosion to fill small gaps
    mask = cv2.dilate(mask, np.ones((5,5), np.uint8), iterations = 1)
    mask = cv2.erode(mask, np.ones((3,3), np.uint8), iterations = 2)
    mask = cv2.dilate(mask, np.ones((5,5), np.uint8), iterations = 3)
    mask = cv2.erode(mask, np.ones((3,3), np.uint8), iterations = 5)

    #cv2.imshow("L Blur Test", lthresh)

    return mask, floorColPix, floorPixLAB

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
y1 = int(height - height//5)
y2 = int(height)

ret, refFrame = cam.read()


while True:

    ret, frame = cam.read()

    # Flips the frame to be the right orientation
    frame = cv2.flip(frame,1)

    # Applies a slight blur to reduce noise
    frame = cv2.GaussianBlur(frame, (25,25), 8)

    # Returns the floor detection mask and the "average" floor color in BGR and LAB
    mask, floorColPix, floorpixLAB = floorMasker(refFrame, frame)

    # Uncomment to draw rectangle around floor detect region
    cv2.rectangle(frame, (x1,y1), (x2,y2), (int(floorColPix[0]), int(floorColPix[1]), int(floorColPix[2])),3)

    # Display the captured frame
    cv2.imshow(windowTitle, frame)
    cv2.imshow("Floor Mask", mask)
    
    #cv2.imshow("Blur", blur)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) == ord('q'):
        break
