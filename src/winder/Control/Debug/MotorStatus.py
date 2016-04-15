###############################################################################
# Name: MotorStatus.py
# Uses: Display motor motion status.
# Date: 2016-04-15
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
import wx
from Remote import Remote

class MotorStatus( Remote ) :
  #---------------------------------------------------------------------
  def __init__( self, remote, panel, vbox ) :

    Remote.__init__( self, remote )

    #
    # Motor status.
    #
    grideSizer = wx.FlexGridSizer( 4, 6, 5, 5 )

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

    grideSizer.AddMany(
      [
        ( self.empty ), ( self.xAxisML ), ( self.xAxisSL ), ( self.xAxisPL ), ( self.xAxisVL ), ( self.xAxisAL ),
        ( self.xAxis ), ( self.xAxisM  ), ( self.xAxisS  ), ( self.xAxisP  ), ( self.xAxisV  ), ( self.xAxisA  ),
        ( self.yAxis ), ( self.yAxisM  ), ( self.yAxisS  ), ( self.yAxisP  ), ( self.yAxisV  ), ( self.yAxisA  ),
        ( self.zAxis ), ( self.zAxisM  ), ( self.zAxisS  ), ( self.zAxisP  ), ( self.zAxisV  ), ( self.zAxisA  ),
      ]
     )

    vbox.Add( grideSizer )

  #---------------------------------------------------------------------
  def update( self ) :

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
# end class
