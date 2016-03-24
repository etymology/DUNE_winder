###############################################################################
# Name: LayerU_Recipe.py
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

from RecipeGenerator import RecipeGenerator
from Path3d import Path3d
from G_CodePath import G_CodePath
from G_CodeFunctions.WireLengthG_Code import WireLengthG_Code
from G_CodeFunctions.SeekTransferG_Code import SeekTransferG_Code
from G_CodeFunctions.LatchG_Code import LatchG_Code

class LayerV_Recipe( RecipeGenerator ) :
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
  def __init__( self, geometry, windsOverride=None ) :
    """
    Constructor.  Does all calculations.

    Args:
      geometry: Instance of LayerV_Layout that specifies parameters for recipe
        generation.
      windsOverride: Set to specify the number to winds to make before stopping.
        Normally left to None.
    """

    self.nodesFront = []
    self.nodesBack = []

    #----------------------------------
    # Create nodes.
    # This is a list of pins starting with the bottom left corner moving in
    # a clockwise direction.
    #----------------------------------
    x = 0
    y = 0
    for parameter in geometry.gridParameters :
      count = parameter[ 0 ]
      xInc  = parameter[ 1 ]
      yInc  = parameter[ 2 ]
      x += parameter[ 3 ]
      y += parameter[ 4 ]

      for position in range( 0, count ) :
        self.nodesFront.append( Location( x, y, 0 ) )
        self.nodesBack.append( Location( x, y, geometry.depth ) )

        x += xInc
        y += yInc

      # Backup for last position.
      x -= xInc
      y -= yInc

    #----------------------------------
    # Create net list.
    # This is a path of node indexes specifying the order in which they are
    # connected.
    #----------------------------------

    # Define the first few net locations.
    # All following locations are just modifications of this initial set.
    self.net = \
    [
      2 * geometry.rows + geometry.columns - 1,
      geometry.columns - 1,
      0,
      2 * geometry.rows + 2 * geometry.columns - 2,
      geometry.columns,
      2 * geometry.rows + geometry.columns - 2
    ]

    # Number of items in above list.
    repeat = len( self.net )

    # Total number of pins.
    pins = 2 * geometry.rows + 2 * geometry.columns + 1

    # Initial direction.
    direction = 1

    # All remaining net locations are based off a simple the previous locations.
    for netNumber in range( repeat, pins ) :
      self.net.append( self.net[ netNumber - repeat ] + direction )
      direction = -direction

    #----------------------------------
    # Crate motions necessary to wind the above pattern.
    #----------------------------------

    # A wire can land in one of four locations along a pin: upper/lower
    # left/right.  The angle of these locations are defined here.
    _180 = math.radians( 180 )
    ul = -geometry.angle
    ll = -geometry.angle + _180
    ur = geometry.angle
    lr = geometry.angle + _180

    # G-Code path is the motions taken by the machine to wind the layer.
    self.gCodePath = G_CodePath()

    # The node path is a path of points that are connect together.  Used to calculate
    # the amount of wire actually dispensed.
    self.nodePath = Path3d()

    #
    # Initial seek position.
    #
    startLocation = Location( geometry.deltaX * geometry.columns, geometry.wireSpacing / 2 )

    # Current net.
    net = 0
    self.nodePath.pushOffset( self.location( net ), 0, geometry.pinRadius, geometry.angle )
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
      # To upper middle moving from lower-right to upper-left starting on front side.
      #

      # Get the two pins we need to be between.
      center = self.center( net, -1 )

      length1 = \
        self.nodePath.pushOffset(
          self.location( net ),
          geometry.partialZ_Front,
          geometry.pinRadius,
          lr
        )

      length2 = \
        self.nodePath.pushOffset(
          self.location( net ),
          geometry.partialZ_Back,
          geometry.pinRadius,
          ll
        )

      wireLine = Line.fromLocations( self.gCodePath.last, center )
      destination = wireLine.intersection( geometry.lineTop )
      self.gCodePath.pushG_Code( WireLengthG_Code( length1 ) )
      self.gCodePath.pushG_Code( SeekTransferG_Code( SeekTransferG_Code.TOP ) )
      self.gCodePath.push( destination.x, destination.y, geometry.frontZ )
      self.gCodePath.push( destination.x, destination.y, geometry.partialZ_Front ) # Partial Z

      center = self.center( net, +1 )
      self.gCodePath.push( center.x, destination.y, geometry.partialZ_Front )
      self.gCodePath.pushG_Code( WireLengthG_Code( length2 ) )

      self.gCodePath.pushG_Code( LatchG_Code( LatchG_Code.BACK ) )
      self.gCodePath.push( center.x, destination.y, geometry.backZ )
      self.gCodePath.push( center.x, center.y - geometry.overshoot, geometry.backZ )

      net += 1

      #
      # To lower left column moving from upper-right to lower-left starting on back side.
      #

      length1 = \
        self.nodePath.pushOffset(
          self.location( net ),
          geometry.partialZ_Back,
          geometry.pinRadius,
          ll
        )

      length2 = \
        self.nodePath.pushOffset(
          self.location( net ),
          geometry.partialZ_Front,
          geometry.pinRadius,
          geometry.angle
        )

      # Pin on lower rear left.
      center = self.center( net, -1 )
      wireLine = Line.fromLocations( self.gCodePath.last, center )
      destinationA = wireLine.intersection( geometry.lineBottom )
      destinationB = wireLine.intersection( geometry.lineLeft )

      if destinationA.x > destinationB.x :
        destination = destinationA
      else :
        destination = destinationB

      self.gCodePath.pushG_Code( SeekTransferG_Code( SeekTransferG_Code.BOTTOM_LEFT ) )
      self.gCodePath.pushG_Code( WireLengthG_Code( length1 ) )
      self.gCodePath.push( destination.x, destination.y, geometry.backZ )
      self.gCodePath.push( destination.x, destination.y, geometry.partialZ_Back )  # Partial Z

      # To second pin on lower front left.
      center = self.center( net, +1 )
      wireLine = Line.fromLocations( self.gCodePath.last, center )
      self.gCodePath.push( self.gCodePath.last.x, center.y, geometry.partialZ_Back )
      self.gCodePath.pushG_Code( WireLengthG_Code( length2 ) )
      self.gCodePath.pushG_Code( LatchG_Code( LatchG_Code.FRONT ) )
      self.gCodePath.push( self.gCodePath.last.x, center.y, geometry.frontZ )
      self.gCodePath.push(
        center.x - geometry.pinRadius + geometry.overshoot,
        center.y,
        geometry.frontZ
      )

      self.gCodePath.push(
        center.x - geometry.pinRadius + geometry.overshoot,
        geometry.bottom,
        geometry.frontZ
      )

      net += 1

      #
      # To lower left row moving from upper-left to lower-right starting on front side.
      #
      length1 = \
        self.nodePath.pushOffset(
          self.location( net ),
          geometry.partialZ_Front,
          geometry.pinRadius,
          ur
        )

      length2 = \
        self.nodePath.pushOffset(
          self.location( net ),
          geometry.partialZ_Back,
          geometry.pinRadius,
          ul
        )

      center = self.center( net, -1 )
      self.gCodePath.pushG_Code( WireLengthG_Code( length1 ) )
      self.gCodePath.push( center.x, self.gCodePath.last.y, geometry.frontZ )
      self.gCodePath.pushG_Code( LatchG_Code( LatchG_Code.BACK ) )
      self.gCodePath.push( center.x, self.gCodePath.last.y, geometry.backZ )

      center = self.center( net, +1 )
      self.gCodePath.pushG_Code( WireLengthG_Code( length2 ) )
      self.gCodePath.push( center.x, self.gCodePath.last.y, geometry.backZ )
      self.gCodePath.push( center.x, center.y + geometry.overshoot, geometry.backZ )

      net += 1

      #
      # To upper middle from lower-left to upper-right starting on back side.
      #
      length1 = \
        self.nodePath.pushOffset(
          self.location( net ),
          geometry.partialZ_Back,
          geometry.pinRadius,
          ll
        )

      length2 = \
        self.nodePath.pushOffset(
          self.location( net ),
          geometry.partialZ_Front,
          geometry.pinRadius,
          lr
        )

      # Get the two pins we need to be between.
      center = self.center( net, +1 )

      wireLine = Line.fromLocations( self.gCodePath.last, center )

      destination = wireLine.intersection( geometry.lineTop )
      self.gCodePath.pushG_Code( WireLengthG_Code( length1 ) )
      self.gCodePath.push( destination.x, destination.y, geometry.backZ )
      self.gCodePath.push( destination.x, destination.y, geometry.partialZ_Back ) # Partial Z

      center = self.center( net, +1 )
      self.gCodePath.pushG_Code( WireLengthG_Code( length2 ) )
      self.gCodePath.push( center.x, destination.y, geometry.partialZ_Back )
      self.gCodePath.pushG_Code( LatchG_Code( LatchG_Code.FRONT ) )
      self.gCodePath.push( center.x, destination.y, geometry.frontZ )

      self.gCodePath.push( center.x, center.y - geometry.overshoot, geometry.frontZ )

      net += 1

      #
      # To lower right column from upper-left to lower-right starting on front side.
      #

      length1 = \
        self.nodePath.pushOffset(
          self.location( net ),
          geometry.partialZ_Front,
          geometry.pinRadius,
          lr
        )
      location = self.location( net )
      location.x += geometry.rightExtention + geometry.pinRadius
      length2  = \
        self.nodePath.pushOffset(
          location,
          geometry.partialZ_Front,
          geometry.pinRadius,
          ll
        )

      length2 += \
        self.nodePath.pushOffset( location, geometry.partialZ_Back, geometry.pinRadius, lr )
      length2 += \
        self.nodePath.pushOffset(
          self.location( net ),
          geometry.partialZ_Back,
          geometry.pinRadius,
          ul
        )

      # Lower right front side.
      center = self.center( net, +1 )
      wireLine = Line.fromLocations( self.gCodePath.last, center )
      destinationA = wireLine.intersection( geometry.lineBottom )
      destinationB = wireLine.intersection( geometry.lineRight )

      self.gCodePath.pushG_Code( WireLengthG_Code( length1 ) )
      if destinationA.x < destinationB.x :
        destination = destinationA
        self.gCodePath.push( destination.x, destination.y, geometry.frontZ )
        self.gCodePath.push( destination.x, destination.y, geometry.partialZ_Front )
        self.gCodePath.push( destinationB.x, destination.y, geometry.partialZ_Front )
      else :
        destination = destinationB
        self.gCodePath.push( destination.x, destination.y, geometry.frontZ )
        self.gCodePath.push( destination.x, destination.y, geometry.partialZ_Front )

      # Lower right backside.
      center = self.center( net, -1 )
      wireLine = Line.fromLocations( self.gCodePath.last, center )
      self.gCodePath.pushG_Code( WireLengthG_Code( length2 ) )
      self.gCodePath.push( self.gCodePath.last.x, center.y, geometry.partialZ_Front )
      self.gCodePath.pushG_Code( LatchG_Code( LatchG_Code.BACK ) )
      self.gCodePath.push( self.gCodePath.last.x, center.y, geometry.backZ )
      self.gCodePath.push(
        center.x + geometry.pinRadius - geometry.overshoot,
        center.y,
        geometry.backZ
      )

      self.gCodePath.push(
        center.x + geometry.pinRadius - geometry.overshoot,
        geometry.bottom,
        geometry.backZ
      )

      net += 1

      #
      # Lower right row from lower-right to lower-left starting on back side.
      #
      length1 = \
        self.nodePath.pushOffset(
          self.location( net ),
          geometry.partialZ_Back,
          geometry.pinRadius,
          ul
        )

      length2 = self.nodePath.pushOffset( self.location( net ), 0, geometry.pinRadius, ur )

      center = self.center( net, +1 )
      self.gCodePath.pushG_Code( WireLengthG_Code( length1 ) )
      self.gCodePath.push( center.x, self.gCodePath.last.y, geometry.backZ )
      self.gCodePath.pushG_Code( LatchG_Code( LatchG_Code.FRONT ) )
      self.gCodePath.push( center.x, self.gCodePath.last.y, geometry.frontZ )

      center = self.center( net, -1 )
      self.gCodePath.pushG_Code( WireLengthG_Code( length2 ) )
      self.gCodePath.push( center.x, self.gCodePath.last.y, geometry.frontZ )
      self.gCodePath.push( center.x, center.y + geometry.overshoot, geometry.frontZ )

      net += 1

