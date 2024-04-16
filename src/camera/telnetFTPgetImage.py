from telnetlib import Telnet
from ftplib import FTP
import cv2
from functools import wraps
from time import time, sleep
import numpy as np
import os
import glob
import math
from queue import Queue

# cognex's config
CAMERA_IP_ADDRESS = "192.168.140.19"
CAMERA_USERNAME = "admin"
CAMERA_PASSWORD = ""
TEMPLATE_DIRECTORY = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "templates"
)
PIN_SPACING = 8  # mm

pixels_per_mm: float


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


# This queue will hold the images for display
image_queue = Queue()


def fetch_images(tn: Telnet, ftp: FTP):
    while True:
        # Capture command
        tn.write(b"SE8\r\n")
        filename = "image.bmp"

        # Fetch the image via FTP
        with open(filename, "wb") as data:
            ftp.retrbinary(f"RETR {filename}", data.write)

        # Read the image into OpenCV
        img = cv2.imread(filename)
        if img is not None:
            image_queue.put(img)

        # Sleep a bit to control the capture rate
        sleep(0.01)  # Adjust as needed for your camera's capture rate


def display_images():
    cv2.namedWindow("Camera Stream")
    while True:
        if not image_queue.empty():
            image = image_queue.get()
            cv2.imshow("Camera Stream", image)
            if cv2.waitKey(1) == ord("q"):  # Press 'q' to quit the display
                break
    cv2.destroyAllWindows()


def find_best_matches(img, templates):
    # Convert image to grayscale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Calculate the center of the image
    img_center_x, img_center_y = img.shape[1] // 2, img.shape[0] // 2

    results = []
    for template in templates:
        # Apply template matching
        result = cv2.matchTemplate(gray_img, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # Draw rectangle on the matching area
        img_with_rect = img.copy()
        top_left = max_loc
        bottom_right = (
            top_left[0] + template.shape[1],
            top_left[1] + template.shape[0],
        )

        # Calculate the center of the template match
        match_center_x = top_left[0] + template.shape[1] // 2
        match_center_y = top_left[1] + template.shape[0] // 2

        # Calculate offsets
        offset_x = img_center_x - match_center_x  # Left is positive
        offset_y = img_center_y - match_center_y  # Up is positive

        # Draw rectangle and crosshairs at the center
        cv2.rectangle(img_with_rect, top_left, bottom_right, (255, 0, 0), 2)
        cv2.line(
            img_with_rect,
            (match_center_x, match_center_y - 10),
            (match_center_x, match_center_y + 10),
            (0, 255, 0),
            2,
        )
        cv2.line(
            img_with_rect,
            (match_center_x - 10, match_center_y),
            (match_center_x + 10, match_center_y),
            (0, 255, 0),
            2,
        )

        # Generate heatmap
        heatmap = cv2.applyColorMap(np.uint8(255 * result), cv2.COLORMAP_JET)

        # Append results
        results.append(
            {
                "image_with_rectangle": img_with_rect,
                "heatmap": heatmap,
                "max_value": max_val,
                "max_location": max_loc,
                "offset_x": offset_x,
                "offset_y": offset_y,
            }
        )

    return results


def display_all_results(results, img_size=(480, 640)):
    if not results:
        print("No results to display.")
        return

    # Calculate the grid size for images and heatmaps
    num_results = len(results)
    grid_size = math.ceil(math.sqrt(num_results))

    # Set the standard size for images and heatmaps
    standard_height, standard_width = img_size

    # Create a large canvas to fit all images in a grid
    canvas_height = standard_height * grid_size
    canvas_width = (
        standard_width * grid_size * 2
    )  # x2 for image and heatmap side by side
    canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)

    for i, result in enumerate(results):
        row = i // grid_size
        col = i % grid_size

        # Calculate start position for each image and heatmap
        start_y = row * standard_height
        start_x_img = col * standard_width * 2
        start_x_heatmap = start_x_img + standard_width

        # Resize image with rectangle and heatmap
        resized_img = cv2.resize(
            result["image_with_rectangle"], (standard_width, standard_height)
        )
        resized_heatmap = cv2.resize(
            result["heatmap"], (standard_width, standard_height)
        )

        # Place resized image and heatmap in the canvas
        canvas[
            start_y : start_y + standard_height,
            start_x_img : start_x_img + standard_width,
        ] = resized_img
        canvas[
            start_y : start_y + standard_height,
            start_x_heatmap : start_x_heatmap + standard_width,
        ] = resized_heatmap

        # Draw center crosshair for image and heatmap
        center_x_img = start_x_img + standard_width // 2
        center_y = start_y + standard_height // 2
        center_x_heatmap = start_x_heatmap + standard_width // 2

        # Crosshair for the image
        cv2.line(
            canvas,
            (center_x_img, center_y - 10),
            (center_x_img, center_y + 10),
            (0, 255, 0),
            2,
        )
        cv2.line(
            canvas,
            (center_x_img - 10, center_y),
            (center_x_img + 10, center_y),
            (0, 255, 0),
            2,
        )

        # Crosshair for the heatmap
        cv2.line(
            canvas,
            (center_x_heatmap, center_y - 10),
            (center_x_heatmap, center_y + 10),
            (255, 0, 0),
            2,
        )
        cv2.line(
            canvas,
            (center_x_heatmap - 10, center_y),
            (center_x_heatmap + 10, center_y),
            (255, 0, 0),
            2,
        )

    # Display the full canvas
    cv2.imshow("Results Grid", canvas)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def draw_image_with_rect(template, maxLoc, img):
    # Draw rectangle around the best match for template 1
    w1, h1 = template.shape[::-1]
    top_left1 = maxLoc
    bottom_right1 = (top_left1[0] + w1, top_left1[1] + h1)
    result = img.copy()
    cv2.rectangle(result, top_left1, bottom_right1, (0, 255, 0), 2)

    return result


