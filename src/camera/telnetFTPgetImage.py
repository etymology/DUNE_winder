from telnetlib import Telnet
from ftplib import FTP
import cv2
from functools import wraps
from time import time
import numpy as np
import os

# cognex's config
CAMERA_IP_ADDRESS = "192.168.140.19"
CAMERA_USERNAME = "admin"
CAMERA_PASSWORD = ""


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print(f"func:{f.__name__} args:[{args}, {kw}] took: {(te-ts)*1000:.1f} msec")
        return result

    return wrap


@timing
def camera_login():
    # telnet login
    tn = Telnet(CAMERA_IP_ADDRESS)
    telnet_user = f"{CAMERA_USERNAME}\r\n"
    tn.write(telnet_user.encode("ascii"))  # the user name is admin
    tn.write(f"{CAMERA_PASSWORD}\r\n".encode("ascii"))
    print("Telnet Logged in")

    # ftp login
    ftp = FTP(CAMERA_IP_ADDRESS)
    ftp.login(CAMERA_USERNAME)
    print("FTP logged in")

    return tn, ftp


@timing
def camera_capture(tn: Telnet, ftp: FTP):
    # capture
    tn.write(b"SE8\r\n")
    # download file from cognex
    filename = "image.bmp"
    with open(filename, "wb") as data:
        ftp.retrbinary(f"RETR {filename}", data.write)
    return cv2.imread("image.bmp")


def find_best_match(template1, template2, img):
    # Convert images to grayscale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply template matching for the first template
    result1 = cv2.matchTemplate(gray_img, template1, cv2.TM_CCOEFF_NORMED)
    min_val1, max_val1, min_loc1, max_loc1 = cv2.minMaxLoc(result1)

    # Apply template matching for the second template
    result2 = cv2.matchTemplate(gray_img, template2, cv2.TM_CCOEFF_NORMED)
    min_val2, max_val2, min_loc2, max_loc2 = cv2.minMaxLoc(result2)

    img_with_rect1 = draw_image_with_rect(template1, max_loc1, img)
    img_with_rect2 = draw_image_with_rect(template2, max_loc2, img)
    # Generate heatmaps for both templates
    heatmap1 = cv2.applyColorMap(np.uint8(255 * result1), cv2.COLORMAP_JET)
    heatmap2 = cv2.applyColorMap(np.uint8(255 * result2), cv2.COLORMAP_JET)

    return img_with_rect1, heatmap1, max_loc1, img_with_rect2, heatmap2, max_loc2


def draw_image_with_rect(template, maxLoc, img):
    # Draw rectangle around the best match for template 1
    w1, h1 = template.shape[::-1]
    top_left1 = maxLoc
    bottom_right1 = (top_left1[0] + w1, top_left1[1] + h1)
    result = img.copy()
    cv2.rectangle(result, top_left1, bottom_right1, (0, 255, 0), 2)

    return result

def detect_circles_and_average_spacing(img):
    # Step 1: Load the image
    # img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    # if img is None:
    #     return "Image could not be loaded. Please check the path."

    # Step 2: Convert to grayscale and apply Gaussian blur
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)

    # Step 3: Detect circles using the Hough transform
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=20,
                               param1=50, param2=30, minRadius=0, maxRadius=0)

    if circles is None:
        return "No circles detected."

    # Step 4: Ensure the circles array is in the correct shape and sort by x-coordinate
    circles = np.uint16(np.around(circles[0, :]))
    circles_sorted = circles[circles[:, 0].argsort()]  # Sort circles based on the x-coordinate

    if len(circles_sorted) <= 1:
        return "Not enough circles to calculate spacing."
    # Calculate distances between consecutive circle centers
    distances = np.diff(circles_sorted[:, 0])
    return np.mean(distances)

# Function calls are commented out to prevent execution here




if __name__ == "__main__":
    tn, ftp = camera_login()
    bigPin = cv2.imread(
        os.path.join(os.path.dirname(os.path.realpath(__file__)),"bigPin.bmp"),
        cv2.IMREAD_GRAYSCALE,
    )
    smallPin = cv2.imread(
        os.path.join(os.path.dirname(os.path.realpath(__file__)),"smallPin.bmp"),
        cv2.IMREAD_GRAYSCALE,
    )
    # result = detect_circles_and_average_spacing('path_to_your_image.jpg')
    # print(result)
    while True:
        user_input = input("enter c to capture\n")
        if user_input.lower() == "c":
            # capture a new image
            main_image = cv2.imread(os.path.join(os.path.dirname(os.path.realpath(__file__)),"bigPin.bmp")
            )  # camera_capture(tn, ftp)
            detect_circles_and_average_spacing(main_image)
            # Find template in main image
            (
                result_image1,
                heatmap1,
                best_match_loc1,
                result_image2,
                heatmap2,
                best_match_loc2,
            ) = find_best_match(bigPin, smallPin, main_image)

            # Display results
            cv2.imshow("big pin Match", result_image1)
            cv2.imshow("big pin Heatmap", heatmap1)
            print("Best match location for big pin:", best_match_loc1)

            cv2.imshow("small pin Match", result_image2)
            cv2.imshow("small pin Heatmap", heatmap2)
            print("Best match location for small pin:", best_match_loc2)

            cv2.waitKey(0)
            cv2.destroyAllWindows()
