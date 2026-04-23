# Canny edge detection on laptop webcam for local testing

import cv2

# Open the default camera
cam = cv2.VideoCapture(1)

# Get the default frame width and height
frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))


while True:
    ret, frame = cam.read()
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)          # Turn grayscale
    blur = cv2.GaussianBlur(frame, (5, 5), 5)                # Removing noise -- increasing the last number increases blur
    edges_blur = cv2.Canny(blur, threshold1=100, threshold2=200) # Apply Canny Edge Detector -- default is 100-200
    edges_no_blur = cv2.Canny(frame, threshold1=100, threshold2=200) # Apply Canny Edge Detector -- default is 100-200
    edges_no_blurred = cv2.GaussianBlur(edges_no_blur, (5, 5), 5)

    cv2.imshow("frame", frame)    # OpenCV image show
    cv2.imshow("blur", blur)    # OpenCV image show
    cv2.imshow("edges_blur", edges_blur)    # OpenCV image show
    cv2.imshow("edges_no_blur", edges_no_blur)    # OpenCV image show
    cv2.imshow("edges_no_blur_blurred", edges_no_blurred)    # OpenCV image show

    # Press 'q' to exit the loop
    if cv2.waitKey(1) == ord('q'):
        break

# Release the capture and writer objects
cam.release()
cv2.destroyAllWindows()