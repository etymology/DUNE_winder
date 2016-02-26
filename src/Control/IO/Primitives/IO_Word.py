###############################################################################
# Name: IO_Word.py
# Uses: Abstract class for a word of I/O.
# Date: 2016-02-24
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-24 - QUE - Creation.
###############################################################################

from IO_Point import IO_Point
from abc import ABCMeta, abstractmethod

class IO_Word( IO_Point ) :
  # Make class abstract.
  __metaclass__ = ABCMeta

  # Static list of all I/O words.
  list = []

  #---------------------------------------------------------------------
  def __init__( self, name ) :
    """
    Constructor.

    Args:
      name: Name of input.
    """

    IO_Point.__init__( self, name )
    IO_Word.list.append( self )

  #---------------------------------------------------------------------
  @abstractmethod
  def set( self, value ) :
    """
    Abstract function that must be define in child to preform output operations.

    Args:
      value: Value to set the word.

    """

    pass

  #---------------------------------------------------------------------
  @abstractmethod
  def get( self ) :
    """
    Abstract function that must be define in child to preform output operations.

    Returns:
      Value of the I/O word.

    """
    pass

  #---------------------------------------------------------------------
  def __str__( self ):
    """
    Convert level to string.

    Returns:
      String of the level.
    """

    return str( self.get() )

# end class

