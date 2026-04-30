"""
This Python script shows why we need to convert the image to grayscale
and why other single channel values like R, G, and B, do not work well for
contour detection.
"""

import cv2

cap = cv2.VideoCapture(0)

while True:
    ret, image = cap.read()
    if not ret:
        break

    # B, G, R channel splitting
    blue, green, red = cv2.split(image)

    # detect contours using blue channel and without thresholding
    contours1, hierarchy1 = cv2.findContours(image=blue, mode=cv2.RETR_TREE,
                                             method=cv2.CHAIN_APPROX_NONE)

    # draw contours on the original image
    image_contour_blue = image.copy()
    cv2.drawContours(image=image_contour_blue, contours=contours1, contourIdx=-1,
                     color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
    cv2.imshow('Contour detection using blue channels only', image_contour_blue)

    # detect contours using green channel and without thresholding
    contours2, hierarchy2 = cv2.findContours(image=green, mode=cv2.RETR_TREE,
                                             method=cv2.CHAIN_APPROX_NONE)
    image_contour_green = image.copy()
    cv2.drawContours(image=image_contour_green, contours=contours2, contourIdx=-1,
                     color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
    cv2.imshow('Contour detection using green channels only', image_contour_green)

    # detect contours using red channel and without thresholding
    contours3, hierarchy3 = cv2.findContours(image=red, mode=cv2.RETR_TREE,
                                             method=cv2.CHAIN_APPROX_NONE)
    image_contour_red = image.copy()
    cv2.drawContours(image=image_contour_red, contours=contours3, contourIdx=-1,
                     color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
    cv2.imshow('Contour detection using red channels only', image_contour_red)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
