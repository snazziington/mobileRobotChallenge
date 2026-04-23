import cv2
import time
import numpy as np

# Open the default camera
cam = cv2.VideoCapture(1)

# Get the default frame width and height
frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

#sets coordinates for floor color detection
x1 = int(frame_width//8)
x2 = int(frame_width - frame_width//8)
y1 = int(frame_height - frame_height//5)
y2 = int(frame_height)

# Sets dimensions for the resized floor detect region
blurSize = 1
blurWidth = (x2 - x1) // blurSize
blurHeight = (y2 - y1) // blurSize

# I want to draw rectangles around all the different coloured objects in the scene
    # How do I do this?
        # Have mask of new objects in scene
            # Draw outline of those things
            # Might have to blur the image significantly + decrease camera res
        # Use edge detection to draw a rectangle around all new objects
        # Within each object, also get the different colours + print colour to screen
        # Then use edge maybe, so I have an outline of the different colours
        # And then for each colour block, treat the edges as the outline? (idk if possible)

    # Could also have every new object be outlined/contoured
    # And then the smallest one in the centre-most position is highlighted as the object

# After 10 seconds, the object which is in the centre most position is highlighted again
    # Need centre pos?
# Which also moves the least, is selected as "object"
# Then, print out the hsv value of the object, and remove all other rectangles in the scene

def floorMasker(frame, width, height):
    # Creates the frame for floor detection
    floorReg = frame[y1:y2, x1:x2] # floor frame specifically
    floorReg = cv2.resize(floorReg, (blurWidth, blurHeight), interpolation=cv2.INTER_LINEAR)
    blur = cv2.blur(floorReg,(blurWidth, blurHeight))
    #blur = cv2.GaussianBlur(frame, (5, 5), 5)
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

start_time = int(time.time())
interval = 5
analysedScene = False
print("Analysing scene...")

while True:
    current_time = int(time.time())
    # Read camera data
    ret, frame = cam.read()

    # Apply blur to remove noise -- increasing last number increases blur
    blur = cv2.GaussianBlur(frame, (5, 5), 5)              # Removing noise -- increasing the last number increases blur

    # Returns the floor detection mask and the "average" floor color in BGR and HSV
    mask, floorColPix, floorpixHSV = floorMasker(frame, frame_width, frame_height)

    # Uncomment to draw rectangle around floor detect region
    cv2.rectangle(frame, (x1,y1), (x2,y2), (int(floorColPix[0]), int(floorColPix[1]), int(floorColPix[2])),3)

    # Display the captured frame
    cv2.imshow("frame w/ colour rect", frame)
    cv2.imshow("blur", blur)
    cv2.imshow("Floor Mask", mask)

    # After 10 seconds, print ("Scene Analysed")
    if ((start_time + interval) < current_time and analysedScene == False):
        print(start_time + interval, current_time)
        analysedScene = True

    # Press 'q' to exit the loop
    if cv2.waitKey(1) == ord('q'):
        break

# Release the capture and writer objects
cam.release()
cv2.destroyAllWindows()