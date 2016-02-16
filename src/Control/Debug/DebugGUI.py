#==============================================================================
# Name: DebugGUI.py
# Uses: Debug user interface.
# Date: 2016-02-08
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-08 - QUE - Creation.
#==============================================================================
import wx
import datetime
import time

from Library.UI_ClientConnection import UI_ClientConnection

class DebugGUI( wx.Frame ):

    def getIO( self, ioPoint ) :
      return self.remote( ioPoint + ".get()" )

    def setIO( self, ioPoint, state, event ) :
      self.remote( ioPoint + ".set( " + str( state ) + " )" )
      event.Skip()

    def __init__( self, parent, address, port, maxReceiveSize ) :
      super( DebugGUI, self ).__init__( None )

      self.remote = UI_ClientConnection( address, port, maxReceiveSize )

      self._value = 0
      self._parent = parent

      panel = wx.Panel( self )

      vbox = wx.FlexGridSizer( wx.VERTICAL )

      outer = wx.GridSizer( 1, 2, 0, 0 )

      gs = wx.GridSizer( 3, 2, 5, 5 )
      self.time  = wx.StaticText( panel, label='9999.99' )
      self.estop = wx.StaticText( panel, label='' )
      self.park  = wx.StaticText( panel, label='' )
      gs.AddMany(
        [
          ( wx.StaticText( panel, label='Time'  ) ), ( self.time  ),
          ( wx.StaticText( panel, label='ESTOP' ) ), ( self.estop ),
          ( wx.StaticText( panel, label='Park'  ) ), ( self.park  )
        ]
      )

      outer.Add( gs, proportion=1, flag=wx.ALL|wx.EXPAND, border=5 )

      gs = wx.GridSizer( 3, 1, 5, 5 )
      startButton = wx.Button( panel, label='Start' )
      startButton.Bind( wx.EVT_LEFT_DOWN, lambda e: self.setIO( "io.start", True, e ) )
      startButton.Bind( wx.EVT_LEFT_UP,   lambda e: self.setIO( "io.start", False, e ) )

      eStopButton = wx.ToggleButton( panel, label='ESTOP' )
      eStopButton.Bind( wx.EVT_TOGGLEBUTTON, lambda e: self.setIO( "io.estop", e.Checked(), e ) )

      parkButton = wx.ToggleButton( panel, label='Park' )
      parkButton.Bind( wx.EVT_TOGGLEBUTTON, lambda e: self.setIO( "io.park", e.Checked(), e ) )

      gs.AddMany(
        [
          ( startButton ),
          ( eStopButton ),
          ( parkButton )
        ]
      )
      outer.Add( gs, proportion=1, flag=wx.ALL|wx.EXPAND, border=5 )

      vbox.Add( outer )

      gs = wx.FlexGridSizer( 3, 4, 5, 5 )

      self.xAxis = wx.StaticText( panel, label='xAxis:' )
      self.yAxis = wx.StaticText( panel, label='yAxis:' )
      self.zAxis = wx.StaticText( panel, label='zAxis:' )
      self.xAxisP = wx.StaticText( panel, label='+0000.00' )
      self.yAxisP = wx.StaticText( panel, label='+000.00'  )
      self.zAxisP = wx.StaticText( panel, label='+000.00'  )
      self.xAxisV = wx.StaticText( panel, label='+0000.00' )
      self.yAxisV = wx.StaticText( panel, label='+000.00'  )
      self.zAxisV = wx.StaticText( panel, label='+000.00'  )
      self.xAxisA = wx.StaticText( panel, label='+0000.00' )
      self.yAxisA = wx.StaticText( panel, label='+000.00'  )
      self.zAxisA = wx.StaticText( panel, label='+000.00'  )

      gs.AddMany(
        [
          ( self.xAxis ), ( self.xAxisP ), ( self.xAxisV ), ( self.xAxisA ),
          ( self.yAxis ), ( self.yAxisP ), ( self.yAxisV ), ( self.yAxisA ),
          ( self.zAxis ), ( self.zAxisP ), ( self.zAxisV ), ( self.zAxisA ),
        ]
       )

      vbox.Add( gs )


      gs = wx.FlexGridSizer( 2, 2, 5, 5 )
      self.lineText  = wx.StaticText( panel, label='G-Code line:' )
      self.lineValue = wx.StaticText( panel, label='0000' )

      self.stateText  = wx.StaticText( panel, label='State:' )
      self.stateValue = wx.StaticText( panel, label='<unknown>' )

      gs.AddMany(
        [
          ( self.lineText ),  ( self.lineValue ),
          ( self.stateText ), ( self.stateValue )
        ]
       )

      vbox.Add( gs )

      panel.SetSizer( vbox )

      self.startTime = datetime.datetime.utcnow()

      self.timer = wx.Timer(self)
      self.Bind( wx.EVT_TIMER, self.update, self.timer )
      self.timer.Start( 100 )

      self.SetSize( (350, 220) )
      self.SetTitle( 'DUNE Winder Simulator' )
      self.Show( True )

      #self.Bind( wx.EVT_CLOSE, self.onClose )

    #def onClose( self, event ) :
    #  # On close, signal all threads to shutdown.
    #  PrimaryThread.stopAllThreads()
    #  self.Destroy()

    def update( self, event ) :

      isRunning = ( "True" == self.remote.get( "PrimaryThread.isRunning" ) )

      # If primary threads are shutting down, close the window.
      if not isRunning :
        self.Close()

      self.remote( "io.simulationTime.setLocal()" )
      currentTime = self.remote( "io.simulationTime.get()" )
      currentTime = datetime.datetime.strptime( currentTime, "%Y-%m-%d %H:%M:%S.%f" )
      delta = currentTime - self.startTime
      self.time.SetLabel( "{:6.3f}".format( delta.total_seconds() ) )

      estop = ( "True" == self.remote( "io.estop.get()" ) )

      if estop :
        self.remote( "io.xAxis.stop()" )
        self.remote( "io.yAxis.stop()" )
        self.remote( "io.zAxis.stop()" )

      self.remote( "io.xAxis.motionUpdate()" )
      self.remote( "io.yAxis.motionUpdate()" )
      self.remote( "io.zAxis.motionUpdate()" )

      self.estop.SetLabel( self.remote( "io.estop" ) )
      self.park.SetLabel(  self.remote( "io.park" ) )

      self.lineValue.SetLabel( self.remote.get( "gCodeHandler.line" ) )
      self.stateValue.SetLabel( self.remote.get( "controlStateMachine.state.__class__.__name__" ) )


      xAxisPosition     = float( self.remote( "io.xAxis.getPosition()"     ) )
      xAxisVelocity     = float( self.remote( "io.xAxis.getVelocity()"     ) )
      xAxisAcceleration = float( self.remote( "io.xAxis.getAcceleration()" ) )

      yAxisPosition     = float( self.remote( "io.yAxis.getPosition()"     ) )
      yAxisVelocity     = float( self.remote( "io.yAxis.getVelocity()"     ) )
      yAxisAcceleration = float( self.remote( "io.yAxis.getAcceleration()" ) )

      zAxisPosition     = float( self.remote( "io.zAxis.getPosition()"     ) )
      zAxisVelocity     = float( self.remote( "io.zAxis.getVelocity()"     ) )
      zAxisAcceleration = float( self.remote( "io.zAxis.getAcceleration()" ) )

      self.xAxisP.SetLabel( "{:>5.2f}".format( xAxisPosition     ) )
      self.xAxisV.SetLabel( "{:>5.2f}".format( xAxisVelocity     ) )
      self.xAxisA.SetLabel( "{:>5.2f}".format( xAxisAcceleration ) )

      self.yAxisP.SetLabel( "{:>5.2f}".format( yAxisPosition     ) )
      self.yAxisV.SetLabel( "{:>5.2f}".format( yAxisVelocity     ) )
      self.yAxisA.SetLabel( "{:>5.2f}".format( yAxisAcceleration ) )

      self.zAxisP.SetLabel( "{:>5.2f}".format( zAxisPosition     ) )
      self.zAxisV.SetLabel( "{:>5.2f}".format( zAxisVelocity     ) )
      self.zAxisA.SetLabel( "{:>5.2f}".format( zAxisAcceleration ) )

if __name__ == "__main__":
    wxApplication = wx.App()
    guiFrame = DebugGUI( None, "172.16.21.47", 6626 )
    wxApplication.MainLoop()
