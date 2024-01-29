###############################################################################
# Name: SoftwareAnalogInput.py
# Uses: Fake analog input.  Useful for debugging.
# Date: 2016-02-02
# Author(s):
#   Andrew Que <aque@bb7.com>
#   Benjamin Oye <oye@uchicago.edu> [port to python3, Jan 2024]
###############################################################################

from __future__ import absolute_import
from IO.Primitives.AnalogInput import AnalogInput

class SoftwareAnalogInput( AnalogInput ) :

  # Level of virtual input.
  _value = 0

  #---------------------------------------------------------------------
  def __init__( self, name, value = 0 ) :
    """
    Constructor.

    Args:
      name: Name of output.
      value: Value to return.

    """

    AnalogInput.__init__( self, name )
    self._value = value

  #---------------------------------------------------------------------
  def get( self ) :
    """
    Return raw A/D value for this input.

    Returns:
      A/D value for this input.
    """

    return self._value

  #---------------------------------------------------------------------
  def set( self, value ) :
    """
    Set the value of the analog input.

    Args:
      value: Value to set.

    """

    self._value = value

# end class
