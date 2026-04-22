# Canny operator on static image

import cv2
 
# Load image in grayscale
img = cv2.imread("test_img.png", cv2.IMREAD_GRAYSCALE)
 
# Apply Gaussian Blur to reduce noise -- increasing the last number increases blur
blur = cv2.GaussianBlur(img, (5, 5), 1.4)
 
# Apply Canny Edge Detector -- default is 100-200
edges = cv2.Canny(blur, threshold1=400, threshold2=500)
 
# Display result
cv2.imshow("Canny Edge Detection", edges)
 
cv2.waitKey(0)
cv2.destroyAllWindows()