###############################################################################
# Name: SoftwareInput.py
# Uses: Software controlled digital input.
# Date: 2016-02-02
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from IO.Primitives.DigitalInput import DigitalInput

class SoftwareInput( DigitalInput ) :

  # State of virtual input.
  _state = False

  #---------------------------------------------------------------------
  def __init__( self, name, state = False ) :
    """
    Constructor.

    Args:
      name: Name of output.
      state: Steady state of input. This is the value always returned.

    """

    DigitalInput.__init__( self, name )
    self._state = state

  #---------------------------------------------------------------------
  def _doGet( self ) :
    """
    Fetch state of input.

    Returns:
      Returns whatever was passes as the initial state.
    """

    return self._state

  #---------------------------------------------------------------------
  def set( self, state ) :
    """
    Set the state of input.

    Args:
      state: New state of input.

    """

    self._state = state

# end class
