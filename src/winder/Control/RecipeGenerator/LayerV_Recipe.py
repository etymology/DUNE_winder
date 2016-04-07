###############################################################################
# Name: LayerV_Recipe.py
# Uses: Recipe generation for V-layer.
# Date: 2016-03-23
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import math
import sys

from Library.Geometry.Location import Location
from Library.Geometry.Segment import Segment
from Library.Geometry.Line import Line

from RecipeGenerator import Z_Axis
from LayerUV_Recipe import LayerUV_Recipe
from Path3d import Path3d
from G_CodePath import G_CodePath

from G_CodeFunctions.WireLengthG_Code import WireLengthG_Code
from G_CodeFunctions.SeekTransferG_Code import SeekTransferG_Code
from G_CodeFunctions.LatchG_Code import LatchG_Code
from G_CodeFunctions.ClipG_Code import ClipG_Code
from G_CodeFunctions.PinCenterG_Code import PinCenterG_Code
from G_CodeFunctions.OffsetG_Code import OffsetG_Code

class LayerV_Recipe( LayerUV_Recipe ) :
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

  # $$$ #---------------------------------------------------------------------
  # $$$ @staticmethod
  # $$$ def pinCompare( pinA, pinB ) :
  # $$$   pinA_Side = pinA[ 0 ]
  # $$$   pinB_Side = pinB[ 0 ]
  # $$$   pinA_Number = int( pinA[ 1: ] )
  # $$$   pinB_Number = int( pinB[ 1: ] )
  # $$$
  # $$$   result = 0
  # $$$   if pinA_Side < pinB_Side :
  # $$$     result = 1
  # $$$   elif pinA_Side > pinB_Side :
  # $$$     result = -1
  # $$$   elif pinA_Number < pinB_Number :
  # $$$     result = -1
  # $$$   elif pinA_Number > pinB_Number :
  # $$$     result = 1
  # $$$
  # $$$   return result

  #---------------------------------------------------------------------
  def nextNet( self, orientation ) :
    """
    $$$DEBUG
    """
    self.netIndex += 1
    location = self.location( self.netIndex )
    length = self.nodePath.pushOffset( location, self.geometry.pinRadius, orientation )
    self.gCodePath.pushG_Code( WireLengthG_Code( length ) )

  #---------------------------------------------------------------------
  def sideMove( self, direction ) :
    """
    Operation in which the wire is wrapped on a pin column and then seeks a
    near-by row pin.
    """
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
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( self.netIndex, -1 ), "XY" ) )
      self.gCodePath.pushG_Code( SeekTransferG_Code() )
      self.gCodePath.push()
    else:
      self.gCodePath.pushG_Code( OffsetG_Code( y=-1000 ) )
      self.gCodePath.pushG_Code( ClipG_Code() )
      self.gCodePath.push()

    self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( self.netIndex, -1 ), "X" ) )
    self.gCodePath.push()


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

    self.geometry = geometry
    self.totalPins = geometry.pins

    #----------------------------------
    # Create nodes.
    # This is a list of pins starting with the bottom left corner moving in
    # a clockwise direction.
    #----------------------------------
    x = 0
    y = 0
    pinNumber = 1
    for parameter in geometry.gridFront :
      count = parameter[ 0 ]
      xInc  = parameter[ 1 ]
      yInc  = parameter[ 2 ]
      x += parameter[ 3 ]
      y += parameter[ 4 ]

      for position in range( 0, count ) :
        location = Location( round( x, 5 ), round( y, 5 ), 0 )
        self.nodes[ "F" + str( pinNumber ) ] = location

        location = Location( round( x, 5 ), round( y, 5 ), geometry.depth )
        backPin = ( ( geometry.rows - pinNumber ) % geometry.pins ) + 1
        self.nodes[ "B" + str( backPin ) ] = location

        pinNumber += 1

        x += xInc
        y += yInc

      # Backup for last position.
      x -= xInc
      y -= yInc

    #for node in sorted( self.nodes, cmp=LayerV_Recipe.pinCompare ) :
    #  side = node[ 0 ]
    #  pin = node[ 1: ]
    #  location = str( self.nodes[ node ] )[ 1:-1 ].replace( ' ', '' )
    #  print side + "," + pin + "," + location
    #
    #return

    #----------------------------------
    # Create self.netIndex list.
    # This is a path of node indexes specifying the order in which they are
    # connected.
    #----------------------------------

    # Define the first few self.netIndex locations.
    # All following locations are just modifications of this initial set.
    self.net = \
    [
      "F" + str( 2 * geometry.rows + geometry.columns ),
      "F" + str( geometry.columns ),
      "B" + str( geometry.rows + 2 * geometry.columns ),
      "B" + str( geometry.rows ),
      "F" + str( 1 ),
      "F" + str( 2 * geometry.rows + 2 * geometry.columns - 1 ),
      "B" + str( geometry.rows + 1 ),
      "B" + str( geometry.rows + 2 * geometry.columns - 1 ),
      "F" + str( geometry.columns + 1 ),
      "F" + str( 2 * geometry.rows + geometry.columns - 1 ),
      "B" + str( geometry.rows + geometry.columns + 1 ),
      "B" + str( geometry.rows + geometry.columns - 1 ),
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
    startLocation = Location( geometry.deltaX * geometry.columns, geometry.wireSpacing / 2 )

    # Current self.netIndex.
    self.netIndex = 0
    self.nodePath.pushOffset( self.location( self.netIndex ), geometry.pinRadius, ur )
    self.gCodePath.push( startLocation.x, startLocation.y, geometry.frontZ )

    # To wind half the layer, divide by half and the number of steps in a
    # circuit.
    totalCount = geometry.pins / ( 2 * 6 )

    if windsOverride :
      totalCount = windsOverride

    z = Z_Axis( self.gCodePath, geometry, geometry.frontZ )

    # A single loop completes one circuit of the APA starting and ending on the
    # lower left.
    for count in range( 1, totalCount + 1 ) :

      # 1
      self.nextNet( lr )
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( self.netIndex, -1 ) ) )
      self.gCodePath.pushG_Code( SeekTransferG_Code() )
      self.gCodePath.push()
      z.set( Z_Axis.PARTIAL_FRONT )


      # 2
      self.nextNet( ll )
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( self.netIndex, -1 ), "X" ) )
      self.gCodePath.push()
      z.set( Z_Axis.BACK )
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( self.netIndex, -1 ), "XY" ) )
      self.gCodePath.pushG_Code( OffsetG_Code( y=-geometry.overshoot ) )
      self.gCodePath.push()


      # 3
      self.nextNet( ll )
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( self.netIndex, +1 ), "XY" ) )
      self.gCodePath.pushG_Code( SeekTransferG_Code() )
      self.gCodePath.push()
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( self.netIndex, +1 ), "X" ) )
      self.gCodePath.pushG_Code( OffsetG_Code( x=-1000 ) )
      self.gCodePath.pushG_Code( SeekTransferG_Code() )
      self.gCodePath.push()
      z.set( Z_Axis.PARTIAL_BACK )


      # 4
      self.nextNet( ur )
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( self.netIndex, +1 ), "Y" ) )
      self.gCodePath.push()
      z.set( Z_Axis.FRONT )
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( self.netIndex, +1 ), "X" ) )
      self.gCodePath.pushG_Code( OffsetG_Code( x=geometry.overshoot - geometry.pinRadius ) )
      self.gCodePath.push()
      self.gCodePath.pushG_Code( OffsetG_Code( y=-geometry.overshoot ) )
      self.gCodePath.pushG_Code( ClipG_Code() )
      self.gCodePath.push()


      # 5
      self.nextNet( ur )
      self.sideMove( -1 )
      z.set( Z_Axis.PARTIAL_FRONT )

      # 6
      self.nextNet( ul )
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( self.netIndex, -1 ), "X" ) )
      self.gCodePath.push()
      z.set( Z_Axis.BACK )
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( self.netIndex, +1 ), "Y" ) )
      self.gCodePath.pushG_Code( OffsetG_Code( y=geometry.overshoot ) )
      self.gCodePath.push()

      # 7
      self.nextNet( ll )
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( self.netIndex, +1 ), "XY" ) )
      self.gCodePath.pushG_Code( SeekTransferG_Code() )
      self.gCodePath.push()
      z.set( Z_Axis.PARTIAL_BACK )

      # 8
      self.nextNet( lr )
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( self.netIndex, -1 ), "X" ) )
      self.gCodePath.push()
      z.set( Z_Axis.FRONT )
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( self.netIndex, -1 ), "Y" ) )
      self.gCodePath.pushG_Code( OffsetG_Code( y=-geometry.overshoot ) )
      self.gCodePath.push()

      # 9
      self.nextNet( lr )
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( self.netIndex, +1 ), "XY" ) )
      self.gCodePath.pushG_Code( SeekTransferG_Code() )
      self.gCodePath.push()
      z.set( Z_Axis.PARTIAL_FRONT )

      # 10
      self.nextNet( ul )
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( self.netIndex, +1 ), "Y" ) )
      self.gCodePath.push()
      z.set( Z_Axis.BACK )
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( self.netIndex, +1 ), "X" ) )
      self.gCodePath.pushG_Code( OffsetG_Code( x=geometry.pinRadius - geometry.overshoot ) )
      self.gCodePath.push()
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( self.netIndex, +1 ), "Y" ) )
      self.gCodePath.pushG_Code( OffsetG_Code( y=-geometry.overshoot ) )
      self.gCodePath.pushG_Code( ClipG_Code() )
      self.gCodePath.push()


      # 11
      self.nextNet( ul )
      self.sideMove( 1 )

      # 12
      self.nextNet( ur )
      z.set( Z_Axis.PARTIAL_BACK )
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( self.netIndex, -1 ), "X" ) )
      self.gCodePath.push()
      z.set( Z_Axis.FRONT )
      self.gCodePath.pushG_Code( PinCenterG_Code( self.pinNames( self.netIndex, -1 ), "Y" ) )
      self.gCodePath.pushG_Code( OffsetG_Code( y=geometry.overshoot ) )
      self.gCodePath.push()
