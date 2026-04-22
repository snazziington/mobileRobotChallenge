# Canny edge bottom screen distance detection on laptop webcam for local testing
# Using a cropped frame from the full image, assuming that the object is in the middle and bottom half

import cv2
import numpy as np

# Open the default camera
cam = cv2.VideoCapture(1)

# Get the default frame width and height
frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))

# Define area we expect the object to be within
x_start, y_start, x_end, y_end = 450, 500, 1500, 1079
cropped_height = y_end - y_start

while True:
    ret, frame = cam.read()
    out.write(frame) # Write the frame to the output file
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)          # Turn grayscale
    blur = cv2.GaussianBlur(gray, (5, 5), 1.4)                # Removing noise -- increasing last number increases blur
    edges = cv2.Canny(blur, threshold1=100, threshold2=200) # Apply Canny Edge Detector -- default is 100-200
 
    cropped = edges[y_start:y_end, x_start:x_end] # Crop the image using slicing
    coords = np.argwhere(cropped > 250) # Search for near-white values

    if coords.shape[0] > 0:
        x_positions = coords[:, 1]
        y_positions = coords[:, 0]
        lowest = cropped_height-np.max(y_positions) # because y=0 is on top
        print(lowest)

        # Drawing a grey dotted line on right to indicate if it detects an edge and maps on y-axis
        for y, x in coords:
            cv2.circle(cropped, (x, y), 15, 128, -1)

    cv2.imshow("video", edges)    # OpenCV image show

    # Press 'q' to exit the loop
    if cv2.waitKey(1) == ord('q'):
        break

# Release the capture and writer objects
cam.release()
out.release()
cv2.destroyAllWindows()