#==============================================================================
# Name: GCodeHandler.py
# Uses: Hardware specific G-code handling.  Associates the G-code command to a
#       actual hardware.
# Date: 2016-02-11
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-11 - QUE - Creation.
#==============================================================================
from IO.IO import io
from Library.GCode import GCode, GCodeCallbacks

class GCodeHandler :
  #---------------------------------------------------------------------
  def setX( self, x ) :
    """
    Callback for setting x-axis.

    Args:
      x: Desired x-axis location.
    Returns:
      None.
    """
    self.x = x

  #---------------------------------------------------------------------
  def setY( self, y ) :
    """
    Callback for setting y-axis.

    Args:
      y: Desired y-axis location.
    Returns:
      None.
    """
    self.y = y

  #---------------------------------------------------------------------
  def setLine( self, line ) :
    """
    Callback for setting line number.

    Args:
      line: Current line number.

    Returns:
      None.
    """
    self.line = line

  #---------------------------------------------------------------------
  def isDone( self ) :
    """
    Check to see if the G-Code execution has finished.

    Args:

    Returns:
      True if finished, false if not.
    """
    return self.gCode.isEndOfList()

  #---------------------------------------------------------------------
  def runNextLine( self ):
    """
    Interpret and execute the next line of G-Code.

    Args:
      None.

    Returns:
      None.
    """
    self.gCode.executeNextLine()
    io.xyAxis.setDesiredPosition( [ self.x, self.y ] )

    #
    # $$$DEBUG Log G-Code output.
    #

  #---------------------------------------------------------------------
  def __init__( self ):
    """
    Constructor.

    Args:
      None.

    Returns:
      None.
    """
    callbacks = GCodeCallbacks()
    callbacks.registerCallback( 'X', self.setX )
    callbacks.registerCallback( 'Y', self.setY )
    callbacks.registerCallback( 'N', self.setLine )

    # $$$DEBUG
    self.gCode = GCode( 'GCodeTest.txt', callbacks )

    self.x = 0
    self.y = 0
    self.line = 0
