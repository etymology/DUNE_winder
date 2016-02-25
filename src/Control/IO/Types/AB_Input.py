#==============================================================================
# Name: AB_Input.py
# Uses: Digital input from an Allen-Bradley PLC.
# Date: 2016-02-22
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-22 - QUE - Creation.
#==============================================================================

from IO.Primitives.DigitalInput import DigitalInput

class AB_Input( DigitalInput ) :

  list = []

  #---------------------------------------------------------------------
  def __init__( self, name, abPLC, tag, bit, defaultState = False ) :
    """
    Constructor.

    Args:
      name: Name of output.
      abPLC: Instance of IO_Device.AB_PLC.
      tag: Which PLC tag this input is assigned.
      defaultState: Default state if input is unreadable.
    """
    DigitalInput.__init__( self, name )
    AB_Input.list.append( self )
    self._abPLC = abPLC
    self._tag   = tag
    self._bit   = bit
    self._defaultState = defaultState
    self._state = defaultState

  #---------------------------------------------------------------------
  def poll( self ) :
    """
    Update the input by reading the value form PLC.  Call periodically.
    """
    value = self._abPLC.read( self._tag )
    if not value == None and not self._abPLC.isNotFunctional() :
      self.updateFromReadTag( value )
    else :
      self._state = self._defaultState

    #if not value == None and not self._abPLC.isNotFunctional() :
    #  status = int( value[ 0 ] )
    #  status >>= self._bit
    #  status &= 1
    #  self._state = bool( status )
    #else :
    #  self._state = defaultState

  #---------------------------------------------------------------------
  @staticmethod
  def pollAll() :
    """
    $$$DEBUG
    """
    for instance in AB_Input.list :
      instance.poll() # $$$DEBUG - Do single read.


  #---------------------------------------------------------------------
  def getReadTag( self ) :
    """
    Get read tag.  Used when reading multiple tags at once.
    """
    return self._tag

  #---------------------------------------------------------------------
  def updateFromReadTag( self, value ) :
    """
    Update internal state from tag data.  Used when multiple reads have
    been done at once to feed back data.
    """
    # $$$DEBUG if not None == data :
    # $$$DEBUG   self._state = bool( data[ 0 ] )

    status = int( value[ 0 ] )
    status >>= self._bit
    status &= 1
    self._state = bool( status )


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
    return self._state

# end class
