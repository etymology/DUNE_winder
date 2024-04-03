###############################################################################
# Name: Settings.py
# Uses: Structure for constant settings used in various systems.
# Date: 2016-02-11
# Author(s):
#   Andrew Que <aque@bb7.com>
#   Benjamin Oye <oye@uchicago.edu> [port to python3, Jan 2024]
###############################################################################
import os


class Settings:

    SERVER_PORT = 6626  # Default TCP port number (plank's constant).
    WEB_SERVER_PORT = 80    # Port for web server (80 is default).
    # Max data that can be read from server at once.
    SERVER_MAX_DATA_SIZE = 1024
    SERVER_BACK_LOG = 5     # Default recommended by Python manual.
    # Max data that can be read from client at once.
    CLIENT_MAX_DATA_SIZE = 1024
    IO_UPDATE_TIME = 0.1   # In seconds.  Currently 10 times/sec.

    # Path to configuration file.
    CONFIG_FILE = "../configuration.xml"

    # Path and name of version information file.
    VERSION_FILE = "version.xml"

    # Check the operating system
    if os.name == 'posix':  # posix is used for Linux and macOS
        # Linux-specific code
        print("Running on Linux")
        UI_VERSION_FILE = "/WebUI/version.xml"
        WEB_DIRECTORY = "/home/ben/DUNE/DUNE_winder/src/winder/WebUI"

    elif os.name == 'nt':  # nt is used for Windows
        # Windows-specific code
        print("Running on Windows")
        UI_VERSION_FILE = "C:/Users/Dune Admin/winder_py3/src/winder/WebUI/version.xml"
        WEB_DIRECTORY = "C:/Users/Dune Admin/winder_py3/src/winder/WebUI"

    else:
        # Code for other operating systems
        print("Operating system not recognized")
        # Add code for other operating systems here if needed

    G_CODE_LOG_FILE = "_gCode.gc"

    IO_LOG = "../Data/IO_log.csv"

    MACHINE_CALIBRATION_FILE = "machineCalibration.xml"

    # File making up the version for the control software.
    CONTROL_FILES = ".*\.py$"

    # File making up the version for the user interface.
    UI_FILES = ".*\.html$|.*\.css$|.*\.js$"

    # ---------------------------------------------------------------------
    @staticmethod
    def defaultConfig(configuration):
        """
        Setup default values for configuration.
        """
        configuration.default("plcAddress", "192.168.140.13")

        # Location of camera's last captured image.
        configuration.default(
            "cameraURL", "ftp://admin@192.168.140.19/image.bmp")
        configuration.default("pixelsPer_mm", 18)

        # Default for GUI server.
        configuration.default("serverAddress", "127.0.0.1")
        configuration.default("serverPort", Settings.SERVER_PORT)

        # Default for GUI server.
        configuration.default("webServerPort", 80)

        # Log file locations.
        configuration.default("LogDirectory", "../Data")
        configuration.default("machineCalibrationPath", "../Data/")
        configuration.default("machineCalibrationFile",
                              Settings.MACHINE_CALIBRATION_FILE)
        configuration.default("APA_LogDirectory", "../Data/APA")
        configuration.default("recipeDirectory", "../Recipes")
        configuration.default("recipeArchiveDirectory", "../Recipes")

        # Velocity limits.
        configuration.default("maxVelocity", 16 * 25.4)  # 16 inches/second
        configuration.default("maxSlowVelocity", 1 * 25.4)  # 1 inches/second

        # Acceleration limits.
        configuration.default("maxAcceleration", 8 * 25.4)  # 8 inches/s^2
        configuration.default("maxDeceleration", 2 * 25.4)  # 2 inches/s^2
