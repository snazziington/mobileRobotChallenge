import picar_4wd as fc
import cv2
import numpy as np
from picamera2 import Picamera2
import math

# ==Colours==
white = (255, 255, 255)
magenta = (255, 0, 255)
blue = (255, 0, 0)

# ==Camera properties==
width = 640
height = 480
blurSize = 0
blurArea = (15, 15)

# ==Camera Properties; resized dimensions, horizon, center of floor==
resizeFactor = 4 # Camera resolution is divided by this number
width = int(width / resizeFactor); height = int(height / resizeFactor)
resizedDimensions = (width, height)
horizon = int(height * 0.4)

# A list containing the coordinates of the center of the floor
centerFloor = [int(width / 2), int(horizon * 1.5)]

# ==Threshold for difference mask==
# Difference threshold value; decrease in rooms with warm lighting
threshold_diff_value = 50

# ==Toggles==
object_identified = False # Becomes true once the object has been identified

# ==Object Tracking==
# How quickly the position and size of the object moves towards the target (0 < speed =< 1)
speed_position = 0.5
speed_size = 0.3

# ==Robot Movement==
object_held_distance = 350 # Distance to maintain from object
object_distance_margin = 50 # Margin for object distance
object_angle_margin = 30 # Margin for angle

# centerXO and centerYO are the center coordinates of the object; that is what the robot follows
def robot_movement(centerXO, centerYO, object_held_distance):
        # Object Distance Calculations
        horizontal_distance_object = width / 2 - centerXO
        vertical_distance_object = height - centerYO
        pixel_distance_to_object = math.sqrt(horizontal_distance_object ** 2 + vertical_distance_object ** 2)
        object_angle = int(math.degrees(math.asin(horizontal_distance_object / pixel_distance_to_object))  ) 

        # Exponential ratio for pixel distance
        ratio = 1.5
        distance_to_object = pixel_distance_to_object ** ratio
        difference_in_distance = distance_to_object - object_held_distance

        # Defining turning speed; relative to angle magnitude
        turning_speed = min(80, np.interp(abs(object_angle), [30, 50], [1, 15]))
        
        # Defining forward speed; relative to difference in distance
        forward_speed = min(120, abs(difference_in_distance / 1.2))

        # Robot Movement
        if difference_in_distance < -(object_distance_margin): 
            print("Move backwards")
            fc.backward(forward_speed)
        
        elif object_angle < -(object_angle_margin):
            fc.turn_left(turning_speed)
            print("Turn left")

        elif object_angle > object_angle_margin:
            fc.turn_right(turning_speed)
            print("Turn right")

        elif difference_in_distance > object_distance_margin: 
            print("Move forward")
            fc.forward(forward_speed)

        else: 
            print("Object distance is perfect!")
            fc.stop()

# Initialises target values of object to be center of the floor
xT = 180; yT = 160; wT = 50; hT = 50

# Margin values for the colour once detected
colour_lightness_diff = 40
colour_hue_diff = 6

def color_detect(img, color):
    # Convert from BGR to LAB
    colLAB = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

    mask = cv2.inRange(colLAB, np.array([color[0] - colour_lightness_diff, color[1] - colour_hue_diff, color[2] - colour_hue_diff]), np.array([color[0] + colour_lightness_diff, color[1] + colour_hue_diff, color[2] + colour_hue_diff]))           # inRange()：Make the ones between lower/upper white, and the rest black

    # Find the contour in mask, and the contours are arranged according to the area from small to large.
    _tuple = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)      
    
    if len(_tuple) == 3:
        _, contours, hierarchy = _tuple
    else:
        contours, hierarchy = _tuple
    
    color_area_num = len(contours) # Count the number of contours

    if color_area_num > 0: 
        for i in contours:    # Traverse all contours
            x, y, w, h = cv2.boundingRect(i)      # Decompose the contour into the coordinates of the upper left corner and the width and height of the recognition object

            # Draw a rectangle on the image (picture, upper left corner coordinate, lower right corner coordinate, color, line width)
            cv2.rectangle(img, (x, y), (x+ w, y+ h), (0, 255, 0), 2)  # Draw a rectangular frame

    # Return a mask of all objects coloured similarly to the object
    return mask

