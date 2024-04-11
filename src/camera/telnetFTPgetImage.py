from telnetlib import Telnet
from ftplib import FTP
import cv2
from functools import wraps
from time import time
import numpy as np

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

    # show all file in cognex
    # files_list = ftp.dir()
    # print(files_list)
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


# TODO Rename this here and in `find_best_match`
def draw_image_with_rect(template, maxLoc, img):
    # Draw rectangle around the best match for template 1
    w1, h1 = template.shape[::-1]
    top_left1 = maxLoc
    bottom_right1 = (top_left1[0] + w1, top_left1[1] + h1)
    result = img.copy()
    cv2.rectangle(result, top_left1, bottom_right1, (0, 255, 0), 2)

    return result


if __name__ == "__main__":
    tn, ftp = camera_login()
    bigPin = cv2.imread(
        "C:\\Users\\Dune Admin\\winder_py2\\src\\camera\\bigPin.bmp",
        cv2.IMREAD_GRAYSCALE,
    )
    smallPin = cv2.imread(
        "C:\\Users\\Dune Admin\\winder_py2\\src\\camera\\smallPin.bmp",
        cv2.IMREAD_GRAYSCALE,
    )
    while True:
        user_input = input("enter c to capture\n")
        if user_input.lower() == "c":
            # capture a new image
            main_image = cv2.imread(
                "C:\\Users\\Dune Admin\\winder_py2\\src\\camera\\pins.bmp"
            )  # camera_capture(tn, ftp)

            # Find template in main image
            (
                result_image1,
                heatmap1,
                best_match_loc1,
                result_image2,
                heatmap2,
                best_match_loc2,
            ) = find_best_match(bigPin, smallPin, main_image)

            # Find the best match for both templates in the main image
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
