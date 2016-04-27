###############################################################################
# Name: JogTab.py
# Uses: The manual/jog tab.
# Date: 2016-04-15
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
import math
import wx
from Remote import Remote
from ActivatedTab import ActivatedTab
from SystemTime import SystemTime
from MotorStatus import MotorStatus

class JogTab( wx.Panel, Remote, ActivatedTab ) :
  #---------------------------------------------------------------------
  def jogZ_Start( self, direction ) :
    velocity = self.slider.GetValue()
    velocity *= direction
    self.remote( "process.jogZ(" + str( velocity ) + ")" )

  #---------------------------------------------------------------------
  def jogStart( self, x, y ) :

    velocity = self.slider.GetValue()
    x *= velocity
    y *= velocity

    # When both velocities are the same, calculate the maximum linear velocity
    # and use that.
    if 0 != x and 0 != y and abs( x ) == abs( y ) :
      velocity = math.sqrt( x * x / 2.0 )
      if x < 0 :
        x = -velocity
      else :
        x = velocity

      if y < 0 :
        y = -velocity
      else :
        y = velocity

    self.remote( "process.jogXY(" + str( x ) + "," + str( y ) + ")" )

  #---------------------------------------------------------------------
  def jogStop( self ) :
    self.remote( "process.jogXY( 0, 0 )" )

  #---------------------------------------------------------------------
  def jogZ_Stop( self ) :
    self.remote( "process.jogZ( 0 )" )

  #---------------------------------------------------------------------
  def setPosition( self, event ) :
    event = event
    velocity = self.slider.GetValue()
    self.remote( "process.manualSeekXY( 0, 0, " + str( velocity ) + " )" )

  #---------------------------------------------------------------------
  def setZ_Retract( self, event ) :
    event = event
    velocity = self.slider.GetValue()
    self.remote( "process.manualSeekZ( 0, " + str( velocity ) + " )" )

  #---------------------------------------------------------------------
  def setZ_Extend( self, event ) :
    event = event
    velocity = self.slider.GetValue()
    self.remote( "process.manualSeekZ( 422, " + str( velocity ) + " )" )

  #---------------------------------------------------------------------
  def latch( self, event ) :
    self.remote.get( "io.plcLogic.latch()" )

  #---------------------------------------------------------------------
  def latchHome( self, event ) :
    self.remote.get( "io.plcLogic.latchHome()" )

  #---------------------------------------------------------------------
  def latchUnlock( self, event ) :
    self.remote.get( "io.plcLogic.latchUnlock()" )

  #---------------------------------------------------------------------
  def __init__( self, remote, panel ):

    wx.Panel.__init__( self, panel )
    ActivatedTab.__init__( self, self, panel )
    Remote.__init__( self, remote )
    self.remote = remote

    vbox = wx.FlexGridSizer( wx.VERTICAL )

    self.systemTime = SystemTime( remote, self, vbox )

    outer = wx.FlexGridSizer( 4, 1, 0, 0 )

    #
    # Jog buttons.
    #
    xyControlsBox   = wx.StaticBox( self, wx.ID_ANY, "X/Y Controls" )
    xyControlsSizer = wx.StaticBoxSizer( xyControlsBox, wx.VERTICAL )
    grideSizer = wx.GridSizer( 3, 3, 5, 5 )

    jogXY_RU = wx.Button( self, label='\\' )
    jogXY_RZ = wx.Button( self, label='<-' )
    jogXY_RD = wx.Button( self, label='/' )

    jogXY_ZU = wx.Button( self, label='^' )
    jogXY_ZZ = wx.Button( self, label='*' )
    jogXY_ZD = wx.Button( self, label='v' )

    jogXY_FU = wx.Button( self, label='/' )
    jogXY_FZ = wx.Button( self, label='->' )
    jogXY_FD = wx.Button( self, label='\\' )

    jogXY_RU.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart( -1,  1 ) )
    jogXY_RZ.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart( -1,  0 ) )
    jogXY_RD.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart( -1, -1 ) )

    jogXY_ZU.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart(  0,  1 ) )
    jogXY_ZD.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart(  0, -1 ) )

    jogXY_FU.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart(  1,  1 ) )
    jogXY_FZ.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart(  1,  0 ) )
    jogXY_FD.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogStart(  1, -1 ) )


    jogXY_RU.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )
    jogXY_RZ.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )
    jogXY_RD.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )

    jogXY_ZU.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )
    jogXY_ZD.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )

    jogXY_FU.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )
    jogXY_FZ.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )
    jogXY_FD.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogStop() )

    jogXY_ZZ.Bind( wx.EVT_LEFT_DOWN, self.setPosition )

    grideSizer.AddMany(
      [
        ( jogXY_RU ), ( jogXY_ZU ), ( jogXY_FU ),
        ( jogXY_RZ ), ( jogXY_ZZ ), ( jogXY_FZ ),
        ( jogXY_RD ), ( jogXY_ZD ), ( jogXY_FD )
      ]
    )
    #outer.Add( grideSizer, proportion=1, flag=wx.ALL|wx.EXPAND, border=5 )
    xyControlsSizer.Add( grideSizer )
    outer.Add( xyControlsSizer, proportion=1, flag=wx.ALL|wx.EXPAND, border=5 )


    zControlsBox   = wx.StaticBox( self, wx.ID_ANY, "Z-Controls" )
    zControlsSizer = wx.StaticBoxSizer( zControlsBox, wx.VERTICAL )

    grideSizer = wx.GridSizer( 1, 3, 5, 5 )
    jogZ_E = wx.Button( self, label='<-' )
    jogZ_Z = wx.Button( self, label='*' )
    jogZ_R = wx.Button( self, label='->' )

    jogZ_E.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogZ_Start( -1 ) )
    jogZ_Z.Bind( wx.EVT_LEFT_DOWN, self.setZ_Retract )
    jogZ_R.Bind( wx.EVT_LEFT_DOWN, lambda e: self.jogZ_Start( 1 ) )

    jogZ_E.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogZ_Stop() )
    jogZ_R.Bind( wx.EVT_LEFT_UP,   lambda e: self.jogZ_Stop() )

    grideSizer.AddMany( [ ( jogZ_E ), ( jogZ_Z ), ( jogZ_R )  ] )
    zControlsSizer.Add( grideSizer, proportion=1, flag=wx.ALL|wx.EXPAND, border=5 )



    grideSizer = wx.GridSizer( 2, 3, 5, 5 )
    jogZ_Retract = wx.Button( self, label='Retract' )
    jogZ_Extend  = wx.Button( self, label='Extend' )
    jogZ_Latch   = wx.Button( self, label='Latch' )

    jogZ_Home    = wx.Button( self, label='Home' )
    jogZ_Idle    = wx.Button( self, label='Unlock' )

    jogZ_Retract.Bind( wx.EVT_LEFT_DOWN, self.setZ_Retract )
    jogZ_Extend.Bind(  wx.EVT_LEFT_DOWN, self.setZ_Extend )
    jogZ_Latch.Bind(   wx.EVT_LEFT_DOWN, self.latch )
    jogZ_Home.Bind(    wx.EVT_LEFT_DOWN, self.latchHome )
    jogZ_Idle.Bind(    wx.EVT_LEFT_DOWN, self.latchUnlock )


    grideSizer.AddMany(
      [
        ( jogZ_Retract ), ( jogZ_Extend ), ( jogZ_Latch ),
        ( jogZ_Home ),    ( jogZ_Idle )
      ]
    )
    zControlsSizer.Add( grideSizer )
    outer.Add( zControlsSizer, proportion=1, flag=wx.ALL|wx.EXPAND, border=5 )

    vbox.Add( outer )


    #
    # Velocity bar.
    #
    grideSizer = wx.GridSizer( 1, 1, 5, 5 )
    self.slider = \
      wx.Slider(
        self,
        -1,
        100,
        1, 500,
        wx.DefaultPosition,
        (500, -1),
        wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_LABELS
      )
    self.slider.Bind( wx.EVT_SCROLL, lambda e: self.remote( "process.gCodeHandler.setLimitVelocity( " + str( self.slider.GetValue() ) + ")" ) )

    grideSizer.AddMany(
      [
        ( self.slider )
      ]
    )
    #outer.Add( grideSizer, proportion=1, flag=wx.ALL|wx.EXPAND, border=5 )
    vbox.Add( grideSizer )


    self.SetSizer( vbox )
    self.motorStatus = MotorStatus( remote, self, vbox )

  #---------------------------------------------------------------------
  def update( self, event ) :
    event = event
    self.systemTime.update()
    self.motorStatus.update()

# end class
