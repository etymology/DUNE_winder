###############################################################################
# Name: Settings.py
# Uses: Structure for constant settings used in various systems.
# Date: 2016-02-11
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

class Settings :
  SERVER_PORT                 = 6626  # Default TCP port number (plank's constant).
  WEB_SERVER_PORT             = 80    # Port for web server (80 is default).
  SERVER_MAX_DATA_SIZE        = 1024  # Max data that can be read from server at once.
  SERVER_BACK_LOG             = 5     # Default recommended by Python manual.
  CLIENT_MAX_DATA_SIZE        = 1024  # Max data that can be read from client at once.
  IO_UPDATE_TIME              = 0.1   # In seconds.  Currently 10 times/sec.

  # Path to configuration file.
  CONFIG_FILE = "../configuration.xml"

  G_CODE_LOG_FILE = "_gCode.txt"

  IO_LOG = "../Data/IO_log.csv"

  WEB_DIRECTORY = "../WebUI"

  #---------------------------------------------------------------------
  @staticmethod
  def defaultConfig( configuration ) :
    """
    Setup default values for configuration.
    """
    configuration.default( "plcAddress", "192.168.1.36" )

    # Default for GUI server.
    configuration.default( "serverAddress", "127.0.0.1" )
    configuration.default( "serverPort", Settings.SERVER_PORT )

    # Default for GUI server.
    configuration.default( "webServerPort", 80 )

    # Log file locations.
    configuration.default( "LogDirectory", "../Data" )
    configuration.default( "APA_LogDirectory", "../Data/APA" )
    configuration.default( "recipeDirectory", "../Recipes" )
    configuration.default( "recipeArchiveDirectory", "../Data/Recipes" )

    # Velocity limits.
    configuration.default( "maxVelocity", 16 * 25.4 ) # 16 inches/second
    configuration.default( "maxSlowVelocity", 1 * 25.4 ) # 1 inches/second

    # Acceleration limits.
    configuration.default( "maxAcceleration", 8 * 25.4 ) # 8 inches/s^2
    configuration.default( "maxDeceleration", 2 * 25.4 ) # 2 inches/s^2
