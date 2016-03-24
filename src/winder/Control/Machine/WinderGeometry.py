###############################################################################
# Name: WinderGeometry.py
# Uses: Constants related to the physical layout of the winder.
# Date: 2016-03-23
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from Library.Geometry.Location import Location
from Library.Geometry.Line import Line

class WinderGeometry :

  def __init__( self ) :

    # Park location.  This location contains a pin that can lock the travel
    # arm in place.
    self.PARK_LOCATION = Location( 0, 0 )

    # The Z-transfer area on the sides of the machine have a narrow window from
    # the outer bound.
    self.TRANSFER_AREA_WIDTH = 25

    # Outer bounds of the Z-transfer area.
    self.TRANSFER_LEFT    = 20    # $$$FUTURE - Get real number.
    self.TRANSFER_RIGHT   = 8000  # $$$FUTURE - Get real number.
    self.TRANSFER_TOP     = 2500  # $$$FUTURE - Get real number.
    self.TRANSFER_BOTTOM  = 20    # $$$FUTURE - Get real number.

    # Lines that define the seek edges of the transfer area.
    # Centered in the transfer area.
    self.TRANSFER_LEFT_SIDE   = Line( Line.VERTICLE_SLOPE, self.TRANSFER_LEFT + self.TRANSFER_AREA_WIDTH / 2 )
    self.TRANSFER_RIGHT_SIDE  = Line( Line.VERTICLE_SLOPE, self.TRANSFER_RIGHT - self.TRANSFER_AREA_WIDTH / 2 )
    self.TRANSFER_TOP_SIDE    = Line( 0, self.TRANSFER_TOP - self.TRANSFER_AREA_WIDTH / 2 )
    self.TRANSFER_BOTTOM_SIDE = Line( 0, self.TRANSFER_BOTTOM + self.TRANSFER_AREA_WIDTH / 2 )
