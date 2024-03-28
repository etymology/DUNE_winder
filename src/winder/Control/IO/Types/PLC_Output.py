###############################################################################
# Name: PLC_Output.py
# Uses: Digital input on a PLC.
# Date: 2016-02-23
# Author(s):
#   Andrew Que <aque@bb7.com>
#   Benjamin Oye <oye@uchicago.edu> [port to python3, Jan 2024]
###############################################################################


from __future__ import absolute_import
from IO.Primitives.DigitalOutput import DigitalOutput
from IO.PLC import PLC

class PLC_Output( DigitalOutput ) :

  # State of virtual input.
  _state = False

  #---------------------------------------------------------------------
  def __init__( self, name, plc, tagName, state = False, immediate = True ) :
    """
    Constructor.

    Args:
      name: Name of output.
      plc: Instance of IO_Device.PLC.
      tagName: PLC.Tag this input is assigned.
      state: Steady state of input. This is the value always returned.
      immediate: True if the output should write immediately to the PLC, False
        to set state internally and wait for polling to do write.
    """
    DigitalOutput.__init__( self, name )
    self._state = state
    self._immediate = immediate

    self._plc = plc
    attributes = PLC.Tag.Attributes()
    attributes.isPolled = False
    self._tag = plc.Tag( plc, tagName, attributes, "BOOL" )


  #---------------------------------------------------------------------
  def poll( self ) :
    """
    Actually write the data to the PLC.  Call periodically.
    """
    self._tag.poll()

  #---------------------------------------------------------------------
  def _doSet( self, state ) :
    """
    Function to set the output.

    Args:
      state: True of on, false for off.

    Note:
      This does not write to the PLC until polled.
    """
    self._state = state
    self._tag.set( state )

# end class
