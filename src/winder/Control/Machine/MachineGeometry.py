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
    self.top    = 2800  / self.scale  # 2800
    self.bottom = 0     / self.scale  # -25
    self.left   = 400   / self.scale  # -250
    self.right  = 6500  / self.scale  # 6500

    # How big the Z-transfer windows are.
    # The Z-transfer windows start at top/bottom/left/right locations.
    self.zWindow = 20

    # Amount of distance the Z-axis can travel.
    self.zTravel = 434

    # Lines defining the where a Z hand-off can take place.  Used for intercept
    # calculations.
    self.lineTop    = Line( 0, self.top )
    self.lineBottom = Line( 0, self.bottom )
    self.lineLeft   = Line( Line.VERTICLE_SLOPE, self.left )
    self.lineRight  = Line( Line.VERTICLE_SLOPE, self.right )

    # Box that defines the Z hand-off edges.
    self.edges = Box( self.left, self.top, self.right, self.bottom )
