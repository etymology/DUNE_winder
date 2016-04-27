###############################################################################
# Name: ActivatedTab.py
# Uses: Periodically update the active tab when it is active.
# Date: 2016-04-15
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
import wx

class ActivatedTab :

  #---------------------------------------------------------------------
  def __init__( self, panel, notebook ) :
    self.notebook = notebook
    self.timer = wx.Timer(self)
    panel.Bind( wx.EVT_TIMER, self.update, self.timer )
    notebook.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self.activate )

  def update( self, event ) :
    pass

  #---------------------------------------------------------------------
  def activate( self, event ) :
    try:
      if self.notebook.GetCurrentPage() == self :
        self.timer.Start( 100 )
      else :
        self.timer.Stop()
    except Exception:
      pass

    if None != event :
      event.Skip()

