###############################################################################
# Name: G_CodeHandler.py
# Uses: Hardware specific G-code handling.  Associates the G-code command to a
#       actual hardware.
# Date: 2016-02-11
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
from .Head import Head
from Library.G_Code import G_Code
from Machine.G_CodeHandlerBase import G_CodeHandlerBase

class G_CodeHandler( G_CodeHandlerBase ) :

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
  def setVelocityScale( self, scaleFactor=1.0 ) :
    """
    Set the velocity scale factor that limits the speed of all motions.

    Args:
      scaleFactor: New scale factor (typically between 0.0-1.0, although > 1 is
                   allowed).
    """
    self._velocityScale = scaleFactor

  #---------------------------------------------------------------------
  def getVelocityScale( self ) :
    """
    Get the velocity scale factor that limits the speed of all motions.

    Returns:
      Scale factor (typically between 0-1.0).
    """
    return self._velocityScale

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

    if self._io.plcLogic.isReady() and self._head.isIdle() :
      self._currentLine = self._nextLine

      isDone = self.isDone() or self.isOutOfWire()

      if not isDone :
        if self._delay > 0 :
          self._delay -= 1
        elif self._pauseCount < self._PAUSE :
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
    self._lastVelocity = self._velocity
    self._functions = []

    # Interpret the next line.
    self._gCode.executeNextLine( self._nextLine )

    # Calibrate the position (if we have a calibration file.)
    if self._calibration :
      offset = self._calibration.getOffset()
      if offset :
        self._x += offset.x
        self._y += offset.y

    velocity = min( self._velocity, self._maxVelocity )
    velocity *= self._velocityScale

    # If an X/Y coordinate change is needed...
    if self._xyChange :
      # Make the move.
      self._io.plcLogic.setXY_Position( self._x, self._y, velocity )

      # Reset change flag.
      self._xyChange = False

    # If Z move...
    if self._zChange :
      # Make the move.
      self._io.plcLogic.setZ_Position( self._z, velocity )

      # Reset change flag.
      self._zChange = False

    # Head movement...
    if self._headPositionChange :
      self._head.setPosition( self._headPosition, velocity )
      self._headPositionChange = False

    # Toggle the latch.
    if self._latchRequest :
      self._io.plcLogic.latch()
      self._latchRequest = False

    # Account for wire used.
    if self._wireLength :
      self._spool.subtract( self._wireLength )
      self._wireLength = 0

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
      geometry: Instance of machine geometry.
    """
    self._gCode = G_Code( lines, self._callbacks )
    self._currentLine = -1
    self._nextLine = -1
    self._geometry = geometry

    # $$$DEBUG - G-Code shouldn't need geometry--only calibration.
    self._head._geometry = geometry

    # Use current X/Y/Z position as starting points.
    # (These will be moved to self.lastN when the next line is executed.)
    self._x = self._io.xAxis.getPosition()
    self._y = self._io.yAxis.getPosition()
    self._z = self._io.zAxis.getPosition()

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
  def setG_CodeLog( self, gCodeLogFile ) :
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
  def __init__( self, io, spool, geometry=None ):
    """
    Constructor.

    Args:
      io: Instance of I/O map.
      spool: Instance of Spool.
      geometry: Machine geometry.
    """
    G_CodeHandlerBase.__init__( self )

    self._gCode = None

    self._io = io
    self._spool = spool

    self._head = Head( io, geometry )

    self._direction = 1
    self.runToLine = -1
    self._currentLine = None
    self._nextLine = None
    self._gCodeLog = None

    # Add a pause between every G-Code instructions by setting _PAUSE to
    # non-zero value.
    self._PAUSE = 0
    self._pauseCount = 0

    # Delay from G-Code file.
    self._delay = 0

    self._velocityScale = 1.0
