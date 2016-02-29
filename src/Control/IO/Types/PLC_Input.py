###############################################################################
# Name: PLC_Input.py
# Uses: Digital input from a PLC.
# Date: 2016-02-22
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-22 - QUE - Creation.
###############################################################################

from IO.Primitives.DigitalInput import DigitalInput
from IO.Devices.PLC import PLC

class PLC_Input( DigitalInput ) :

  list = []

  #---------------------------------------------------------------------
  def __init__( self, name, plc, tagName, bit, defaultState = False ) :
    """
    Constructor.

    Args:
      name: Name of output.
      plc: Instance of IO_Device.PLC.
      tagName: Which PLC tag this input is assigned.
      defaultState: Default state if input is unreadable.
    """
    DigitalInput.__init__( self, name )
    PLC_Input.list.append( self )

    self._plc = plc
    attributes = PLC.Tag.Attributes()
    attributes.canWrite     = False
    attributes.defaultValue = defaultState
    attributes.isPolled     = True
    self._tag = plc.Tag( name, plc, tagName, attributes )

    self._bit = bit
    self._defaultState = defaultState
    self._state = defaultState

  #---------------------------------------------------------------------
  def _doGet( self ) :
    """
    Fetch state of input.

    Returns:
      Returns whatever was passes as the initial state.

    Note:
      Does not reflect any useful value until polled.  If the PLC isn't
      functional, this value returns a default value.
    """
    value = int( self._tag.get() )
    value >>= self._bit
    value &= 0x01
    value = bool( value == 1 )

    return value

# end class
