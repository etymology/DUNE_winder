###############################################################################
# Name: LayerGeometry.py
# Uses: Geometry common to all layers.
# Date: 2016-03-23
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from APA_Geometry import APA_Geometry

class LayerGeometry( APA_Geometry ) :
  #-------------------------------------------------------------------
  def __init__( self ) :
    """
    Constructor.
    """

    APA_Geometry.__init__( self )

    # Diameter of the wire (in mm).
    self.wireDiameter = 0.15
    self.wireRadius = self.wireDiameter / 2

    # Thickness of each layer board.
    self.boardThickness = 3.175  # 1/8"
    self.boardHalfThickness = self.boardThickness / 2

    # Spacing between board.
    self.boardSpacing   = 3.35
