###############################################################################
# Name: LayerUV_Recipe.py
# Uses: Common functions shared by U and V layer recipe.
# Date: 2016-04-06
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import math

from Library.Geometry.Location import Location
from Library.Geometry.Segment import Segment
from Library.Geometry.Line import Line

from G_CodeFunctions.WireLengthG_Code import WireLengthG_Code
from G_CodeFunctions.SeekTransferG_Code import SeekTransferG_Code
from G_CodeFunctions.LatchG_Code import LatchG_Code
from G_CodeFunctions.ClipG_Code import ClipG_Code
from G_CodeFunctions.PinCenterG_Code import PinCenterG_Code
from G_CodeFunctions.OffsetG_Code import OffsetG_Code

from RecipeGenerator import RecipeGenerator, Z_Axis
from Path3d import Path3d
from G_CodePath import G_CodePath

class LayerUV_Recipe( RecipeGenerator ) :

  #---------------------------------------------------------------------
  def __init__( self, geometry ) :
    """
    Constructor.

    Args:
      geometry - Instance (or child) of UV_LayerGeometry.
    """
    RecipeGenerator.__init__( self, geometry )

    self.basePath = Path3d()
    self.orientations = {}
    self.centering = {}

    # G-Code path is the motions taken by the machine to wind the layer.
    self.gCodePath = G_CodePath()

    # The node path is a path of points that are connect together.  Used to calculate
    # the amount of wire actually dispensed.
    self.nodePath = Path3d()

    self.z = Z_Axis( self.gCodePath, self.geometry, Z_Axis.FRONT )

  #---------------------------------------------------------------------
  @staticmethod
  def _pinCompare( pinA, pinB ) :
    """
    Compare two pin numbers.  Used for sorting a list of pin names.
    Debug function.

    Args:
      pinA: First pin.
      pinB: Second pin.

    Returns:
      0 = pins are identical, 1 = pinA < pinB, -1 = pinA > pinB.
    """
    pinA_Side = pinA[ 0 ]
    pinB_Side = pinB[ 0 ]
    pinA_Number = int( pinA[ 1: ] )
    pinB_Number = int( pinB[ 1: ] )

    result = 0
    if pinA_Side < pinB_Side :
      result = 1
    elif pinA_Side > pinB_Side :
      result = -1
    elif pinA_Number < pinB_Number :
      result = -1
    elif pinA_Number > pinB_Number :
      result = 1

    return result

  #---------------------------------------------------------------------
  def _printNodes( self ) :
    """
    Print a sorted list of all the pin names.  Debug function.
    """
    for node in sorted( self.nodes, cmp=LayerUV_Recipe._pinCompare ) :
      side = node[ 0 ]
      pin = node[ 1: ]
      location = str( self.nodes[ node ] )[ 1:-1 ].replace( ' ', '' )
      print side + "," + pin + "," + location

  #---------------------------------------------------------------------
  def _nextNet( self ) :
    """
    Advance to the next net in list.  Pushes length calculation to next G-Code
    and builds the path node list.

    Returns:
      True if there is an other net, False net list if finished.
    """

    result = False

    # Get the next net.
    self.netIndex += 1

    if self.netIndex < len( self.net ) :

      # The orientation specifies one of four points on the pin the wire will
      # contact: upper/lower left/right.  This comes from the orientation
      # look-up table.
      net = self.net[ self.netIndex ]
      orientation = self.orientations[ net ]

      # Location of the the next pin.
      location = self.location( self.netIndex )

      # Add the pin location to the base path.
      self.basePath.push( location.x, location.y, location.z )

      # Add the offset pin location to the node path and get the length of this
      # piece of wire.
      length = self.nodePath.pushOffset( location, self.geometry.pinRadius, orientation )

      # Push a G-Code length function to the next G-Code command to specify the
      # amount of wire consumed by this move.
      self.gCodePath.pushG_Code( WireLengthG_Code( length ) )

      result = True

    return result

  #---------------------------------------------------------------------
  def _pinCenterTarget( self, axis="XY" ) :
    """
    Setup the G-Code function class for targeting the left/right of the next
    pin in the net.  Based on the pin this will figure out which side of the
    pin the wire should target.

    Args:
      axis: Either "X", "Y" or "XY" for which coordinates will be used in the
            targeting.
    Returns:
      An instance of PinCenterG_Code (G_CodeFunction).
    """
    net = self.net[ self.netIndex ]
    direction = self.centering[ net ]
    pinNames = self.pinNames( self.netIndex, direction )
    return PinCenterG_Code( pinNames, axis )

  #-------------------------------------------------------------------
  def _createNode( self, grid, orientation, side, depth, startPin, direction ) :
    """
    Create nodes.
    This is a list of pins starting with the bottom left corner moving in
    a clockwise direction.

    Args:
      grid: Grid parameters from geometry.
      orientation: True/False for orientation.
      side: F/B for front/back.
      depth: Thickness of layer.
      startPin: Starting pin number closest to (0,0).
      direction: +1/-1 for incrementing starting pin number.

    Returns:
      Adds to 'self.nodes'.
      Nothing is returned.
    """

    # A wire can land in one of four locations along a pin: upper/lower
    # left/right.  The angle of these locations are defined here.
    angle180 = math.radians( 180 )
    ul = -self.geometry.angle
    ll = self.geometry.angle + angle180
    ur = self.geometry.angle
    lr = -self.geometry.angle + angle180

    if orientation :
      sideA = "F"
      sideB = "B"
    else :
      sideA = "B"
      sideB = "F"

    orientations = \
    {       # Left  Top   Right  Bottom
      sideA : [ ur,   ll,   ll,    ur ],
      sideB : [ lr,   lr,   ul,    ul ]
    }
    if orientation :
                  # Left  Top   Right  Bottom
      centering = [ +1,   -1,   +1,    -1     ]
    else :
      centering = [ -1,   +1,   -1,    +1     ]

    x = 0
    y = 0
    setIndex = 0
    pinNumber = startPin
    for parameter in grid :
      count = parameter[ 0 ]
      xInc  = parameter[ 1 ]
      yInc  = parameter[ 2 ]
      x += parameter[ 3 ]
      y += parameter[ 4 ]

      for position in range( 0, count ) :
        location = Location( round( x, 5 ), round( y, 5 ), depth )
        pin = side + str( pinNumber )
        self.nodes[ pin ] = location
        self.orientations[ pin ] = orientations[ side ][ setIndex ]
        self.centering[ pin ]    = centering[ setIndex ]

        pinNumber += direction

        if 0 == pinNumber :
          pinNumber = self.geometry.pins
        elif pinNumber > self.geometry.pins :
          pinNumber = 1

        x += xInc
        y += yInc

      # Backup for last position.
      x -= xInc
      y -= yInc
      setIndex += 1

  #-------------------------------------------------------------------
  def _createNet( self, windSteps, direction=1 ) :
    """
    Create net list.  This is a path of node indexes specifying the order in which they are
    connected.

    Args:
      windSteps: Number of steps needed to complete the wind.
      direction: Initial direction (1 or -1).
    """
    # Number of items in above list.
    repeat = len( self.net )

    # # Initial direction.
    # direction = 1

    # All remaining net locations are based off a simple the previous locations.
    for netNumber in range( repeat, windSteps ) :
      pin = self.net[ netNumber - repeat ]
      side = pin[ 0 ]
      number = int( pin[ 1: ] )
      self.net.append( side + str( number + direction ) )
      direction = -direction

  #---------------------------------------------------------------------
  def _wrapCenter( self ) :
    """
    Sequence for wrapping around the top in the center.
    """

    # To center pin.
    if self._nextNet() :
      self.gCodePath.pushG_Code( self._pinCenterTarget( "XY" ) )
      self.gCodePath.pushG_Code( SeekTransferG_Code() )
      self.gCodePath.push()
      self.z.set( Z_Axis.PARTIAL )


    if self._nextNet() :
      # Hook pin and line up with next pin on other side.
      self.gCodePath.pushG_Code( self._pinCenterTarget( "X" ) )
      self.gCodePath.push()

      # Go to other side and seek past pin so it is hooked with next move.
      self.z.set( Z_Axis.OTHER_SIDE )
      self.gCodePath.pushG_Code( self._pinCenterTarget( "XY" ) )
      self.gCodePath.pushG_Code( OffsetG_Code( y=-self.geometry.overshoot ) )
      self.gCodePath.push()

  #---------------------------------------------------------------------
  def _wrapEdge( self, direction ) :
    """
    Sequence for wrapping around the bottom left/right edges.

    Args:
      direction: -1 for left side, 1 for right side.
    """

    if self._nextNet() :
      self.gCodePath.pushG_Code( self._pinCenterTarget( "XY" ) )
      self.gCodePath.pushG_Code( SeekTransferG_Code() )
      self.gCodePath.push()
      self.z.set( Z_Axis.PARTIAL )

    if self._nextNet() :
      self.gCodePath.pushG_Code( self._pinCenterTarget( "Y" ) )
      self.gCodePath.push()
      self.z.set( Z_Axis.OTHER_SIDE )
      self.gCodePath.pushG_Code( self._pinCenterTarget( "X" ) )
      offset = ( self.geometry.pinRadius - self.geometry.overshoot ) * direction
      self.gCodePath.pushG_Code( OffsetG_Code( x=offset ) )
      self.gCodePath.push()
      self.gCodePath.pushG_Code( OffsetG_Code( y=-self.geometry.overshoot ) )
      self.gCodePath.pushG_Code( ClipG_Code() )
      self.gCodePath.push()

    if self._nextNet() :

      # Get the angle of the line going directly to the center of the destination
      # pins.
      centerA = self.center( self.netIndex - 1, -direction )
      centerA.y -= self.geometry.overshoot
      centerB = self.center( self.netIndex, direction )
      segment = Segment( centerA, centerB )
      line = Line.fromSegment( segment )

      # If the angle isn't too steep, go directly to the destination.  Otherwise,
      # just go to the Z-transfer area in Y.
      # (We could always go to the Z-transfer area in Y, but this allows a
      # faster path as long as the angle is large enough).
      angle = direction * line.getAngle()
      if angle >= self.geometry.minAngle and centerA.y > centerB.y :
        self.gCodePath.pushG_Code( self._pinCenterTarget( "XY" ) )
        self.gCodePath.pushG_Code( SeekTransferG_Code() )
        self.gCodePath.push()
      else:
        self.gCodePath.pushG_Code( OffsetG_Code( y=-1000 ) )
        self.gCodePath.pushG_Code( ClipG_Code() )
        self.gCodePath.push()
        self.gCodePath.pushG_Code( self._pinCenterTarget( "X" ) )
        self.gCodePath.push()

      self.z.set( Z_Axis.PARTIAL )

    if self._nextNet() :
      self.gCodePath.pushG_Code( self._pinCenterTarget( "X" ) )
      self.gCodePath.push()
      self.z.set( Z_Axis.OTHER_SIDE )
      self.gCodePath.pushG_Code( self._pinCenterTarget( "Y" ) )
      self.gCodePath.pushG_Code( OffsetG_Code( y=self.geometry.overshoot ) )
      self.gCodePath.push()

  #---------------------------------------------------------------------
  def _wind( self, startLocation, direction, windsOverride=None ) :
    """
    Wind the layer using the class parameters.

    Args:
      startLocation: Point to start from.
      windsOverride: Set to specify the number to winds to make before stopping.
        Normally left to None.

    Returns:
      Sets up self.gCodePath, self.nodePath, and self.basePath.
      Nothing is returned by function.
    """

    # Current net.
    self.netIndex = 0

    net = self.net[ self.netIndex ]
    orientation = self.orientations[ net ]

    self.nodePath.pushOffset(
      self.location( self.netIndex ),
      self.geometry.pinRadius,
      self.orientations[ net ]
    )

    self.gCodePath.push( startLocation.x, startLocation.y, self.geometry.frontZ )
    self.basePath.push( startLocation.x, startLocation.y, self.geometry.frontZ )

    # To wind half the layer, divide by half and the number of steps in a
    # circuit.
    totalCount = self.geometry.pins / 12

    # # $$$DEBUG - Temp--this will wind the entire layer.
    # totalCount *= 2
    # totalCount += 10

    if windsOverride :
      totalCount = windsOverride

    # A single loop completes one circuit of the APA starting and ending on the
    # lower left.
    for count in range( 1, totalCount + 1 ) :
      self._wrapCenter()
      self._wrapEdge( direction )
      self._wrapCenter()
      self._wrapEdge( -direction )
