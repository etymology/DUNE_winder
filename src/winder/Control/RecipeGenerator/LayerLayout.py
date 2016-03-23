###############################################################################
# Name: LayerLayout.py
# Uses: Layout parameters common to all layers.
# Date: 2016-03-23
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from Library.Geometry.Line import Line

class LayerLayout :
  """
  Layout parameters common to all layers.
  """

  def __init__( self, divide = 1 ) :
    """
    Constructor.

    Args:
      divide: Scale factor to divide down layer (not functional).
    """
    self.rows        = 400 / divide
    self.columns     = 2 * self.rows
    self.pins        = 2 * self.rows + 2 * self.columns - 1

    # Data about the pins.
    self.pinDiameter = 2.43
    self.pinRadius   = self.pinDiameter / 2
    self.pinHeight   = 2

    # Location of Z-Transfer areas.
    # Top/bottom for Y, left/right for X.
    self.top    = 2500
    self.bottom = -25
    self.left   = -250
    self.right  = 6800

    # How big the Z-transfer windows are.
    # The Z-transfer windows start at top/bottom/left/right locations.
    self.zWindow = 20

    # Lines defining the where a Z hand-off can take place.  Used for intercept
    # calculations.
    self.lineTop    = Line( 0, self.top )
    self.lineBottom = Line( 0, self.bottom )
    self.lineLeft   = Line( float( "inf" ), self.left )
    self.lineRight  = Line( float( "inf" ), self.right )
