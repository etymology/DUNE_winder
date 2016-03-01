###############################################################################
# Name: GCodeHandler.py
# Uses: Hardware specific G-code handling.  Associates the G-code command to a
#       actual hardware.
# Date: 2016-02-11
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-11 - QUE - Creation.
###############################################################################
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
  def setVelocity( self, velocity ) :
    """
    Callback for setting velocity.

    Args:
      velocity: Desired maximum velocity.
    Returns:
      None.
    """
    self.velocity = velocity

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
  def runFunction( self, function ) :
    """
    Callback for G-Code function.

    Args:
      function: Function number to execute.

    Returns:
      None.
    """
    isOn = bool( function[ 1 ] == "1" )
    #self.io.blinky.set( isOn )
    self.io.debugLight.set( isOn )

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
    #self.io.maxVelocity.set( self.velocity )
    #self.io.maxAcceleration.set( 10 )
    #self.io.maxDeceleration.set( 5 )
    #
    #self.io.xyAxis.setDesiredPosition( [ self.x, self.y ] )
    #self.io.moveType.set( 2 )
    self.io.plcLogic.setXY_Position( self.x, self.y, self.velocity )

    #
    # $$$DEBUG Log G-Code output.
    #

  #---------------------------------------------------------------------
  def loadG_Code( self, fileName ) :
    #self.gCode = GCode( fileName, callbacks )p
    pass

  #---------------------------------------------------------------------
  def __init__( self, io ):
    """
    Constructor.

    Args:
      io: Instance of I/O map.

    Returns:
      None.
    """
    callbacks = GCodeCallbacks()
    callbacks.registerCallback( 'X', self.setX )
    callbacks.registerCallback( 'Y', self.setY )
    callbacks.registerCallback( 'F', self.setVelocity )
    callbacks.registerCallback( 'G', self.runFunction )
    callbacks.registerCallback( 'N', self.setLine )

    self.gCode = None

    # $$$DEBUG
    self.gCode = GCode( 'GCodeA.txt', callbacks )

    self.io = io

    self.velocity = 1.0
    self.x = 0
    self.y = 0
    self.line = 0