with Picamera2() as camera:
    camera.preview_configuration.main.size = (640, 480)
    camera.preview_configuration.main.format = "RGB888"
    camera.preview_configuration.align()
    camera.configure("preview")
    camera.start()

    # Captures the first background image
    background_initial = camera.capture_array()
    background_initial = cv2.flip(background_initial, 1)

    # Blurs + resizes background image
    background_initial = cv2.resize(background_initial, resizedDimensions, interpolation=cv2.INTER_LINEAR)
    background_initial = cv2.GaussianBlur(background_initial, (5, 5), 5) 

    while True: # Runs until key is pressed to close
        # Initialise current view; will outline the object
        frame_current = camera.capture_array()
        frame_current = cv2.flip(frame_current, 1)
        frame_current = cv2.resize(frame_current, resizedDimensions, interpolation=cv2.INTER_LINEAR)
        frame_current = cv2.GaussianBlur(frame_current, blurArea, blurSize)
               
        # Initialise secondary capture; will show the object tracking reticle once the object is found
        frame = camera.capture_array()
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, resizedDimensions, interpolation=cv2.INTER_LINEAR)
        frame = cv2.GaussianBlur(frame, blurArea, blurSize)

        # If "O" key is pressed in the cv2 view
        if cv2.waitKey(1) == ord('o'):
            # Saves an image of the view so the contour of the new objects can be found
            if object_identified == False:
                snapshot_diff = camera.capture_array()
                snapshot_diff = cv2.flip(snapshot_diff, 1)
                snapshot_diff = cv2.resize(snapshot_diff, resizedDimensions, interpolation=cv2.INTER_LINEAR)
                snapshot_diff = cv2.GaussianBlur(snapshot_diff, blurArea, blurSize)
                print("'O' key pressed. Detecting objects in the current snapshot...")
            
            # Compares difference between initial background photo and current view, 
            # then apply greyscale and apply binary filter (based on threshold value)
            difference = cv2.absdiff(background_initial, snapshot_diff)
            #cv2.imshow("difference", difference)
            difference_greyscale = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)
            _, difference_mask = cv2.threshold(difference_greyscale, threshold_diff_value, 255, cv2.THRESH_BINARY)
            #cv2.imshow("difference_mask", difference_mask)

            # ==DIFFERENCE==
            # Erosion and dilation removes noise and thin foreground elements in mask
            difference_mask = cv2.erode(difference_mask, np.ones((2, 2), np.uint8), iterations = 2)
            difference_mask = cv2.dilate(difference_mask, np.ones((4, 4), np.uint8), iterations = 2)
            #cv2.imshow("difference_mask_processed", difference_mask)

            # Find contours from the resultant mask
            contours, hierarchy = cv2.findContours(difference_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # Count the number of contours in the mask
            color_area_num = len(contours)
            
            if color_area_num > 0:
                # If at least one contour was found, then one of them must be the object.
                print("An object has been found!")

                # Initialises default distance from object to centre of horizon
                lowestDis = 1000000

                for i in contours:
                    # For each contour, make a bounding box
                    # # x, y are the top left coords, w, h are the width and height
                    x, y, w, h = cv2.boundingRect(i)
                    print("Coords of new objects:", x, y, w, h)
                    # Center pixels of the contour
                    centerX = x + int((w / 2))
                    centerY = y + int((h / 2))

                    # If the contour's vertical center is on the floor (below the horizon)...
                    if centerY > horizon:
                        # Calculate its distance to the center of the floor
                        centerDis = (abs(centerFloor[0] - centerX) + abs(centerFloor[1] - centerY))
                        
                        # The contour nearest to the center of the floor is the object
                        # Save its coordinates in the following variables
                        if (centerDis < lowestDis):
                            lowestDis = centerDis
                            # The coordinates of the "object" are saved into these variables
                            global xO; global yO; global wO; global hO
                            xO = x; yO = y; wO = w; hO = h

                            # Calculate center of the object
                            centerXO = xO + wO // 2
                            centerYO = yO + hO // 2

                            object_identified = True # An object has been found, so this is now True

                            # Creates a mask of the object
                            masked = cv2.bitwise_and(snapshot_diff, snapshot_diff, mask = difference_mask)

                            # Crops the image of the object, blurs it, and changes colourspace to LAB
                            objCrop = masked[y:y + h, x:x + w]
                            objCrop = cv2.blur(objCrop, (w, h))
                            #cv2.imshow("Crop", objCrop)
                            objCrop = cv2.cvtColor(objCrop, cv2.COLOR_BGR2LAB)

                            objCol = objCrop[h//2, w//2]
                            # Prints detected object colour
                            print(objCol)

            else:
                print("No object found, please try again.")             
        
        # Tracks Object
        if object_identified == True:
            # Returns a mask containing all pixels coloured similarly to the object
            colorMask = color_detect(frame, objCol)

            # Dilates the mask to ensure each object is contained in one contour and not several
            colorMask = cv2.dilate(colorMask, np.ones((4, 4), np.uint8), iterations = 8)
            #cv2.imshow("Color Mask", colorMask)    # OpenCV image show
        
            # Finds contours of the objects
            colorContours, hierarchy = cv2.findContours(colorMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            filter_contours = [] 

            # Count the number of contours in the mask
            color_area_num = len(colorContours)

            # Initialises default distance from contours to known centre of object
            lowestDis = 1000000

            if color_area_num > 0:
                for i in colorContours:
                    # x, y are the top left coords, w, h are the width and height (of the contour)
                    x, y, w, h = cv2.boundingRect(i)

                    # Center pixels of the contour
                    centerX = x + int((w / 2))
                    centerY = y + int((h / 2))

                    if centerY > horizon:
                        # Calculate distance from contour to known center of object
                        centerDis = (abs(centerXO - centerX) + abs(centerYO - centerY))

                        # The contour nearest to the last known location of the object must be the object
                        # Save the contour's coordinates into the target variables
                        if (centerDis < lowestDis):
                            lowestDis = centerDis
                            # These are the target values for the object
                            xT = x; yT = y; wT = w; hT = h

                            # For the user's reference, add all the contours of eligible objects to this list
                            filter_contours.append(i)

                # Draw the contours of objects below the horizon onto the frame
                cv2.drawContours(frame, filter_contours, -1, blue, 7)
                
                # Create a black image the size of the camera and convert it to grey colourspace
                filter_contour_mask = np.zeros(frame.shape, np.uint8)
                filter_contour_mask = cv2.cvtColor(filter_contour_mask, cv2.COLOR_BGR2GRAY)

                # Create a mask of all the filtered contours
                cv2.drawContours(filter_contour_mask, filter_contours, -1, white, -1) ####
                mask_frame = cv2.bitwise_and(frame, frame, mask = filter_contour_mask)

                # Once the object's new position has been found, the properties of the object
                # gradually move towards those new properties
                xO = int(xO + (xT - xO) * speed_position)
                yO = int(yO + (yT - yO) * speed_position)
                wO = int(wO + (wT - wO) * speed_size)
                hO = int(hO + (hT - hO) * speed_size)

                # Updates center of the object
                centerXO = xO + int((wO / 2))
                centerYO = yO + int((hO / 2))
                
            # Draw small pink circle on the center of object;
            # This is the object tracker the robot is following
            cv2.circle(frame_current, (centerXO, centerYO), 10, magenta, -1)
            
            # The robot moves as needed
            robot_movement(centerXO, centerYO, object_held_distance)

        # Places a line at the horizon so the user knows where the robot is looking for objects
        cv2.line(frame, (0, horizon), (width, horizon), blue, 1)
        
        cv2.imshow("mask_frame", frame) # Shows colour mask outlines
        cv2.imshow("frame_current", frame_current) # Shows current frame with dot on object

        # Press 'q' to exit the loop
        if cv2.waitKey(1) == ord('q'):
            fc.stop()
            break