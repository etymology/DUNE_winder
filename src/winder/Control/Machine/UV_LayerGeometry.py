###############################################################################
# Name: UV_LayerGeometry.py
# Uses: Geometry common to the induction (U and V) layers.
# Date: 2016-03-24
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from LayerGeometry import LayerGeometry

class UV_LayerGeometry( LayerGeometry ) :

  #-------------------------------------------------------------------
  def __init__( self ) :
    """
    Constructor.
    """

    LayerGeometry.__init__( self )

    self.rows        = 400
    self.columns     = 2 * self.rows
    self.pins        = 2 * self.rows + 2 * self.columns - 1

    # Data about the pins.
    self.pinDiameter = 2.43
    self.pinRadius   = self.pinDiameter / 2
    self.pinHeight   = 2
