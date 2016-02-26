###############################################################################
# Name: SoftwareOutput.py
# Uses: Software controlled digital output.  Debug class.
# Date: 2016-02-02
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-02 - QUE - Creation.
###############################################################################
from IO.Primitives.DigitalOutput import DigitalOutput

class SoftwareOutput( DigitalOutput ) :
  #---------------------------------------------------------------------
  def __init__( self, name, state = False ) :
    """
    Constructor.

    Args:
      name: Name of output.
      state: Steady state of input. This is the value always returned.

    """

    DigitalOutput.__init__( self, name, state )

  #---------------------------------------------------------------------
  def _doSet( self, state ) :
    """
    Function to actually set the output.

    Args:
      state: True of on, false for off.

    """

    pass

# end class
