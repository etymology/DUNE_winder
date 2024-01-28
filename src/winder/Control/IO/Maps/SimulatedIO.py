###############################################################################
# Name: SimulatedIO.py
# Uses: Map of I/O used by simulator.
# Date: 2016-02-03
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from IO.Devices.SimulatedPLC import SimulatedPLC
from .BaseIO import BaseIO

class SimulatedIO( BaseIO ) :

  #---------------------------------------------------------------------
  def __init__( self ) :
    """
    Constructor.
    Only need to create the correct type of PLC and call the base I/O
    constructor.
    """
    plc = SimulatedPLC( "PLC" )
    BaseIO.__init__( self, plc )

# end class
