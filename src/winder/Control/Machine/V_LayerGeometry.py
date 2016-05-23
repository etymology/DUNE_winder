###############################################################################
# Name: V_LayerGeometry.py
# Uses: Geometry specific to the 2nd induction layer, V.
# Date: 2016-03-23
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import math
from UV_LayerGeometry import UV_LayerGeometry

from Library.Geometry.Location import Location

class V_LayerGeometry( UV_LayerGeometry ) :

  #-------------------------------------------------------------------
  def __init__( self ) :
    """
    Constructor.
    """

    UV_LayerGeometry.__init__( self )

    # Total number of pins.
    self.pins = 2 * self.rows + 2 * self.columns - 1

    # Spacing between pins and front to back.
    self.depth = 95.2 / self.scale

    # Offset from APA's (0,0,0) position.
    self.apaOffsetX = -4.94
    self.apaOffsetY = -1.59
    self.apaOffsetZ = ( self.apaThickness - self.depth ) / 2

    self.apaOffset = Location( self.apaOffsetX, self.apaOffsetY, self.apaOffsetZ )

    # Distance from the layer to the head.
    self.zClearance = ( self.depth - self.apaToHead ) / self.scale
    self.frontZ = -self.zClearance
    self.backZ  = self.depth + self.zClearance

    # Travel for partial Z.  Should place head level with board and below pin
    # height.
    self.partialZ_Front = 0
    self.partialZ_Back  = self.depth

    # Distance that must be traveled past a pin to ensure it will be hooked
    # by the wire when moving in an other direction.
    # Doing some manual checks, I found 18 degrees is a good number that will
    # maximize the amount of contact of wire to the pin and still clear any
    # neighboring pins.
    overshootAngle = 90 - 18
    self.overshoot = self.zClearance * math.tan( math.radians( overshootAngle ) )

    # The grid parameters are a list of parameters for how the grid is constructed.
    # Columns:
    #   Count - Number of pins this row in the table represents.
    #   dx - Change in x each iteration.
    #   dy - Change in y each iteration.
    #   off.x - Starting x offset for initial position of first pin in this set.
    #   off.y - Starting y offset for initial position of first pin in this set.
    self.gridFront = \
    [
      # Count                    dx            dy   off.x   off.y
      [ self.rows,                0,  self.deltaY,      0,  4.463 ],
      [ self.columns,   self.deltaX,            0,  6.209,  4.462 ],
      [ self.rows - 1,            0, -self.deltaY,  2.209, -7.336 ],
      [ self.columns,  -self.deltaX,            0, -2.209, -7.339 ]
    ]

    # Back is identical to front.
    self.gridBack = self.gridFront
