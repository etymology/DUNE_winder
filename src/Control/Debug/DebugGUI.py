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
#import time

from Library.UI_ClientConnection import UI_ClientConnection

class DebugGUI( wx.Frame ):

    def getIO( self, ioPoint ) :
      return self.remote( ioPoint + ".get()" )

    def setIO( self, ioPoint, state, event ) :
      self.remote( ioPoint + ".set( " + str( state ) + " )" )
      event.Skip()

    def jogStart( self, x, y ) :
      self.remote( "io.xAxis.setVelocity( " + str( x ) + " )" )
      self.remote( "io.yAxis.setVelocity( " + str( y ) + " )" )
      self.remote( "io.moveType.set( 1 )" )

    def jogStop( self ) :
      self.remote( "io.xAxis.setVelocity( 0.0 )" )
      self.remote( "io.yAxis.setVelocity( 0.0 )" )

    def setPosition( self, event ) :
      self._temp += 1
      if self._temp > 10 :
        self._temp = 0
      self.remote( "io.xAxis.setDesiredPosition( " + str( self._temp ) + " )" )
      self.remote( "io.yAxis.setDesiredPosition( " + str( self._temp ) + " )" )
      self.remote( "io.moveType.set( 2 )" )

    def __init__( self, parent, address, port, maxReceiveSize ) :
      super( DebugGUI, self ).__init__( None )

      self.remote = UI_ClientConnection( address, port, maxReceiveSize )

      self._temp = 0

      self._value = 0
      self._parent = parent

      panel = wx.Panel( self )

      vbox = wx.FlexGridSizer( wx.VERTICAL )

      outer = wx.FlexGridSizer( 1, 2, 0, 0 )

      gs = wx.GridSizer( 3, 2, 5, 5 )
      self.time  = wx.StaticText( panel, label='9999.99' )
      self.estop = wx.StaticText( panel, label='' )
      self.park  = wx.StaticText( panel, label='' )
      gs.AddMany(
        [
          ( wx.StaticText( panel, label='Time'  ) ), ( self.time  ),
          ( wx.StaticText( panel, label='Stop' ) ),  ( self.estop ),
          ( wx.StaticText( panel, label='Park'  ) ), ( self.park  )
        ]
      )

      outer.Add( gs, proportion=1, flag=wx.ALL|wx.EXPAND, border=5 )

      gs = wx.GridSizer( 3, 4, 5, 5 )
      startButton = wx.Button( panel, label='Start' )
      startButton.Bind( wx.EVT_LEFT_DOWN, lambda e: self.setIO( "io.start", True, e ) )
      startButton.Bind( wx.EVT_LEFT_UP,   lambda e: self.setIO( "io.start", False, e ) )

      eStopButton = wx.ToggleButton( panel, label='Stop' )
      eStopButton.Bind( wx.EVT_TOGGLEBUTTON, lambda e: self.setIO( "io.stop", e.Checked(), e ) )

      parkButton = wx.ToggleButton( panel, label='Park' )
      parkButton.Bind( wx.EVT_TOGGLEBUTTON, lambda e: self.setIO( "io.park", e.Checked(), e ) )



      jogXY_RU = wx.Button( panel, label='\\' )
      jogXY_RZ = wx.Button( panel, label='<-' )
      jogXY_RD = wx.Button( panel, label='/' )

      jogXY_ZU = wx.Button( panel, label='^' )
      jogXY_ZZ = wx.Button( panel, label='*' )
      jogXY_ZD = wx.Button( panel, label='v' )

      jogXY_FU = wx.Button( panel, label='/' )
      jogXY_FZ = wx.Button( panel, label='->' )
      jogXY_FD = wx.Button( panel, label='\\' )

      jogXY_RU.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart( -1,  1 ) )
      jogXY_RZ.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart( -1,  0 ) )
      jogXY_RD.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart( -1, -1 ) )

      jogXY_ZU.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart(  0,  1 ) )
      jogXY_ZZ.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart(  0,  0 ) )
      jogXY_ZD.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart(  0, -1 ) )

      jogXY_FU.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart(  1,  1 ) )
      jogXY_FZ.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart(  1,  0 ) )
      jogXY_FD.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart(  1, -1 ) )


      jogXY_RU.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )
      jogXY_RZ.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )
      jogXY_RD.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )

      jogXY_ZU.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )
      jogXY_ZZ.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )
      jogXY_ZD.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )

      jogXY_FU.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )
      jogXY_FZ.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )
      jogXY_FD.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )

      #jogX_Forward.Bind( wx.EVT_LEFT_DOWN, self.jogX_StartF )
      #jogX_Forward.Bind( wx.EVT_LEFT_UP,   self.jogX_Stop )

      #jogX_Reverse.Bind( wx.EVT_LEFT_DOWN, self.jogX_StartR )
      #jogX_Reverse.Bind( wx.EVT_LEFT_UP,   self.jogX_Stop )



      #jogY_Forward = wx.Button( panel, label='^' )
      #jogY_Forward.Bind( wx.EVT_LEFT_DOWN, self.setPosition )


      gs.AddMany(
        [
          ( startButton ),  ( jogXY_RU ), ( jogXY_ZU ), ( jogXY_FU ),
          ( eStopButton ),  ( jogXY_RZ ), ( jogXY_ZZ ), ( jogXY_FZ ),
          ( parkButton ),   ( jogXY_RD ), ( jogXY_ZD ), ( jogXY_FD )
        ]
      )
      outer.Add( gs, proportion=1, flag=wx.ALL|wx.EXPAND, border=5 )

      vbox.Add( outer )

      gs = wx.FlexGridSizer( 4, 6, 5, 5 )

      self.empty = wx.StaticText( panel, -1, '')
      self.xAxis = wx.StaticText( panel, label='x:' )
      self.yAxis = wx.StaticText( panel, label='y:' )
      self.zAxis = wx.StaticText( panel, label='z:' )
      self.xAxisML = wx.StaticText( panel, label='Moving' )
      self.xAxisSL = wx.StaticText( panel, label='Seek' )
      self.xAxisPL = wx.StaticText( panel, label='Position' )
      self.xAxisVL = wx.StaticText( panel, label='Velocity' )
      self.xAxisAL = wx.StaticText( panel, label='Acceleration' )
      self.xAxisM = wx.StaticText( panel, label='False' )
      self.yAxisM = wx.StaticText( panel, label='False'  )
      self.zAxisM = wx.StaticText( panel, label='False'  )
      self.xAxisS = wx.StaticText( panel, label='+0000.00' )
      self.yAxisS = wx.StaticText( panel, label='+000.00'  )
      self.zAxisS = wx.StaticText( panel, label='+000.00'  )
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
          ( self.empty ), ( self.xAxisML ), ( self.xAxisSL ), ( self.xAxisPL ), ( self.xAxisVL ), ( self.xAxisAL ),
          ( self.xAxis ), ( self.xAxisM  ), ( self.xAxisS  ), ( self.xAxisP  ), ( self.xAxisV  ), ( self.xAxisA  ),
          ( self.yAxis ), ( self.yAxisM  ), ( self.yAxisS  ), ( self.yAxisP  ), ( self.yAxisV  ), ( self.yAxisA  ),
          ( self.zAxis ), ( self.zAxisM  ), ( self.zAxisS  ), ( self.zAxisP  ), ( self.zAxisV  ), ( self.zAxisA  ),
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

      self.SetSize( (550, 220) )
      self.SetTitle( 'DUNE Winder Simulator' )
      self.Show( True )

      #self.Bind( wx.EVT_CLOSE, self.onClose )

    #def onClose( self, event ) :
    #  # On close, signal all threads to shutdown.
    #  PrimaryThread.stopAllThreads()
    #  self.Destroy()


    def isFloat( self, value ):
      result = True
      try:
        float( value )
      except:
        result = False

      return result

    def remoteFloat( self, tag, formating ) :
      result = "--"
      value = self.remote( tag )
      if ( self.isFloat( value ) ) :
        value = float( value )
        result = formating.format( value )

        # Round -0.00 to 0.00.
        if 0 == float( result ) :
          result = formating.format( 0.0 )

      return result

    def update( self, event ) :

      isRunning = ( "True" == self.remote.get( "PrimaryThread.isRunning" ) )

      # If primary threads are shutting down, close the window.
      if not isRunning :
        self.Close()

      self.remote( "io.simulationTime.setLocal()" )
      currentTime = self.remote( "io.simulationTime.get()" )
      try:
        currentTime = datetime.datetime.strptime( currentTime, "%Y-%m-%d %H:%M:%S.%f" )
      except ValueError:
        # Work around.  On some system (Windows) if the time 0 for microseconds,
        # it does not append the ".0" at the end.  So on a value error, just
        # try again with the .0 appended.
        currentTime += ".0"
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

      xAxisMotion       = self.remote.get( "io.xAxis.isSeeking()" )
      yAxisMotion       = self.remote.get( "io.yAxis.isSeeking()" )
      zAxisMotion       = self.remote.get( "io.zAxis.isSeeking()" )

      xAxisSeek         = self.remoteFloat( "io.xAxis.getDesiredPosition()", "{0:>1.3f}" )
      yAxisSeek         = self.remoteFloat( "io.yAxis.getDesiredPosition()", "{0:>1.3f}" )
      zAxisSeek         = self.remoteFloat( "io.zAxis.getDesiredPosition()", "{0:>1.3f}" )

      xAxisPosition     = self.remoteFloat( "io.xAxis.getPosition()"    , "{0:>1.3f}" )
      xAxisVelocity     = self.remoteFloat( "io.xAxis.getVelocity()"    , "{0:>1.2f}" )
      xAxisAcceleration = self.remoteFloat( "io.xAxis.getAcceleration()", "{0:>1.0f}" )


      yAxisPosition     = self.remoteFloat( "io.yAxis.getPosition()"    , "{0:>1.3f}" )
      yAxisVelocity     = self.remoteFloat( "io.yAxis.getVelocity()"    , "{0:>1.2f}" )
      yAxisAcceleration = self.remoteFloat( "io.yAxis.getAcceleration()", "{0:>1.0f}" )

      zAxisPosition     = self.remoteFloat( "io.zAxis.getPosition()"    , "{0:>1.2f}" )
      zAxisVelocity     = self.remoteFloat( "io.zAxis.getVelocity()"    , "{0:>1.2f}" )
      zAxisAcceleration = self.remoteFloat( "io.zAxis.getAcceleration()", "{0:>1.0f}" )

      self.xAxisS.SetLabel( xAxisSeek )
      self.yAxisS.SetLabel( yAxisSeek )
      self.zAxisS.SetLabel( zAxisSeek )

      self.xAxisM.SetLabel( xAxisMotion )
      self.yAxisM.SetLabel( yAxisMotion )
      self.zAxisM.SetLabel( zAxisMotion )

      self.xAxisP.SetLabel( xAxisPosition     )
      self.xAxisV.SetLabel( xAxisVelocity     )
      self.xAxisA.SetLabel( xAxisAcceleration )

      self.yAxisP.SetLabel( yAxisPosition     )
      self.yAxisV.SetLabel( yAxisVelocity     )
      self.yAxisA.SetLabel( yAxisAcceleration )

      self.zAxisP.SetLabel( zAxisPosition     )
      self.zAxisV.SetLabel( zAxisVelocity     )
      self.zAxisA.SetLabel( zAxisAcceleration )

if __name__ == "__main__":
    wxApplication = wx.App()
    guiFrame = DebugGUI( None, "172.16.21.47", 6626 )
    wxApplication.MainLoop()
