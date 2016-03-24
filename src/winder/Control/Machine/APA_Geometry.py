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

    # The wing on the right is extra distance the wire must wrap around.
    self.rightExtention = 304.29

