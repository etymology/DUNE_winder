###############################################################################
# Name: DebugGUI.py
# Uses: Debug user interface.
# Date: 2016-02-08
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
import wx

from Library.UI_ClientConnection import UI_ClientConnection

from .Remote import Remote
from .JogTab import JogTab
from .APA_Tab import APA_Tab
from .IO_Tab import IO_Tab
from .PLC_Tab import PLC_Tab
from .LogTab import LogTab

class DebugGUI( wx.Frame, Remote ):

  #---------------------------------------------------------------------
  def __init__( self, parent, address, port, maxReceiveSize ) :
    wx.Frame.__init__( self, None )

    #time.sleep( 0.2 )

    self.remote = UI_ClientConnection( address, port, maxReceiveSize )

    Remote.__init__( self, self.remote )

    self._parent = parent
    panel = wx.Panel( self )

    notebook = wx.Notebook( panel )

    tab1 = JogTab( self.remote, notebook )
    tab2 = APA_Tab( self.remote, notebook )
    tab3 = IO_Tab( self.remote, notebook )
    tab4 = PLC_Tab( self.remote, notebook )
    tab5 = LogTab( self.remote, notebook )

    notebook.AddPage( tab1, "Jog" )
    notebook.AddPage( tab2, "APA" )
    notebook.AddPage( tab3, "I/O" )
    notebook.AddPage( tab4, "PLC" )
    notebook.AddPage( tab5, "Log" )

    sizer = wx.BoxSizer()
    sizer.Add( notebook, 1, wx.EXPAND )
    panel.SetSizer( sizer )

    self.timer = wx.Timer(self)
    self.Bind( wx.EVT_TIMER, self.update, self.timer )
    self.timer.Start( 100 )

    self.SetSize( (520, 600) )
    self.SetTitle( 'DUNE Winder Simulator' )
    self.Show( True )

  #---------------------------------------------------------------------
  def update( self, event ) :
    event = event
    isRunning = ( "True" == self.remote.get( "PrimaryThread.isRunning" ) )

    # If primary threads are shutting down, close the window.
    if not isRunning :
      self.Close()

# end class

if __name__ == "__main__":

  import sys
  from Machine.Settings import Settings

  if len( sys.argv ) < 2 :
    print "Need to specify IP address for DebugGUI"
  else:
    wxApplication = wx.App()
    ip = sys.argv[ 1 ]
    DebugGUI( None, ip, Settings.SERVER_PORT , Settings.SERVER_MAX_DATA_SIZE )
    wxApplication.MainLoop()
