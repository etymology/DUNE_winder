###############################################################################
# Name: LogTab.py
# Uses: Log display tab.
# Date: 2016-04-15
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
import ast
import wx
from .Remote import Remote
from .ActivatedTab import ActivatedTab
from .SystemTime import SystemTime

class LogTab( wx.Panel, Remote, ActivatedTab ) :
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

    grideSizer = wx.FlexGridSizer( 1, 1, 5, 5 )
    self.log = wx.TextCtrl( self, -1, size = (500, 530), style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL )

    grideSizer.Add( self.log )

    vbox.Add( grideSizer )

    self.SetSizer( vbox )

  #---------------------------------------------------------------------
  def update( self, event ) :
    event = event
    self.systemTime.update()

    log = self.remote.get( "log.getRecent()" )
    log = ast.literal_eval( log )
    result = ""
    for line in log :
      sections = line.split( "\t" )

      eventTime = self.systemTime.convertTimeString( sections[ 0 ] )
      eventTime = self.systemTime.deltaString( eventTime )

      result += eventTime + " " + sections[ 3 ] + "\n"

    log = result

    self.log.SetValue( log )
