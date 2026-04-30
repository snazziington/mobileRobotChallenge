import cv2

cap = cv2.VideoCapture(0)

while True:
    ret, image = cap.read()
    if not ret:
        break

    # convert the image to grayscale format
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # apply binary thresholding
    ret, thresh = cv2.threshold(img_gray, 150, 255, cv2.THRESH_BINARY)
    # visualize the binary image
    cv2.imshow('Binary image', thresh)

    # detect the contours on the binary image using cv2.CHAIN_APPROX_NONE
    contours, hierarchy = cv2.findContours(image=thresh, mode=cv2.RETR_TREE,
                                           method=cv2.CHAIN_APPROX_NONE)
    # draw contours on the original image
    image_copy = image.copy()
    cv2.drawContours(image=image_copy, contours=contours, contourIdx=-1,
                     color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
    cv2.imshow('None approximation', image_copy)

    """
    Now let's try with `cv2.CHAIN_APPROX_SIMPLE`
    """
    # detect the contours on the binary image using cv2.CHAIN_APPROX_SIMPLE
    contours1, hierarchy1 = cv2.findContours(thresh, cv2.RETR_TREE,
                                             cv2.CHAIN_APPROX_SIMPLE)
    # draw contours on the original image for `CHAIN_APPROX_SIMPLE`
    image_copy1 = image.copy()
    cv2.drawContours(image_copy1, contours1, -1, (0, 255, 0), 2,
                     cv2.LINE_AA)
    cv2.imshow('Simple approximation', image_copy1)

    # visualize CHAIN_APPROX_SIMPLE points only
    image_copy2 = image.copy()
    for i, contour in enumerate(contours1):  # loop over one contour area
        for j, contour_point in enumerate(contour):  # loop over the points
            # draw a circle on the current contour coordinate
            cv2.circle(image_copy2, ((contour_point[0][0], contour_point[0][1])),
                       2, (0, 255, 0), 2, cv2.LINE_AA)
    cv2.imshow('CHAIN_APPROX_SIMPLE Point only', image_copy2)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
