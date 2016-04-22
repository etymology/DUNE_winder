###############################################################################
# Name: PLC_Tab.py
# Uses: PLC tag list monitoring tab.
# Date: 2016-04-15
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
import ast
import wx
from .Remote import Remote
from .ActivatedTab import ActivatedTab
from .SystemTime import SystemTime

class PLC_Tab( wx.Panel, Remote, ActivatedTab ) :
  #---------------------------------------------------------------------
  def __init__( self, remote, panel ) :

    wx.Panel.__init__( self, panel )
    ActivatedTab.__init__( self, self, panel )
    Remote.__init__( self, remote )
    self.remote = remote

    vbox = wx.FlexGridSizer( wx.VERTICAL )

    #
    # Time.
    #
    self.systemTime = SystemTime( remote, self, vbox )

    #
    # Tags.
    #
    grideSizer = wx.FlexGridSizer( 100, 2, 0, 40 )

    self._tagList = self.remote.get( "LowLevelIO.getTags()" )
    self._tagList = ast.literal_eval( self._tagList )

    self._tagLabels = {}
    for instance in self._tagList :
      label = wx.StaticText( self, label=instance[ 0 ] )
      value = wx.StaticText( self, label=str( instance[ 1 ] ) )
      self._tagLabels[ instance[ 0 ] ] = value

      grideSizer.Add( label )
      grideSizer.Add( value )

    vbox.Add( grideSizer )

    self.SetSizer( vbox )

  #---------------------------------------------------------------------
  def update( self, event ) :
    event = event
    self.systemTime.update()

    for instance in self._tagList :
      tagName = instance[ 0 ]
      tagValue = self.remote.get( "LowLevelIO.getTag( \"" + tagName + "\")" )
      self._tagLabels[ tagName ].SetLabel( tagValue )
