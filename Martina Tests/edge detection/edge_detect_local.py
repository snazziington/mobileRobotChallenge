# Canny edge detection on laptop webcam for local testing

import cv2

# Open the default camera
cam = cv2.VideoCapture(1)

# Get the default frame width and height
frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))


while True:
    ret, frame = cam.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)          # Turn grayscale
    blur = cv2.GaussianBlur(gray, (5, 5), 1.4)              # Removing noise -- increasing the last number increases blur
    edges = cv2.Canny(blur, threshold1=100, threshold2=200) # Apply Canny Edge Detector -- default is 100-200

    cv2.imshow("video", edges)    # OpenCV image show

    # Press 'q' to exit the loop
    if cv2.waitKey(1) == ord('q'):
        break

# Release the capture and writer objects
cam.release()
cv2.destroyAllWindows()