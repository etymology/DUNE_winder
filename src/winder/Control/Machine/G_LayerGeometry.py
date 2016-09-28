###############################################################################
# Name: X_LayerGeometry.py
# Uses: Geometry specific to the 2nd grid layer, G.
# Date: 2016-03-23
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################


from Library.Geometry.Location import Location

from GX_LayerGeometry import GX_LayerGeometry

class G_LayerGeometry( GX_LayerGeometry ) :

  #-------------------------------------------------------------------
  def __init__( self ) :
    """
    Constructor.
    """

    GX_LayerGeometry.__init__( self )

    # Total number of pins.
    self.pins = int( 481 * 2 / self.scale )

    # Spacing between pins and front to back.
    self.depth = 114.2 / self.scale

    # Locations of the two columns of pins.
    self.boardWidth = 3.18
    self.leftEdge  = -self.boardWidth
    self.rightEdge = 6410.37 / self.scale + self.boardWidth

    # Offset from APA's (0,0,0) position.
    self.apaOffsetX = -13.23 + self.boardWidth
    self.apaOffsetY = 0
    self.apaOffsetZ = ( self.apaThickness - self.depth ) / 2

    self.apaOffset = Location( self.apaOffsetX, self.apaOffsetY, self.apaOffsetZ )

    # Distance from the layer to the head.
    self.frontZ = 0
    self.backZ  = self.zTravel

    # Travel for partial Z.  Should place head level with board and below pin
    # height.
    self.partialZ_Front = ( self.zTravel + self.depth ) / ( 2 * self.scale )
    self.partialZ_Back  = ( self.zTravel - self.depth ) / ( 2 * self.scale )
