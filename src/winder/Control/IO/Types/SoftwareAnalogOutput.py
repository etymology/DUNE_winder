###############################################################################
# Name: SoftwareAnalogInput.py
# Uses: Fake analog output.  Useful for debugging.
# Date: 2016-02-02
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################
from IO.Primitives.AnalogOutput import AnalogOutput

class SoftwareAnalogOutput( AnalogOutput ) :
  #---------------------------------------------------------------------
  def __init__( self, name ) :
    """
    Constructor.

    Args:
      name: Name of output.
      value: Value to return.

    """

    AnalogOutput.__init__( self, name )

  #---------------------------------------------------------------------
  def _doSet( self, level ) :
    """
    Dummy function to do set. Does nothing.

    Args:
      level: Output level.

    """

    pass

# end class
