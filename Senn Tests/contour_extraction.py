import cv2

"""
Contour detection and drawing using different extraction modes to complement
the understanding of hierarchies
"""

cap = cv2.VideoCapture(0)

while True:
    ret, image2 = cap.read()
    if not ret:
        break

    img_gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    ret, thresh2 = cv2.threshold(img_gray2, 150, 255, cv2.THRESH_BINARY)

    contours3, hierarchy3 = cv2.findContours(thresh2, cv2.RETR_LIST,
                                             cv2.CHAIN_APPROX_NONE)
    image_copy4 = image2.copy()
    cv2.drawContours(image_copy4, contours3, -1, (0, 255, 0), 2,
                     cv2.LINE_AA)
    cv2.imshow('LIST', image_copy4)

    contours4, hierarchy4 = cv2.findContours(thresh2, cv2.RETR_EXTERNAL,
                                             cv2.CHAIN_APPROX_NONE)
    image_copy5 = image2.copy()
    cv2.drawContours(image_copy5, contours4, -1, (0, 255, 0), 2,
                     cv2.LINE_AA)
    cv2.imshow('EXTERNAL', image_copy5)

    contours5, hierarchy5 = cv2.findContours(thresh2, cv2.RETR_CCOMP,
                                             cv2.CHAIN_APPROX_NONE)
    image_copy6 = image2.copy()
    cv2.drawContours(image_copy6, contours5, -1, (0, 255, 0), 2,
                     cv2.LINE_AA)
    cv2.imshow('CCOMP', image_copy6)

    contours6, hierarchy6 = cv2.findContours(thresh2, cv2.RETR_TREE,
                                             cv2.CHAIN_APPROX_NONE)
    image_copy7 = image2.copy()
    cv2.drawContours(image_copy7, contours6, -1, (0, 255, 0), 2,
                     cv2.LINE_AA)
    cv2.imshow('TREE', image_copy7)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
