###############################################################################
# Name: APA_Geometry.py
# Uses: Geometry specific to the APA, not including layers.
# Date: 2016-03-24
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from MachineGeometry import MachineGeometry
from Library.Geometry.Location import Location

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

    # Offset from machine 0,0
    self.toAPA_OffsetX = 605.914 - 25.4/2
    self.toAPA_OffsetY = 339.778 - ( 191.107 - 38.1 / 2 )
    self.toAPA_OffsetZ = ( self.zTravel - self.apaThickness ) / 2

    # Location of bottom left corner of APA.
    self.apaLocation = Location( self.toAPA_OffsetX, self.toAPA_OffsetY, self.toAPA_OffsetZ )

    # Distance the head is from the APA frame.
    # Based on the fact the head is 25 mm from the tallest point, on the pin
    # height (2 mm) of the G-layer.
    self.apaToHead = 114.2 + 2 + 25 - self.apaThickness
