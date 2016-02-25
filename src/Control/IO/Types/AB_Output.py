#==============================================================================
# Name: AB_Output.py
# Uses: Digital input on an Allen-Bradley PLC.
# Date: 2016-02-23
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-23 - QUE - Creation.
#==============================================================================

from IO.Primitives.DigitalOutput import DigitalOutput

class AB_Output( DigitalOutput ) :

  # State of virtual input.
  _state = False

  #---------------------------------------------------------------------
  def __init__( self, name, abPLC, tag, state = False, immediate = True ) :
    """
    Constructor.

    Args:
      name: Name of output.
      abPLC: Instance of IO_Device.AB_PLC.
      tag: Which PLC tag this input is assigned.
      state: Steady state of input. This is the value always returned.
      immediate: True if the output should write immediately to the PLC, False
        to set state internally and wait for polling to do write.
    """
    DigitalOutput.__init__( self, name )
    self._state = state
    self._immediate = immediate
    self._abPLC = abPLC
    self._tag   = tag

  #---------------------------------------------------------------------
  def poll( self ) :
    """
    Actually write the data to the PLC.  Call periodically.
    """
    self._abPLC.write( self._tag, self._state, "BOOL" )

  #---------------------------------------------------------------------
  def getWriteTag( self ) :
    """
    Get a list for the write tag.  Used when writing multiple tags at
    once.
    """
    return [ self._tag, self._state, "BOOL" ]

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

    if self._immediate :
      self.poll()

# end class