def preprocess_image_and_detect_circles(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=20,
        param1=50,
        param2=30,
        minRadius=5,
        maxRadius=20,
    )
    if circles is not None:
        circles = np.uint16(np.around(circles[0, :]))
    return circles


def display_circles(img, circles):
    img_with_circles = img.copy()
    for x, y, r in circles:
        cv2.circle(img_with_circles, (x, y), r, (0, 255, 0), 2)
        cv2.circle(img_with_circles, (x, y), 2, (0, 0, 255), 3)
    cv2.imshow("Circles Detected", img_with_circles)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def detect_circles_and_average_spacing(img, display=False):
    circles = preprocess_image_and_detect_circles(img)
    if circles is None:
        return "No circles detected."
    circles_sorted = circles[circles[:, 0].argsort()]
    if display:
        display_circles(img, circles_sorted)
    if len(circles_sorted) <= 1:
        return "Not enough circles to calculate spacing."
    distances = np.sqrt(np.sum(np.diff(circles_sorted[:, :2], axis=0) ** 2, axis=1))
    return np.mean(distances)


def find_closest_circles(img, num_circles: int, display=False):
    global pixels_per_mm
    """
    Find the specified number of circles closest to the center of the image and their displacement from the center.
    """
    circles = preprocess_image_and_detect_circles(img)
    if circles is None:
        return "No circles detected."

    img_center = np.array([img.shape[1] // 2, img.shape[0] // 2])
    distances_to_center = np.sqrt(np.sum((circles[:, :2] - img_center) ** 2, axis=1))
    closest_indices = np.argsort(distances_to_center)[:num_circles]
    closest_circles = circles[closest_indices]

    if display:
        display_circles(img, closest_circles)

    displacements = (closest_circles[:, :2] - img_center) / pixels_per_mm
    return displacements.tolist()


def manual_find_center_distance(image):
    img = image.copy()
    points = []

    def click_event(event, x, y, flags, params):
        # On left mouse click, record the point and draw it on the image
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            cv2.circle(params, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow("Image", params)
            if len(points) > 1:
                # Draw lines between consecutive points
                cv2.line(params, points[-2], points[-1], (255, 0, 0), 2)
                cv2.imshow("Image", params)

    cv2.imshow("Image", img)
    cv2.setMouseCallback("Image", click_event, img)

    # Wait until a key is pressed
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    if len(points) < 2:
        return "Not enough points to calculate distances."

    # Calculate distances between consecutive points
    distances = np.diff(points, axis=0)
    mean_x_distance = np.mean(distances[:, 0])
    mean_y_distance = np.mean(distances[:, 1])

    return math.sqrt(mean_x_distance**2 + mean_y_distance**2)


def load_templates(directory):
    templates = []
    for filepath in glob.glob(os.path.join(directory, "*.bmp")):
        template = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
        if template is not None:
            templates.append(template)
        else:
            print(f"Failed to load:{filepath}")
    return templates


if __name__ == "__main__":
    tn, ftp = camera_login()
    # # Start the image fetching thread
    # fetch_thread = threading.Thread(target=fetch_images, args=(tn, ftp))
    # fetch_thread.daemon = True
    # fetch_thread.start()

    # # Start the display on the main thread
    # display_images()

    # # Wait for the fetch thread to finish (it won't if you're continuously capturing)
    # fetch_thread.join()
    templates = load_templates(TEMPLATE_DIRECTORY)
    main_image = camera_capture(tn, ftp)

    pixels_per_mm = detect_circles_and_average_spacing(main_image) / PIN_SPACING
    print(f"{pixels_per_mm} pixels/mm")

    while True:
        user_input = input("enter c to capture\n")
        if user_input.lower() == "c":
            main_image = camera_capture(tn, ftp)

            cv2.imwrite("/src/camera/pins.bmp", main_image)
            circles = find_closest_circles(main_image, 2)
            print(circles)
            # results = find_best_matches(main_image, templates)
            # best_match = max(results, key=lambda x: x["max_value"])
            # print(
            #     f"Offsets: x={best_match['offset_x']/pixels_per_mm}, y={best_match['offset_y']/pixels_per_mm}"
            # )
            # display_all_results([best_match])
