###############################################################################
# Name: GCodeHandler.py
# Uses: Hardware specific G-code handling.  Associates the G-code command to a
#       actual hardware.
# Date: 2016-02-11
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
from Library.GCode import GCode, GCodeCallbacks

from Library.Geometry.Location import Location
from Library.Geometry.Segment import Segment
from Library.Geometry.Line import Line

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
      # Get the length from the parameter.
      length = float( function[ 1 ] )

      # Account for direction of travel.  In reverse, the wire is actually
      # going back onto the spool.
      length *= self._direction
      self._spool.subtract( length )

    # Seek to transfer area
    elif "102" == function[ 0 ] :

      startLocation = Location( self._lastX, self._lastY, self._lastZ )
      endLocation = Location( self._x, self._y, self._z )
      segment = Segment( startLocation, endLocation )

      location = self._geometry.edges.intersectSegment( segment )
      self._x = location.x
      self._y = location.y

    # Seek between pins.
    elif "103" == function[ 0 ] :
      pinA = int( function[ 1 ] )
      pinB = int( function[ 2 ] )

      if not self._calibration :
        raise Exception( "G-Code request for calibrated move, but no calibration to use." )

      pinA = self._calibration.getPinLocation( pinA )
      pinB = self._calibration.getPinLocation( pinB )
      center = pinA.center( pinB )
      self._x = center.x
      self._y = center.y


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

    startLine = 0
    endLine = self._gCode.getLineCount() - 1

    if -1 != self.runToLine :
      if 1 == self._direction :
        endLine = self.runToLine - 1
      else :
        startLine = self.runToLine - 1

    isDone = False
    isDone |= 1 == self._direction and self._nextLine >= endLine
    isDone |= 1 != self._direction and self._nextLine <= startLine

    return isDone

  #---------------------------------------------------------------------
  def getTotalLines( self ) :
    """
    Return the total number of G-Code lines for the current G-Code file.

    Returns:
      Total number of G-Code lines for the current G-Code file.  None if there
      is no G-Code file currently loaded.
    """
    result = None
    if self._gCode :
      result = self._gCode.getLineCount()

    return result

  #---------------------------------------------------------------------
  def getLine( self ) :
    """
    Get the current line number being executed/ready to execute.

    Returns:
      Line number being executed/ready to execute.  None if no G-Code is
      loaded.
    """

    result = None
    if self._gCode :
      result = self._currentLine

    return result

  #---------------------------------------------------------------------
  def setLine( self, line ) :
    """
    Set the line number of G-Code to execute next.

    Args:
      line: New line number.
    """

    isError = True
    if line >= -1 and line < self._gCode.getLineCount() :
      isError = False
      self._nextLine = line
      self._currentLine = line

    return isError

  #---------------------------------------------------------------------
  def setDirection( self, isForward ) :
    """
    Set the direction of G-Code execution.

    Args:
      isForward: True for normal direction, False to run in reverse.
    """
    if isForward :
      self._direction = 1
    else :
      self._direction = -1

  #---------------------------------------------------------------------
  def getDirection( self ) :
    """
    Get the direction of G-Code execution.

    Returns
      True for normal direction, False to run in reverse.
    """
    return 1 == self._direction

  #---------------------------------------------------------------------
  def stop( self ) :
    """
    Stop the running G-Code.  Call when interrupting G-Code sequence.
    """

    # If we are interrupting a running line, set it as the next line to run.
    if not self._io.plcLogic.isReady() :
      self._nextLine -= self._direction

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
      self._currentLine = self._nextLine

      isDone = self.isDone() or self.isOutOfWire()

      if not isDone :
        if self._pauseCount < self._PAUSE :
          self._pauseCount += 1
        else :
          self._pauseCount = 0
          self._nextLine += self._direction
          self.runNextLine()

    return isDone

  #---------------------------------------------------------------------
  def runNextLine( self ):
    """
    Interpret and execute the next line of G-Code.
    """

    # Reset all values so we know what has changed.
    self._line = None
    self._lastX = self._x
    self._lastY = self._y
    self._lastZ = self._z
    self._functions = []
    self._lastVelocity = self._velocity

    # Interpret the next line.
    self._gCode.executeNextLine( self._nextLine )

    # Calibrate the position (if we have a calibration file.)
    if self._calibration :
      offset = self._calibration.getOffset()
      self.x += offset.x
      self.y += offset.y

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
      # Only log what has changed since the self._last line.
      #

      if None != self._line :
        line += "N" + str( self._line ) + " "

      if self._lastX != self._x :
        line += "X" + str( self._x ) + " "

      if self._lastY != self._y :
        line += "Y" + str( self._y ) + " "

      if self._lastZ != self._z :
        line += "Z" + str( self._z ) + " "

      if self._lastVelocity != self._velocity :
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
  def loadG_Code( self, lines, geometry ) :
    """
    Load G-Code file.

    Args:
      fileName: Full file name to G-Code to be loaded.
    """
    self._gCode = GCode( lines, self._callbacks )
    self._currentLine = -1
    self._nextLine = -1
    self._geometry = geometry

  #---------------------------------------------------------------------
  def isG_CodeLoaded( self ) :
    """
    Check to see if there is G-Code loaded.

    Returns:
      True if G-Code is loaded, False if not.
    """
    return None != self._gCode

  #---------------------------------------------------------------------
  def fetchLines( self, center, delta ) :
    """
    Fetch a sub-set of the G-Code self.lines.  Useful for showing what has
    recently executed, and what is to come.

    Args:
      center: Where to center the list.
      delta: Number of entries to read +/- center.

    Returns:
      List of G-Code lines, padded with empty lines if needed.  Empty list if
      no G-Code is loaded.
    """
    result = []
    if self._gCode :
      result = self._gCode.fetchLines( center, delta )

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
  def useCalibration( self, calibration ) :
    """
    Give handler an instance of Calibration to use for pin locations.  Must
    be called before running G-Code.
    """
    self._calibration = calibration

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

    self._gCode = None

    self._io = io
    self._spool = spool

    self._maxVelocity = float( "inf" )   # <- No limit.
    self._velocity = 500.0                 # <- $$$DEBUG
    self._lastX = None
    self._lastY = None
    self._lastZ = None
    self._x = None
    self._y = None
    self._z = None
    self._line = 0
    self._xyChange = False
    self._zChange = False
    self._direction = 1
    self.runToLine = -1
    self._currentLine = None
    self._nextLine = None
    self._gCodeLog = None
    self._functions = []
    self._calibration = None
    self._geometry = None

    # Add a pause between G-Code instructions by setting _PAUSE to non-zero value.
    self._PAUSE = 0
    self._pauseCount = 0
