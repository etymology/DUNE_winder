###############################################################################
# Name: AnalogOutput.py
# Uses: Abstract class for analog outputs.
# Date: 2016-02-02
# Author(s):
#   Andrew Que <aque@bb7.com>
#   Benjamin Oye <oye@uchicago.edu> [port to python3, Jan 2024]
###############################################################################

from .IO_Point import IO_Point
from abc import ABCMeta, abstractmethod
import six

class AnalogOutput( IO_Point, metaclass=ABCMeta ) :
  # Make class abstract.
  list = []

  # Current output level.
  _level = 0

  #---------------------------------------------------------------------
  def __init__( self, name ):
    """
    Constructor.

    Args:
      name: Name of output.

    """

    # Make sure this name isn't already in use.
    assert name not in AnalogOutput.list

    IO_Point.__init__( self, name )

    AnalogOutput.list.append( self )
    AnalogOutput.map[ name ] = self

  #---------------------------------------------------------------------
  @abstractmethod
  def _doSet( self, state ) :
    """
    Abstract function that must be define in child to preform output operations.

    Args:
      level: Output level.

    """

    pass

  #---------------------------------------------------------------------
  def set( self, level ) :
    """
    Set the output to a given level.

    Args:
      level: New output level.

    """

    # Save the state for requests.
    self._level = level

    # Actually set the state.
    self._doSet( level )

  #---------------------------------------------------------------------
  def get( self ) :
    """
    Return current level of output.

    Returns:
      Level of output.
    """

    return self._level

  #---------------------------------------------------------------------
  def __str__( self ):
    """
    Convert level to string.

    Returns:
      String of the level.
    """

    return str( self.get() )

# end class
