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
from Library.Geometry.Line    import Line
from Library.Geometry.Box     import Box
from Library.Geometry.Segment import Segment

from .G_Codes import G_Codes

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

    # Toggle spool latch.
    if G_Codes.LATCH == number :
      self._latchRequest = True

    # Consumed wire for line.
    elif G_Codes.WIRE_LENGTH == number :
      # Get the length from the parameter.
      length = float( function[ 1 ] )

      # Account for direction of travel.
      self._wireLength = length

    # Seek to transfer area
    elif G_Codes.SEEK_TRANSFER == number :

      startLocation = Location( self._lastX, self._lastY, self._lastZ )
      endLocation = Location( self._x, self._y, self._z )
      segment = Segment( startLocation, endLocation )

      # Box that defines the Z hand-off edges.
      edges = \
        Box(
          self._machineCalibration.transferLeft,
          self._machineCalibration.transferTop,
          self._machineCalibration.transferRight,
          self._machineCalibration.transferBottom
        )

      location = edges.intersectSegment( segment )

      self._x = location.x
      self._y = location.y
      self._xyChange = True

    # Seek between pins.
    elif G_Codes.PIN_CENTER == number :
      pinNumberA = function[ 1 ]
      pinNumberB = function[ 2 ]
      axies = function[ 3 ]

      if not self._layerCalibration :
        raise Exception( "G-Code request for calibrated move, but no layer calibration to use." )

      pinA = self._layerCalibration.getPinLocation( pinNumberA )
      pinB = self._layerCalibration.getPinLocation( pinNumberB )
      center = pinA.center( pinB )
      center = center.add( self._layerCalibration.offset )

      if "X" in axies :
        self._x = center.x
        self._xyChange = True

      if "Y" in axies :
        self._y = center.y
        self._xyChange = True

    # Clip coordinates.
    elif G_Codes.CLIP == number :
      oldX = self._x
      oldY = self._y

      self._y = max( self._y, self._machineCalibration.transferBottom )
      self._y = min( self._y, self._machineCalibration.transferTop )
      self._x = max( self._x, self._machineCalibration.transferLeft )
      self._x = min( self._x, self._machineCalibration.transferRight )

      self._xyChange |= ( oldX != self._x ) or ( oldY != self._y )

    # Offset coordinates.
    elif G_Codes.OFFSET == number :
      for parameter in function[ 1: ] :
        axis = parameter[ 0 ]
        offset = float( parameter[ 1: ] )

        if "X" == axis :
          self._x += offset
          self._xyChange = True

        if "Y" == axis :
          self._y += offset
          self._xyChange = True

        if "Z" == axis :
          self._z += offset
          self._xyChange = True

    # Head position.
    elif G_Codes.HEAD_LOCATION == number :
      self._headPosition = int( function[ 1 ] )
      self._headPositionChange = True

    # Delay.
    elif G_Codes.DELAY == number :
      self._delay = int( function[ 1 ] )

    # Correct for the arm on the winder head.
    elif G_Codes.ANCHOR_POINT == number :
      # Get anchor point.
      pinNumberA = function[ 1 ]
      pinNumberB = function[ 2 ]
      offsetDirection = None
      if len( function ) > 2 :
        offsetDirection = function[ 3 ]

      # Get the pin center.
      pinA = self._layerCalibration.getPinLocation( pinNumberA )
      pinB = self._layerCalibration.getPinLocation( pinNumberB )
      center = pinA.center( pinB )
      center = center.add( self._layerCalibration.offset )

      # Compensate for pin diameter (if requested).
      if "U" == offsetDirection :
        center._y += self._machineCalibration.pinDiameter / 2
      elif "D" == offsetDirection :
        center._y -= self._machineCalibration.pinDiameter / 2
      elif "L" == offsetDirection :
        center._x -= self._machineCalibration.pinDiameter / 2
      elif "R" == offsetDirection :
        center._x += self._machineCalibration.pinDiameter / 2

      self._headCompensation.anchorPoint( center )

    # Correct for the arm on the winder head.
    elif G_Codes.ARM_CORRECT == number :

      z = self._machineCalibration.zFront
      if 1 == self._headPosition :
        z = self._layerCalibration.partialZ_Front
      elif 2 == self._headPosition :
        z = self._layerCalibration.partialZ_Back
      elif 3 == self._headPosition :
        z = self._machineCalibration.zBack

      currentLocation = Location( self._x, self._y, z )
      # print "Correct", currentLocation, "anchored at", self._headCompensation.anchorPoint(),  # $$$
      y = round( self._y, 4 )
      top    = round( self._machineCalibration.transferTop, 4 )
      bottom = round( self._machineCalibration.transferBottom, 4 )
      if   y == top \
        or y == bottom :
          #print "Correct X",  # $$$
          self._x = self._headCompensation.correctX( currentLocation )

          edge = None

          # Check to see if the adjusted position shifted past the right/left
          # transfer area.
          if self._x > self._machineCalibration.transferRight :
            edge = Line( Line.VERTICLE_SLOPE, self._machineCalibration.transferRight )
          elif self._x < self._machineCalibration.transferLeft :
            edge = Line( Line.VERTICLE_SLOPE, self._machineCalibration.transferLeft )

          # Do correct for transfer area (if needed)...
          if edge :
            # Make a line along the path from the anchor point to the
            # destination.
            start = self._headCompensation.anchorPoint()
            line = Line.fromLocations( start, currentLocation )

            #print "Over-travel", end   # $$$

            # Get position where line crosses transfer area.
            location = line.intersection( edge )
            #print "Clip", location,  # $$$

            # Compensate for head's arm.
            self._y = self._headCompensation.correctY( location )
            self._x = location.x
      else :
        #print "Correct Y",   # $$$
        self._y = self._headCompensation.correctY( currentLocation )

      #print Location( self._x, self._y, z )   # $$$

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
  def setVelocity( self, velocity ) :
    """
    Set the velocity (override the commanded velocity until next command).

    Args:
      velocity: New velocity.
    """
    self._velocity = velocity

  #---------------------------------------------------------------------
  def useLayerCalibration( self, layerCalibration ) :
    """
    Give handler an instance of layerCalibration to use for pin locations.  Must
    be called before running G-Code.

    Args:
      layerCalibration: Calibration specific to the layer being wound.
    """
    self._layerCalibration = layerCalibration

  #---------------------------------------------------------------------
  def getLayerCalibration( self ) :
    """
    Return the layer calibration currently in use.

    Returns:
      Instance of LayerCalibration.  None if no calibration loaded.
    """
    return self._layerCalibration

  #---------------------------------------------------------------------
  def setInitialLocation( self, x, y, headLocation ) :
    """
    Set the last machine location.  This is needed when loading a new recipe
    because seeks to transfer areas need to know form where to begin.

    Args:
      location: Coordinates of starting position.
    """

    self._startLocationX = x
    self._startLocationY = y
    self._startHeadLocation = headLocation

  #---------------------------------------------------------------------
  def __init__( self, machineCalibration, headCompensation ):
    """
    Constructor.

    Args:
      machineCalibration: Machine calibration instance.
      headCompensation: Instance of HeadCompensation.
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
    self._headPosition = None

    self._lastX = None
    self._lastY = None
    self._lastZ = None

    self._xyChange = False
    self._zChange = False
    self._headPositionChange = False

    self._latchRequest = False

    # Current line number.
    self._line = 0

    # Wire length consumed by line.
    self._wireLength = 0

    # Velocity.
    self._maxVelocity = float( "inf" )   # <- No limit.
    self._velocity = float( "inf" )

    self._layerCalibration = None
    self._machineCalibration = machineCalibration
    self._headCompensation = headCompensation

    self._startLocationX = None
    self._startLocationY = None
    self._startHeadLocation = None

