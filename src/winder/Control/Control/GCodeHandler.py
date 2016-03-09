###############################################################################
# Name: GCodeHandler.py
# Uses: Hardware specific G-code handling.  Associates the G-code command to a
#       actual hardware.
# Date: 2016-02-11
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
from Library.GCode import GCode, GCodeCallbacks

class GCodeHandler :
  #---------------------------------------------------------------------
  def _setX( self, x ) :
    """
    Callback for setting x-axis.

    Args:
      x: Desired x-axis location.

    Returns:
      None.
    """
    self._xyChange = True
    self._x = x

  #---------------------------------------------------------------------
  def _setY( self, y ) :
    """
    Callback for setting y-axis.

    Args:
      y: Desired y-axis location.

    Returns:
      None.
    """
    self._xyChange = True
    self._y = y


  #---------------------------------------------------------------------
  def _setZ( self, z ) :
    """
    Callback for setting z-axis.

    Args:
      z: Desired z-axis location.

    Returns:
      None.
    """
    self._zChange = True
    self._z = z

  #---------------------------------------------------------------------
  def _setVelocity( self, velocity ) :
    """
    Callback for setting velocity.

    Args:
      velocity: Desired maximum velocity.
    Returns:
      None.
    Notes:
      Limited to 'maxVelocity'.
    """
    if velocity < self._maxVelocity :
      self._velocity = velocity
    else :
      self._velocity = self._maxVelocity

  #---------------------------------------------------------------------
  def _setLine( self, line ) :
    """
    Callback for setting line number.

    Args:
      line: Current line number.

    Returns:
      None.
    """
    self._line = line

  #---------------------------------------------------------------------
  def _runFunction( self, function ) :
    """
    Callback for G-Code function.

    Args:
      function: Function number to execute.

    Returns:
      None.
    """

    self._functions.append( function )

    # Z-Latch.
    if "100" == function[ 0 ] :
      isOn = bool( function[ 1 ] == "1" )
      self._io.debugLight.set( isOn )
      self._io.plcLogic.initiateLatch()

    # Consumed wire for line.
    elif "101" == function[ 0 ] :
      length = float( function[ 1 ] )
      self._spool.subtract( length )


  #---------------------------------------------------------------------
  def isOutOfWire( self ) :
    """
    Check to see if spool is low on wire.

    Returns:
      True if spool is low on wire, False if not.
    """
    isOutOfWire = False
    if self._spool :
      isOutOfWire |= self._spool.isLow()

    return isOutOfWire

  #---------------------------------------------------------------------
  def isDone( self ) :
    """
    Check to see if the G-Code execution has finished.

    Returns:
      True if finished, false if not.
    """
    return self.gCode.isEndOfList()

  #---------------------------------------------------------------------
  def setLine( self, line ) :
    """
    Set the line number of G-Code to execute next.

    Args:
      line: New line number.
    """
    result = self.gCode.setLine( line )
    self._currentLine = self.gCode.getLine()
    return result

  #---------------------------------------------------------------------
  def poll( self ) :
    """
    Update the logic for executing this line of G-Code.

    Returns:
      True if either the G-Code list has finished, or if the spool is
      out of wire, False if not.
    """

    isDone = False

    if self._io.plcLogic.isReady() :
      self._currentLine = self.gCode.getLine()

      isDone = self.isDone() or self.isOutOfWire()

      if not isDone :
        self.runNextLine()

    return isDone

  #---------------------------------------------------------------------
  def runNextLine( self ):
    """
    Interpret and execute the next line of G-Code.
    """

    # Reset all values so we know what has changed.
    self._line = None
    lastX = self._x
    lastY = self._y
    lastZ = self._z
    self._functions = []
    lastVelocity = self._velocity

    # Interpret the next line.
    self.gCode.executeNextLine()

    # If an X/Y coordinate change is needed...
    if self._xyChange :
      # Make the move.
      self._io.plcLogic.setXY_Position( self._x, self._y, self._velocity )

      # Reset change flag.
      self._xyChange = False

    # If Z move...
    if self._zChange :
      # Make the move.
      self._io.plcLogic.setZ_Position( self._z, self._velocity )

      # Reset change flag.
      self._zChange = False

    # Place adjusted line in G-Code output log.
    if self._gCodeLog :

      line = ""

      #
      # Only log what has changed since the last line.
      #

      if None != self._line :
        line += "N" + str( self._line ) + " "

      if lastX != self._x :
        line += "X" + str( self._x ) + " "

      if lastY != self._y :
        line += "Y" + str( self._y ) + " "

      if lastZ != self._z :
        line += "Z" + str( self._z ) + " "

      if lastVelocity != self._velocity :
        line += "F" + str( self._velocity ) + " "

      for function in self._functions :
        line += "G" + str( function[ 0 ] ) + " "
        for parameter in function[ 1: ] :
          line += "P" + str( parameter ) + " "

      # Strip trailing space.
      line = line.strip()

      # Add line-feed.
      line += "\r\n"

      # Place in G-Code log.
      self._gCodeLog.write( line )

  #---------------------------------------------------------------------
  def loadG_Code( self, lines ) :
    """
    Load G-Code file.

    Args:
      fileName: Full file name to G-Code to be loaded.
    """
    self.gCode = GCode( lines, self._callbacks )
    self._currentLine = 0

  #---------------------------------------------------------------------
  def getCurrentLineNumber( self ) :
    """
    Get the current line number being executed/ready to execute.

    Returns:
      Line number being executed/ready to execute.  None if no G-Code is
      loaded.
    """

    result = None
    if self.gCode :
      result = self._currentLine

    return result

  #---------------------------------------------------------------------
  def getTotalLines( self ) :
    """
    Return the total number of G-Code lines for the current G-Code file.

    Returns:
      Total number of G-Code lines for the current G-Code file.  None if there
      is no G-Code file currently loaded.
    """
    result = None
    if self.gCode :
      result = self.gCode.getLines()

    return result

  #---------------------------------------------------------------------
  def setLimitVelocity( self, maxVelocity ) :
    """
    Set the maximum velocity at which any axis can move.  Useful to slow
    down operations.

    Args:
      maxVelocity: New maximum velocity.

    Note:
      Does not effect the whatever the motors are currently doing.
    """
    self._maxVelocity = maxVelocity

  #---------------------------------------------------------------------
  def setGCodeLog( self, gCodeLogFile ) :
    """
    Set a file to output resulting G-Code.

    Args:
      gCodeLogFile: File name to log data.
    """
    self._gCodeLog = open( gCodeLogFile, "a" )

  #---------------------------------------------------------------------
  def __init__( self, io, spool ):
    """
    Constructor.

    Args:
      io: Instance of I/O map.

    Returns:
      None.
    """
    self._callbacks = GCodeCallbacks()
    self._callbacks.registerCallback( 'X', self._setX )
    self._callbacks.registerCallback( 'Y', self._setY )
    self._callbacks.registerCallback( 'Z', self._setZ )
    self._callbacks.registerCallback( 'F', self._setVelocity )
    self._callbacks.registerCallback( 'G', self._runFunction )
    self._callbacks.registerCallback( 'N', self._setLine )

    self.gCode = None

    self._io = io
    self._spool = spool

    self._maxVelocity = float( "inf" )   # <- No limit.
    self._velocity = 1.0                 # <- $$$DEBUG
    self._x = None
    self._y = None
    self._z = None
    self._line = 0
    self._xyChange = False
    self._zChange = False
    self._currentLine = None
    self._gCodeLog = None
    self._functions = []
