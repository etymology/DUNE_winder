###############################################################################
# Name: G_CodeHandlerBase.py
# Uses: Base class to handle G-Code execution.
# Date: 2016-03-30
# Author(s):
#   Andrew Que <aque@bb7.com>
# Notes:
#   This class handles all the machine specific G-Code functions, but not the
# execution of the motions.  That is, it knows how to decode and handle
# specific G-Code functions that modify X/Y or signal other functions.
###############################################################################

from Library.G_Code import G_CodeCallbacks

from Library.Geometry.Location import Location
from Library.Geometry.Segment import Segment
from Library.Geometry.Line import Line

class G_CodeHandlerBase :
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
    number = int( function[ 0 ] )
    self._functions.append( function )

    # Z-Latch.
    if 100 == number :
      # $$$DEBUG
      pass

    # Consumed wire for line.
    elif 101 == number :
      # Get the length from the parameter.
      length = float( function[ 1 ] )

      # Account for direction of travel.
      self._wireLength = length

    # Seek to transfer area
    elif 102 == number :

      startLocation = Location( self._lastX, self._lastY, self._lastZ )
      endLocation = Location( self._x, self._y, self._z )
      segment = Segment( startLocation, endLocation )

      if not self._geometry :
        raise Exception( "G-Code request for boundary move, but no geometry to use." )

      location = self._geometry.edges.intersectSegment( segment )

      self._x = location.x
      self._y = location.y

    # Seek between pins.
    elif 103 == number :
      pinA = int( function[ 1 ] )
      pinB = int( function[ 2 ] )

      if not self._calibration :
        raise Exception( "G-Code request for calibrated move, but no calibration to use." )

      pinA = self._calibration.getPinLocation( pinA )
      pinB = self._calibration.getPinLocation( pinB )
      center = pinA.center( pinB )
      self._x = center.x
      self._y = center.y

    # Clip coordinates.
    elif 104 == number :
      self._y = max( self._y, self._geometry.bottom )
      self._y = min( self._y, self._geometry.top )
      self._x = max( self._x, self._geometry.left )
      self._x = min( self._x, self._geometry.right )

  #---------------------------------------------------------------------
  def __init__( self ):
    """
    Constructor.
    """
    self._callbacks = G_CodeCallbacks()
    self._callbacks.registerCallback( 'X', self._setX )
    self._callbacks.registerCallback( 'Y', self._setY )
    self._callbacks.registerCallback( 'Z', self._setZ )
    self._callbacks.registerCallback( 'F', self._setVelocity )
    self._callbacks.registerCallback( 'G', self._runFunction )
    self._callbacks.registerCallback( 'N', self._setLine )

    self._functions = []

    # X/Y/Z positions.  Protected.
    self._x = None
    self._y = None
    self._z = None

    self._lastX = None
    self._lastY = None
    self._lastZ = None

    self._xyChange = False
    self._zChange = False

    # Current line number.
    self._line = 0

    # Wire length consumed by line.
    self._wireLength = 0

    # Velocity.
    self._maxVelocity = float( "inf" )   # <- No limit.
    self._velocity = 500.0               # <- $$$DEBUG

    self._geometry = None
    self._calibration = None
