###############################################################################
# Name: IO_Tab.py
# Uses: I/O monitoring tab.
# Date: 2016-04-15
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
import ast
import wx
from .Remote import Remote
from .ActivatedTab import ActivatedTab
from .SystemTime import SystemTime
from .MotorStatus import MotorStatus


class IO_Tab( wx.Panel, Remote, ActivatedTab ) :
  #---------------------------------------------------------------------
  def __init__( self, remote, panel ) :

    wx.Panel.__init__( self, panel )
    Remote.__init__( self, remote )
    ActivatedTab.__init__( self, self, panel )
    self.remote = remote

    vbox = wx.FlexGridSizer( wx.VERTICAL )

    #
    # Time.
    #
    self.systemTime = SystemTime( remote, self, vbox )

    outerGrid = wx.FlexGridSizer( 1, 2, 10, 50 )

    #
    # Inputs.
    #
    grideSizer = wx.FlexGridSizer( 100, 2, 0, 20 )

    self._inputList = self.remote.get( "LowLevelIO.getInputs()" )
    self._inputList = ast.literal_eval( self._inputList )

    self._inputLabels = {}
    for instance in self._inputList :
      label = wx.StaticText( self, label=instance[ 0 ] )
      value = wx.StaticText( self, label=str( instance[ 1 ] ) )
      self._inputLabels[ instance[ 0 ] ] = value

      grideSizer.Add( label )
      grideSizer.Add( value )

    outerGrid.Add( grideSizer )

    #
    # Outputs.
    #
    grideSizer = wx.FlexGridSizer( 1, 2, 0, 20 )

    self._outputList = self.remote.get( "LowLevelIO.getOutputs()" )
    self._outputList = ast.literal_eval( self._outputList )

    self._outputLabels = {}
    for instance in self._outputList :
      label = wx.StaticText( self, label=instance[ 0 ] )
      value = wx.StaticText( self, label=str( instance[ 1 ] ) )
      self._outputLabels[ instance[ 0 ] ] = value

      grideSizer.Add( label )
      grideSizer.Add( value )

    outerGrid.Add( grideSizer, wx.EXPAND )

    vbox.Add( outerGrid )

    #
    # Motor status.
    #
    self.motorStatus = MotorStatus( remote, self, vbox )

    self.SetSizer( vbox )

    self.timer = wx.Timer(self)
    self.Bind( wx.EVT_TIMER, self.update, self.timer )
    self.timer.Start( 100 )

  #---------------------------------------------------------------------
  def update( self, event ) :
    event = event
    self.systemTime.update()

    for instance in self._inputList :
      inputName = instance[ 0 ]
      inputValue = self.remote.get( "LowLevelIO.getInput( \"" + inputName + "\")" )
      self._inputLabels[ inputName ].SetLabel( inputValue )

    for instance in self._outputList :
      outputName = instance[ 0 ]
      outputValue = self.remote.get( "LowLevelIO.getOutput( \"" + outputName + "\")" )
      self._outputLabels[ outputName ].SetLabel( outputValue )

    self.motorStatus.update()

