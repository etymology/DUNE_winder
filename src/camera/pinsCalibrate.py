import cv2
import numpy as np
import os

# Function to detect circles and average spacing, with visualization
def detect_circles_and_average_spacing(img):
    """
    This function takes an image (an ndarray image as loaded by cv2)
    and looks for circles in it. Assuming the circles are colinear,
    it calculates the average distance between them in x. 
    """
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)

    # Apply thresholding to make the circles stand out
    _, thresh = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY)

    # Use the Hough transform to detect circles in the image
    circles = cv2.HoughCircles(thresh, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
                               param1=100, param2=30, minRadius=5, maxRadius=30)

    if circles is None:
        return "No circles detected."

    # Convert the circle parameters to integers
    circles = np.uint16(np.around(circles[0, :]))

    if len(circles) <= 1:
        return "Not enough circles to calculate spacing."
    # Sort circles based on the x-coordinate
    circles_sorted = circles[circles[:, 0].argsort()]
    # Calculate distances between consecutive circle centers
    distances = np.diff(circles_sorted[:, 0])
    return np.mean(distances)

# Path to the uploaded image
image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"pins.bmp")
img = cv2.imread(image_path, cv2.IMREAD_COLOR)
result = detect_circles_and_average_spacing(img)
pixels_per_mm = result/8

print(f"{pixels_per_mm} pixels per mm")
