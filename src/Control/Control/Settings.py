###############################################################################
# Name: Settings.py
# Uses: Structure for constant settings used in various systems.
# Date: 2016-02-11
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-11 - QUE - Creation.
###############################################################################

class Settings :
  SERVER_PORT                 = 6626  # Default TCP port number (plank's constant).
  SERVER_MAX_DATA_SIZE        = 1024  # Max data that can be read from client at once.
  SERVER_BACK_LOG             = 5     # Default recommended by Python manual.
  CLIENT_MAX_DATA_SIZE        = 1024  # Max data that can be read from client at once.
  IO_UPDATE_TIME              = 0.1   # In seconds.  Currently 10 times/sec.

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
