###############################################################################
# Name: UV_LayerGeometry.py
# Uses: Geometry common to the induction (U and V) layers.
# Date: 2016-03-24
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import math
from LayerGeometry import LayerGeometry

class UV_LayerGeometry( LayerGeometry ) :


  #-------------------------------------------------------------------
  def __init__( self ) :
    """
    Constructor.
    """

    LayerGeometry.__init__( self )

    self.rows    = 400
    self.columns = 2 * self.rows

    # Data about the pins.
    self.pinDiameter = 2.43
    self.pinRadius   = self.pinDiameter / 2
    self.pinHeight   = 2

    # Spacing between pins and front to back.
    self.deltaX      = 8.0
    self.deltaY      = 5.75

    # Typical slope of lines.
    self.slope = self.deltaY / self.deltaX

    # Primary angle (in radians) between wires.
    self.angle = math.atan( self.deltaY / self.deltaX )

    # When crossing between pins, this is the minimum allowable angle.  Less
    # than this the wire risks hitting the pins on either side.
    self.minAngle = math.radians( 30 )

    # Distance between wires.
    self.wireSpacing = \
      self.deltaY / math.sqrt( self.deltaY**2 / self.deltaX**2 + 1 )
