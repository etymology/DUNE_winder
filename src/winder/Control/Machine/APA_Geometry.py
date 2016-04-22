###############################################################################
# Name: APA_Geometry.py
# Uses: Geometry specific to the APA, not including layers.
# Date: 2016-03-24
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from MachineGeometry import MachineGeometry

class APA_Geometry( MachineGeometry ) :

  #-------------------------------------------------------------------
  def __init__( self ) :
    """
    Constructor.
    """

    MachineGeometry.__init__( self )

    # Dimensions of base APA steel frame.
    self.apaLength    = 6060.2
    self.apaHeight    = 2300
    self.apaThickness = 76.2

    # Distance the head is from the APA frame.
    # Based on the fact the head is 25 mm from the tallest point, on the pin
    # height (2 mm) of the G-layer.
    self.apaToHead = 114.2 + 2 + 25 - self.apaThickness
