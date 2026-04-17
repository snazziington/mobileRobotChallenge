import cv2
from ultralytics import YOLO

windowTitle = "YOLO Test"

cv2.namedWindow(windowTitle)
cam = cv2.VideoCapture(0)

model = YOLO('yolo26n-seg.pt')

while True:

    ret, frame = cam.read()

    frame = cv2.flip(frame,1)

    results = model(frame)

    # Display the captured frame
    cv2.imshow(windowTitle, frame)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) == ord('q'):
        break