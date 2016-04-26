###############################################################################
# Name: SystemTime.py
# Uses: Display the system time.
# Date: 2016-04-15
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
import wx
import datetime
from Remote import Remote

class SystemTime( Remote ) :

  #---------------------------------------------------------------------
  def convertTimeString( self, currentTime ) :
    currentTime = self.remote( "systemTime.get()" )
    try:
      currentTime = datetime.datetime.strptime( currentTime, "%Y-%m-%d %H:%M:%S.%f" )
    except ValueError:
      if "None" != currentTime :
        # Work around.  On some system (Windows) if the time 0 for microseconds,
        # it does not append the ".0" at the end.  So on a value error, just
        # try again with the .0 appended.
        currentTime += ".0"
        currentTime = datetime.datetime.strptime( currentTime, "%Y-%m-%d %H:%M:%S.%f" )

    return currentTime

  #---------------------------------------------------------------------
  def readTime( self ) :
    currentTime = self.remote( "systemTime.get()" )
    currentTime = self.convertTimeString( currentTime )

    return currentTime

  #---------------------------------------------------------------------
  def __init__( self, remote, panel, vbox ) :

    Remote.__init__( self, remote )

    staticBox   = wx.StaticBox( panel, wx.ID_ANY, "Time" )
    staticSizer = wx.StaticBoxSizer( staticBox, wx.VERTICAL )
    grideSizer = wx.GridSizer( 1, 2, 5, 5 )
    self.time  = wx.StaticText( panel, label='2000-01-01 12:00:00.000000' )
    self.timeDelta  = wx.StaticText( panel, label='000d 00h 00m 00.000s' )
    grideSizer.AddMany(
      [
        ( self.time  ), ( self.timeDelta, 0, wx.ALIGN_RIGHT )
      ]
    )

    self.startTime = self.readTime()

    staticSizer.Add( grideSizer )
    vbox.Add( staticSizer )

  #---------------------------------------------------------------------
  def deltaString( self, endTime ) :
    delta = endTime - self.startTime
    delta = delta.total_seconds()

    deltaString = ""
    days = int( delta / ( 60 * 60 * 24 ) )
    delta -= days * ( 60 * 60 * 24 )

    hours = int( delta / ( 60 * 60 ) )
    delta -= hours * ( 60 * 60 )

    minutes = int( delta / ( 60 ) )
    delta -= minutes * ( 60 )

    if days > 0 :
      deltaString += str( days ) + "d "

    if hours > 0 :
      deltaString += str( hours ) + "h "

    if minutes > 0 :
      deltaString += str( minutes ) + "m "

    deltaString += "{:2.3f}s".format( delta )

    return deltaString

  #---------------------------------------------------------------------
  def update( self ) :
    currentTime = self.readTime()

    #delta = currentTime - self.startTime
    #delta = delta.total_seconds()

    #self.time.SetLabel( "{:6.3f}".format( delta.total_seconds() ) )
    self.time.SetLabel( str( currentTime ) )

    #deltaString = ""
    #days = int( delta / ( 60 * 60 * 24 ) )
    #delta -= days * ( 60 * 60 * 24 )
    #
    #hours = int( delta / ( 60 * 60 ) )
    #delta -= hours * ( 60 * 60 )
    #
    #minutes = int( delta / ( 60 ) )
    #delta -= minutes * ( 60 )
    #
    #if days > 0 :
    #  deltaString += str( days ) + "d "
    #
    #if hours > 0 :
    #  deltaString += str( hours ) + "h "
    #
    #if minutes > 0 :
    #  deltaString += str( minutes ) + "m "
    #
    #deltaString += "{:2.3f}s".format( delta )
    #

    deltaString = self.deltaString( currentTime )
    self.timeDelta.SetLabel( deltaString )
