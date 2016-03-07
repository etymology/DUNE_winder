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

    if "100" == function[ 0 ] :
      isOn = bool( function[ 1 ] == "1" )
      self._io.debugLight.set( isOn )
    elif "101" == function[ 0 ] :
      length = float( function[ 1 ] )
      # $$$DEBUG - Subtract wire length by parameter.


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

    # Reset all values so we know what has changed.
    self._line = None
    lastX = self._x
    lastY = self._y
    lastZ = self._z
    self._functions = []
    lastVelocity = self._velocity

    self._currentLine = self._nextLine
    self._nextLine = self.gCode.getLine()

    # Interpret the next line.
    self.gCode.executeNextLine()

    # If an X/Y coordinate change is needed...
    if self._xyChange :
      # Make the move.
      self._io.plcLogic.setXY_Position( self._x, self._y, self._velocity )

      # Reset change flag.
      self._xyChange = False

    # If Z move...
    # $$$DEBUG - No coordinate move for Z.
    if self._zChange :
      # Make the move.
      self._io._zAxis.setDesiredPosition( self._z, self._velocity )

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
  def stop( self ):
    """
    """

    # If we are still executing this line,
    if self.gCode :
      self.gCode.backup()


  #---------------------------------------------------------------------
  def loadG_Code( self, lines ) :
    """
    Load G-Code file.

    Args:
      fileName: Full file name to G-Code to be loaded.
    """
    self.gCode = GCode( lines, self._callbacks )
    self._currentLine = 0
    self._nextLine = 0

  #---------------------------------------------------------------------
  def getCurrentLineNumber( self ) :
    """
    $$$DEBUG
    """

    # $$$DEBUG - Broken, does not always reflect current line.

    result = None
    if self.gCode :
      result = self._currentLine

    return result

  #---------------------------------------------------------------------
  def getNextLineNumber( self ) :
    """
    Return the next line of G-Code to be executed.

    Returns:
      The next line of G-Code to be executed.  None if there is no G-Code
      file currently loaded.
    """
    result = None
    if self.gCode :
      result = self.gCode.getLine()

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
  def setMaxVelocity( self, maxVelocity ) :
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
  def __init__( self, io ):
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
    self._callbacks.registerCallback( 'F', self._setVelocity )
    self._callbacks.registerCallback( 'G', self._runFunction )
    self._callbacks.registerCallback( 'N', self._setLine )

    self.gCode = None

    self._io = io

    self._maxVelocity = float( "inf" )   # <- No limit.
    self._velocity = 1.0                 # <- $$$DEBUG
    self._x = None
    self._y = None
    self._z = None
    self._line = 0
    self._xyChange = False
    self._zChange = False
    self._currentLine = None
    self._nextLine = None
    self._gCodeLog = None
    self._functions = []
