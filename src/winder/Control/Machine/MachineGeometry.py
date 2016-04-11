###############################################################################
# Name: MachineGeometry.py
# Uses: Geometry of outer winding machine.
# Date: 2016-03-24
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from Library.Geometry.Line import Line
from Library.Geometry.Box import Box

class MachineGeometry :

  #-------------------------------------------------------------------
  def __init__( self ) :
    """
    Constructor.
    """

    # Scale down factor for geometry.
    # Debug only.  Set to 1 for production.
    self.scale = 1

    # Location of Z-Transfer areas.
    # Top/bottom for Y, left/right for X.
    self.top    = 2500  / self.scale
    self.bottom = -25   / self.scale
    self.left   = -250  / self.scale
    self.right  = 7000  / self.scale

    # How big the Z-transfer windows are.
    # The Z-transfer windows start at top/bottom/left/right locations.
    self.zWindow = 20

    # Lines defining the where a Z hand-off can take place.  Used for intercept
    # calculations.
    self.lineTop    = Line( 0, self.top )
    self.lineBottom = Line( 0, self.bottom )
    self.lineLeft   = Line( Line.VERTICLE_SLOPE, self.left )
    self.lineRight  = Line( Line.VERTICLE_SLOPE, self.right )

    # Box that defines the Z hand-off edges.
    self.edges = Box( self.left, self.top, self.right, self.bottom )
