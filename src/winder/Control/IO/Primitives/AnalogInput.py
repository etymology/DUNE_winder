###############################################################################
# Name: AnalogInput.py
# Uses: Abstract class for analog inputs.
# Date: 2016-02-02
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-02 - QUE - Creation.
###############################################################################

from IO_Point import IO_Point

class AnalogInput( IO_Point ) :

  # Static list of all analog inputs.
  list = []

  #---------------------------------------------------------------------
  def __init__( self, name ) :
    """
    Constructor.

    Args:
      name: Name of input.
      isListed: True if analog input should show up in list.

    """

    IO_Point.__init__( self, name )
    AnalogInput.list.append( self )

  #---------------------------------------------------------------------
  def __str__( self ):
    """
    Convert level to string.

    Returns:
      String of the level.
    """

    return str( self.get() )

# end class

