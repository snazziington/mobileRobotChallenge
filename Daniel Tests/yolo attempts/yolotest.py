import cv2
from ultralytics import YOLO

windowTitle = "YOLO Test"

cv2.namedWindow(windowTitle)
cam = cv2.VideoCapture(0)
cam.set( cv2.CAP_PROP_FRAME_WIDTH, 320)
cam.set( cv2.CAP_PROP_FRAME_HEIGHT, 240)

model = YOLO('yolo26n.pt')

while True:

    ret, frame = cam.read()

    frame = cv2.flip(frame,1)

    results = model.track(frame)

    for obj in results:
        xyxy = obj.boxes.xyxy  # Bounding box coordinates

    print(f"Coordinates: {xyxy}")

    # Visualize the results on the frame
    annotated_frame = results[0].plot()

    # Display the captured frame
    cv2.imshow(windowTitle, annotated_frame)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) == ord('q'):
        break
