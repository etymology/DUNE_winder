###############################################################################
# Name: Settings.py
# Uses: Structure for constant settings used in various systems.
# Date: 2016-02-11
# Author(s):
#   Andrew Que <aque@bb7.com>
#   Benjamin Oye <oye@uchicago.edu> [port to python3, Jan 2024]
###############################################################################
import platform
from pathlib import Path

class Settings :

    SERVER_PORT                 = 6626  # Default TCP port number (plank's constant).
    WEB_SERVER_PORT             = 80    # Port for web server (80 is default).
    SERVER_MAX_DATA_SIZE        = 1024  # Max data that can be read from server at once.
    SERVER_BACK_LOG             = 5     # Default recommended by Python manual.
    CLIENT_MAX_DATA_SIZE        = 1024  # Max data that can be read from client at once.
    IO_UPDATE_TIME              = 0.1   # In seconds.  Currently 10 times/sec.

    src_winder = Path(__file__).parents[2]
    # Path to configuration file.
    # Check the operating system

    CONFIG_FILE = str(src_winder / "configuration.xml")
    UI_VERSION_FILE = str(src_winder / "WebUI/version.xml")
    WEB_DIRECTORY = str(src_winder / "WebUI")
    VERSION_FILE = str(src_winder / "Control/version.xml")

    # if platform.system() == "Windows":
    #     CONFIG_FILE = str(src_winder / "configuration.xml")
    #     UI_VERSION_FILE = str(src_winder / "WebUI/version.xml")
    #     WEB_DIRECTORY = str(src_winder / "WebUI")
    #     VERSION_FILE = str(src_winder / "Control/version.xml")

    # elif platform.system() == "Linux":
    #     CONFIG_FILE = str(src_winder / "configuration.xml")
    #     UI_VERSION_FILE = str(src_winder / "WebUI/version.xml")
    #     WEB_DIRECTORY = str(src_winder / "WebUI")
    #     VERSION_FILE = str(src_winder / "Control/version.xml")
    # else:
    #     # Handle other operating systems if needed
    #     print("Unsupported operating system")

    G_CODE_LOG_FILE = "_gCode.gc"

    IO_LOG = str(src_winder / "Data/IO_log.csv")

    MACHINE_CALIBRATION_FILE = "machineCalibration.xml"



    # File making up the version for the control software.
    CONTROL_FILES = ".*/.py$"

    # File making up the version for the user interface.
    UI_FILES = ".*/.html$|.*/.css$|.*/.js$"

    #---------------------------------------------------------------------
    @staticmethod
    def defaultConfig( configuration ) :
        """
        Setup default values for configuration.
        """
        configuration.default( "plcAddress", "192.168.140.13" )

        # Location of camera's last captured image.
        configuration.default( "cameraURL", "ftp://admin@192.168.140.19/image.bmp" )
        configuration.default( "pixelsPer_mm", 18 )

        # Default for GUI server.
        configuration.default( "serverAddress", "127.0.0.1" )
        configuration.default( "serverPort", Settings.SERVER_PORT )

        # Default for GUI server.
        configuration.default( "webServerPort", 80 )

        # Log file locations.
        configuration.default( "LogDirectory", "../Data" )
        configuration.default( "machineCalibrationPath", "../Data/" )
        configuration.default( "machineCalibrationFile", Settings.MACHINE_CALIBRATION_FILE )
        configuration.default( "APA_LogDirectory", "../Data/APA" )
        configuration.default( "recipeDirectory", "../Recipes" )
        configuration.default( "recipeArchiveDirectory", "../Recipes" )

        # Velocity limits.
        configuration.default( "maxVelocity", 16 * 25.4 ) # 16 inches/second
        configuration.default( "maxSlowVelocity", 1 * 25.4 ) # 1 inches/second

        # Acceleration limits.
        configuration.default( "maxAcceleration", 8 * 25.4 ) # 8 inches/s^2
        configuration.default( "maxDeceleration", 2 * 25.4 ) # 2 inches/s^2
