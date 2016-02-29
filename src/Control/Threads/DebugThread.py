###############################################################################
# Name: DebugThread.py
# Uses: Thread for debug interface.
# Date: 2016-02-08
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-08 - QUE - Creation.
###############################################################################
from PrimaryThread import PrimaryThread
from Debug.DebugGUI import DebugGUI
from Control.Settings import Settings
import wx

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

    wxApplication = wx.App()
    DebugGUI( None, self.address, self.port, Settings.CLIENT_MAX_DATA_SIZE )
    wxApplication.MainLoop()

    # If this point is reached, the GUI has shutdown.
    PrimaryThread.stopAllThreads()

# end class
