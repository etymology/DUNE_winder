###############################################################################
# Name: DigitalInput.py
# Uses: Abstract class to define digital inputs.
# Date: 2016-02-02
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-02 - QUE - Creation.
###############################################################################

from DigitalIO import DigitalIO

class DigitalInput( DigitalIO ) :

  # Static list of all digital inputs.
  list = []

  #---------------------------------------------------------------------
  def __str__( self ) :
    """
    Convert state to string.

    Returns:
      "1" for on, "0" for off.
    """

    result = "0"
    if self.get() :
      result = "1"

    return result

  #---------------------------------------------------------------------
  def __init__( self, name ) :
    """
    Constructor.

    Args:
      name: Name of input.

    """

    DigitalIO.__init__( self, name )
    DigitalInput.list.append( self )

# end class