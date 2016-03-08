###############################################################################
# Name: DebugThread.py
# Uses: Thread for debug interface.
# Date: 2016-02-08
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
from PrimaryThread import PrimaryThread
from Debug.DebugGUI import DebugGUI
from Control.Settings import Settings
import wx
import sys
import traceback

#------------------------------------------------------------------------------
# User interface server thread.
#------------------------------------------------------------------------------
class DebugThread( PrimaryThread ):
  #---------------------------------------------------------------------
  def __init__( self, address, port ):
    """
    Constructor.

    Args:
      callback: Function to send data from client.

    """

    PrimaryThread.__init__( self, "DebugThread" )
    self.address = address
    self.port = port

  #---------------------------------------------------------------------
  def run( self ):
    """
    Body of thread.  Create GUI and run it.
    """

    try :
      wxApplication = wx.App()
      DebugGUI( None, self.address, self.port, Settings.CLIENT_MAX_DATA_SIZE )
      wxApplication.MainLoop()
    except :
      exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
      tracebackString = repr( traceback.format_tb( exceptionTraceback ) )
      print tracebackString
      pass

    # If this point is reached, the GUI has shutdown.
    PrimaryThread.stopAllThreads()

# end class
