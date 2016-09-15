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

from Library.MathExtra import MathExtra
from Library.G_Code    import G_CodeCallbacks, G_CodeException

from Library.Geometry.Location import Location
from Library.Geometry.Line     import Line
from Library.Geometry.Box      import Box
from Library.Geometry.Segment  import Segment

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
  def _parameterExtract( self, parameters, start, finish, newType, errorMessage ) :
    """
    Extract the parameters and format them, raising an exception if they are
    incorrect.  Internal function.

    Args:
      parameters: String with parameters.
      start: Start location in string.
      end: End location in string (None to use end of line).
      newType: Type to cast (int, float, str, ect.)
      errorMessage: Error message to append if an incorrect format is encountered.

    Returns:
      An instance of 'newType' with data.

    Throws:
      G_CodeException if formatting is incorrect.
    """

    try :
      if None == finish :
        value = newType( parameters[ start ] )
      elif finish == start :
        value = newType( parameters[ start: ] )
      else :
        value = newType( parameters[ start:finish ] )
    except ( IndexError, AttributeError, ValueError ) as exception :
      data = [
        str( parameters )
      ]

      raise G_CodeException( "G-Code " + errorMessage + " function incorrectly formatted.", data )

    return value


  #---------------------------------------------------------------------
  def _runFunction( self, function ) :
    """
    Callback for G-Code function.

    Args:
      function: Function number to execute.

    Throws:
      G_CodeException if formatting is incorrect.
    """
    number = self._parameterExtract( function, 0, None, int, "base" )
    self._functions.append( function )

    # Toggle spool latch.
    if G_Codes.LATCH == number :
      self._latchRequest = True

    # Consumed wire for line.
    elif G_Codes.WIRE_LENGTH == number :
      # Get the length from the parameter.
      length = self._parameterExtract( function, 1, None, float, "wire length" )

      # Account for direction of travel.
      self._wireLength = length

    # Seek to transfer area
    # This will maintain the slope of the path between where the wire is
    # anchored and where the G-Code position is at present.
    elif G_Codes.SEEK_TRANSFER == number :

      # The position thus far.
      endLocation = Location( self._x, self._y, self._z )

      # Starting location based on anchor point.  Actual location has compensation
      # for pin diameter.
      startLocation = self._headCompensation.pinCompensation( endLocation )

      if None == startLocation :
        data = [
          str( self._headCompensation.anchorPoint() ),
          str( self._headCompensation.orientation() ),
          str( endLocation )
        ]

        raise G_CodeException( "G-Code seek transfer could not establish an anchor point.", data )

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
      pinNumberA = self._parameterExtract( function, 1, None, str, "pin center" )
      pinNumberB = self._parameterExtract( function, 2, None, str, "pin center" )
      axies = self._parameterExtract( function, 3, None, str, "pin center" )

      if not self._layerCalibration :
        raise G_CodeException( "G-Code request for calibrated move, but no layer calibration to use." )

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
      parameters = function[ 1: ]
      for parameter in parameters :
        axis = self._parameterExtract( parameter, 0, None, str, "offset" )
        offset = self._parameterExtract( parameter, 1, 1, float, "offset" )

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
      self._headPosition = self._parameterExtract( function, 1, None, int, "head location" )
      self._headPositionChange = True

    # Delay.
    elif G_Codes.DELAY == number :
      self._delay = self._parameterExtract( function, 1, None, int, "delay" )

    # Correct for the arm on the winder head.
    elif G_Codes.ANCHOR_POINT == number :
      # Get anchor point.
      pinNumber   = self._parameterExtract( function, 1, None, str, "anchor point" )
      orientation = self._parameterExtract( function, 2, None, str, "anchor point" )

      # Get the pin center.
      pin = self._layerCalibration.getPinLocation( pinNumber )
      pin = pin.add( self._layerCalibration.offset )

      if "0" == orientation :
        orientation = None

      self._headCompensation.anchorPoint( pin )
      self._headCompensation.orientation( orientation )

    # Correct for the arm on the winder head.
    elif G_Codes.ARM_CORRECT == number :

      # $$$DEBUG - Fix constants.
      z = self._machineCalibration.zFront
      if 1 == self._headPosition :
        z = self._layerCalibration.zFront
      elif 2 == self._headPosition :
        z = self._layerCalibration.zBack
      elif 3 == self._headPosition :
        z = self._machineCalibration.zBack

      currentLocation = Location( self._x, self._y, z )

      if   MathExtra.isclose( self._y, self._machineCalibration.transferTop ) \
        or MathExtra.isclose( self._y, self._machineCalibration.transferBottom ) :
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

            # Get position where line crosses transfer area.
            location = line.intersection( edge )

            # Compensate for head's arm.
            self._y = self._headCompensation.correctY( location )
            self._x = location.x
      else :
        self._y = self._headCompensation.correctY( currentLocation )

      self._xyChange = True

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

# Unit test code.
if __name__ == "__main__":

  from Library.G_Code import G_Code
  from Library.MathExtra import MathExtra
  from Machine.DefaultCalibration import DefaultMachineCalibration, DefaultLayerCalibration
  from Machine.HeadCompensation import HeadCompensation

  # Child of G-Code handler to do testing.
  class G_CodeTester( G_CodeHandlerBase ) :
    def __init__( self ) :
      # Create default calibrations and setup head compensation.
      machineCalibration = DefaultMachineCalibration()
      layerCalibration = DefaultLayerCalibration( None, None, "V" )
      headCompensation = HeadCompensation( machineCalibration )

      # Some G-Code test lines.
      lines = [
        "X10 Y10 Z10",
        "G103 PF800 PF800 PXY",
        "G109 PF1200 PTR G103 PF1199 PF1198 PXY G102"
      ]

      # Construct G-Code handler.
      G_CodeHandlerBase.__init__( self, machineCalibration, headCompensation )
      self.useLayerCalibration( layerCalibration )

      # Setup G-Code interpreter.
      gCode = G_Code( lines, self._callbacks )

      #
      # Run tests.
      #

      # Simple X/Y/Z seek.
      gCode.executeNextLine( 0 )
      assert( Location( self._x, self._y, self._z ) == Location( 10, 10, 10 ) )

      # Pin seek.
      gCode.executeNextLine( 1 )
      location = layerCalibration.getPinLocation( "F800" )
      location = location.add( layerCalibration.offset )
      location.z = 0
      assert( location == Location( self._x, self._y ) )

      # Anchor point to transfer area check.
      # Anchor on pin F1, then center between F2399 and F2398.  Preserve the slope
      # of the line and seek to a transfer area.  This should intercept the bottom.
      gCode.executeNextLine( 2 )
      assert( MathExtra.isclose( self._x, 887.701845335 ) )
      assert( MathExtra.isclose( self._y, 0 ) )

  # Create instance of test class, thereby running tests.
  tester = G_CodeTester()
