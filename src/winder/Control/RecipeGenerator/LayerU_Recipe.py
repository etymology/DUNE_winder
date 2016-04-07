###############################################################################
# Name:
# Uses:
# Date: 2016-04-05
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import math
import sys

from Library.Geometry.Location import Location
from Library.Geometry.Segment import Segment
from Library.Geometry.Line import Line

from LayerUV_Recipe import LayerUV_Recipe
from Path3d import Path3d
from G_CodePath import G_CodePath

from G_CodeFunctions.WireLengthG_Code import WireLengthG_Code
from G_CodeFunctions.SeekTransferG_Code import SeekTransferG_Code
from G_CodeFunctions.LatchG_Code import LatchG_Code
from G_CodeFunctions.ClipG_Code import ClipG_Code
from G_CodeFunctions.PinCenterG_Code import PinCenterG_Code
from G_CodeFunctions.OffsetG_Code import OffsetG_Code

class LayerU_Recipe( LayerUV_Recipe ) :
  """

    *  *  *  *  *  *  *  *
            / \/ \
  *        /  /\  \       *
         /   /  \  \
  *     /  /      \ \
      /   /        \  \   *
  *  /   /          \  \
   /   /              \ \
  *   /                \  *
   \ /                  \
    *  *  *  *  *  *  *  *

  This layer begins in the bottom right corner, runs diagonally to the
  top center, then to the bottom most pin on the far left, the left most
  pin on the bottom, one pin right of center, and the second from the bottom
  """

  #---------------------------------------------------------------------
  @staticmethod
  def pinCompare( pinA, pinB ) :
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
  def __init__( self, geometry, windsOverride=None ) :
    """
    Constructor.  Does all calculations.

    Args:
      geometry: Instance of LayerV_Layout that specifies parameters for recipe
        generation.
      windsOverride: Set to specify the number to winds to make before stopping.
        Normally left to None.
    """

    LayerUV_Recipe.__init__( self )

    self.totalPins = geometry.pins

    self._createNode( geometry.gridFront, "F", geometry.partialZ_Front, 1, 1 )
    self._createNode( geometry.gridBack,  "B", geometry.partialZ_Back, 401, -1 )

    #----------------------------------
    # Create net list.
    # This is a path of node indexes specifying the order in which they are
    # connected.
    #----------------------------------

    # Define the first few net locations.
    # All following locations are just modifications of this initial set.
    self.net = \
    [
      "F" + str( 1 ),
      "F" + str( geometry.columns + 1 ),
      "B" + str( 2 * geometry.columns + geometry.rows + 2 ),
      "B" + str( geometry.columns + geometry.rows + 1 ),
      "F" + str( 2 * geometry.columns + 2 ),
      "F" + str( 2 * geometry.columns + 1 ),
      "B" + str( geometry.columns + geometry.rows + 2 ),
      "B" + str( 2 * geometry.columns + geometry.rows + 1 ),
      "F" + str( geometry.columns + 2 ),
      "F" + str( 2 * geometry.columns + 2 * geometry.rows + 1 ),
      "B" + str( geometry.rows + 2 ),
      "B" + str( geometry.rows ),
    ]

    # Total number of steps to do a complete wind.
    windSteps = 4 * geometry.rows + 4 * geometry.columns - 3

    self._createNet( windSteps )

    #----------------------------------
    # Crate motions necessary to wind the above pattern.
    #----------------------------------

    # A wire can land in one of four locations along a pin: upper/lower
    # left/right.  The angle of these locations are defined here.
    angle180 = math.radians( 180 )
    ul = -geometry.angle
    ll = -geometry.angle + angle180
    ur = geometry.angle
    lr = geometry.angle + angle180

    # G-Code path is the motions taken by the machine to wind the layer.
    self.gCodePath = G_CodePath()

    # The node path is a path of points that are connect together.  Used to calculate
    # the amount of wire actually dispensed.
    self.nodePath = Path3d()

    #
    # Initial seek position.
    #
    startLocation = Location( 0, 0 )

    radius = geometry.pinRadius

    # Current net.
    net = 0
    self.nodePath.pushOffset( self.location( net ), radius, ll )
    self.gCodePath.push( startLocation.x, startLocation.y, geometry.frontZ )
    net += 1

    # To wind half the layer, divide by half and the number of steps in a
    # circuit.
    totalCount = geometry.pins / ( 2 * 6 )

    if windsOverride :
      totalCount = windsOverride

    # A single loop completes one circuit of the APA starting and ending on the
    # lower left.
    for count in range( 1, totalCount + 1 ) :
      #
      # To upper middle from lower-left to upper-right starting on back side.
      #
      length = self.nodePath.pushOffset( self.location( net ), radius, ll )

      # Get the two pins we need to be between.
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( net, +1 ), "XY" ) )
      self.gCodePath.pushG_Code( SeekTransferG_Code() )
      self.gCodePath.pushG_Code( WireLengthG_Code( length ) )
      self.gCodePath.push()

      self.gCodePath.push( z=geometry.partialZ_Front ) # Partial Z

      # 7
      net += 1
      length = self.nodePath.pushOffset( self.location( net ), radius, lr )

      self.gCodePath.pushG_Code( WireLengthG_Code( length ) )
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( net, -1 ), "X" ) )
      self.gCodePath.push()

      self.gCodePath.pushG_Code( LatchG_Code( LatchG_Code.BACK ) )
      self.gCodePath.push( z=geometry.backZ )
      self.gCodePath.push( z=geometry.frontZ )

      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( net, -1 ), "Y" ) )
      self.gCodePath.pushG_Code( OffsetG_Code( y=-geometry.overshoot ) )
      self.gCodePath.push()

      # 8
      net += 1

      #
      # To lower right column from upper-left to lower-right starting on front side.
      #

      length = self.nodePath.pushOffset( self.location( net ), radius, ur )

      # Lower right front side.

      # Seek what is likely the bottom.
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( net, +1 ), "XY" ) )
      self.gCodePath.pushG_Code( SeekTransferG_Code() )
      self.gCodePath.pushG_Code( WireLengthG_Code( length ) )
      self.gCodePath.push()

      self.gCodePath.pushG_Code( LatchG_Code( LatchG_Code.FRONT ) )
      self.gCodePath.push( z=geometry.backZ )
      self.gCodePath.push( z=geometry.partialZ_Back )

      # 9
      net += 1
      length = self.nodePath.pushOffset( self.location( net ), radius, ul )

      # Lower right backside.
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( net, +1 ), "X" ) )
      self.gCodePath.pushG_Code( WireLengthG_Code( length ) )
      self.gCodePath.push()

      self.gCodePath.push( z=geometry.frontZ )

      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( net, +1 ), "Y" ) )
      self.gCodePath.pushG_Code( OffsetG_Code( y=radius + geometry.overshoot ) )
      self.gCodePath.push()

      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( net, +1 ), "X" ) )
      self.gCodePath.pushG_Code( OffsetG_Code( x=geometry.overshoot ) )
      self.gCodePath.pushG_Code( ClipG_Code() )
      self.gCodePath.push()


      # 10
      net += 1

      #
      # Lower right row from lower-right to lower-left starting on back side.
      #
      length = self.nodePath.pushOffset( self.location( net ), radius, ul )

      centerA = self.center( net - 1, -1 )
      centerA.y -= geometry.overshoot
      centerB = self.center( net,     +1 )
      self.gCodePath.pushG_Code( WireLengthG_Code( length ) )

      # Get the angle of the line going directly to the center of the destination
      # pins.
      segment = Segment( centerA, centerB )
      line = Line.fromSegment( segment )

      # If the angle isn't too steep, go directly to the destination.  Otherwise,
      # just go to the Z-transfer area in Y.
      # (We could always go to the Z-transfer area in Y, but this allows a
      # faster path as long as the angle is large enough).
      if line.getAngle() >= geometry.minAngle and centerA.y > centerB.y :
        self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( net, -1 ), "XY" ) )
        self.gCodePath.pushG_Code( SeekTransferG_Code() )
        self.gCodePath.push()
      else:
        self.gCodePath.pushG_Code( OffsetG_Code( x=1000 ) )
        self.gCodePath.pushG_Code( ClipG_Code() )
        self.gCodePath.push()

      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( net, -1 ), "Y" ) )
      self.gCodePath.push()

      break

      # 11
      net += 1
      length = self.nodePath.pushOffset( self.location( net ), radius, lr )

      self.gCodePath.pushG_Code( LatchG_Code( LatchG_Code.FRONT ) )
      self.gCodePath.push( z=geometry.backZ )
      self.gCodePath.push( z=geometry.partialZ_Back )

      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( net, -1 ), "X" ) )
      self.gCodePath.pushG_Code( WireLengthG_Code( length ) )
      self.gCodePath.push()

      self.gCodePath.push( z=geometry.frontZ )
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( net, -1 ), "Y" ) )
      self.gCodePath.pushG_Code( OffsetG_Code( y=geometry.overshoot ) )
      self.gCodePath.push()

      # 12
      net += 1



      #
      # To upper middle moving from lower-right to upper-left starting on front side.
      #

      length = self.nodePath.pushOffset( self.location( net ), radius, lr )


      self.gCodePath.pushG_Code( WireLengthG_Code( length ) )
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( net, -1 ) ) )
      self.gCodePath.pushG_Code( SeekTransferG_Code() )
      self.gCodePath.push()
      self.gCodePath.push( z=geometry.partialZ_Front ) # Partial Z

      # 1
      net += 1
      length = self.nodePath.pushOffset( self.location( net ), radius, ll )
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( net, -1 ), "X" ) )
      self.gCodePath.push()
      self.gCodePath.pushG_Code( WireLengthG_Code( length ) )

      self.gCodePath.pushG_Code( LatchG_Code( LatchG_Code.BACK ) )
      self.gCodePath.push( z=geometry.backZ )
      self.gCodePath.push( z=geometry.frontZ )
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( net, -1 ), "XY" ) )
      self.gCodePath.pushG_Code( OffsetG_Code( y=-geometry.overshoot ) )
      self.gCodePath.push()

      # 2
      net += 1

      #
      # To lower left column moving from upper-right to lower-left starting on back side.
      #

      length = self.nodePath.pushOffset( self.location( net ), radius, ul )


      # Pin on lower rear left.

      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( net, +1 ), "XY" ) )
      self.gCodePath.pushG_Code( SeekTransferG_Code() )
      self.gCodePath.pushG_Code( WireLengthG_Code( length ) )
      self.gCodePath.push()

      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( net, +1 ), "X" ) )
      self.gCodePath.pushG_Code( OffsetG_Code( x=-1000 ) )
      self.gCodePath.pushG_Code( SeekTransferG_Code() )
      self.gCodePath.push()

      self.gCodePath.pushG_Code( LatchG_Code( LatchG_Code.FRONT ) )
      self.gCodePath.push( z=geometry.backZ )
      self.gCodePath.push( z=geometry.partialZ_Back )  # Partial Z

      # 3
      net += 1
      length = self.nodePath.pushOffset( self.location( net ), radius, ur )

      # To second pin on lower front left.
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( net, +1 ), "Y" ) )
      self.gCodePath.push()

      self.gCodePath.pushG_Code( WireLengthG_Code( length ) )
      self.gCodePath.push( z=geometry.frontZ )

      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( net, +1 ), "X" ) )
      self.gCodePath.pushG_Code( OffsetG_Code( x=geometry.overshoot - radius ) )
      self.gCodePath.push()

      self.gCodePath.pushG_Code( OffsetG_Code( y=-geometry.overshoot ) )
      self.gCodePath.pushG_Code( ClipG_Code() )
      self.gCodePath.push()

      # 4
      net += 1

      #
      # To lower left row moving from upper-left to lower-right starting on front side.
      #
      length = self.nodePath.pushOffset( self.location( net ), radius, ur )

      self.gCodePath.pushG_Code( WireLengthG_Code( length ) )

      # Get the angle of the line going directly to the center of the destination
      # pins.
      centerA = self.center( net - 1, +1 )
      centerA.y -= geometry.overshoot
      centerB = self.center( net, -1 )
      segment = Segment( centerA, centerB )
      line = Line.fromSegment( segment )

      # If the angle isn't too steep, go directly to the destination.  Otherwise,
      # just go to the Z-transfer area in Y.
      # (We could always go to the Z-transfer area in Y, but this allows a
      # faster path as long as the angle is large enough).
      if -line.getAngle() >= geometry.minAngle and centerA.y > centerB.y :
        self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( net, -1 ), "XY" ) )
        self.gCodePath.pushG_Code( SeekTransferG_Code() )
        self.gCodePath.push()
      else:
        self.gCodePath.pushG_Code( OffsetG_Code( y=-1000 ) )
        self.gCodePath.pushG_Code( ClipG_Code() )
        self.gCodePath.push()

      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( net, -1 ), "X" ) )
      self.gCodePath.push()
      self.gCodePath.push( z=geometry.partialZ_Front )


      # 5
      net += 1
      length = self.nodePath.pushOffset( self.location( net ), radius, ll )
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( net, -1 ), "X" ) )
      self.gCodePath.pushG_Code( WireLengthG_Code( length ) )
      self.gCodePath.push()

      self.gCodePath.pushG_Code( LatchG_Code( LatchG_Code.BACK ) )
      self.gCodePath.push( z=geometry.backZ )
      self.gCodePath.push( z=geometry.frontZ )

      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( net, +1 ), "Y" ) )
      self.gCodePath.pushG_Code( OffsetG_Code( y=geometry.overshoot ) )
      self.gCodePath.push()

      # 6
      net += 1

