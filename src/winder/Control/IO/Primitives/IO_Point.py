###############################################################################
# Name: IO_Point.py
# Uses: A generic abstract class used for all I/O points. Keeps a static list
#       of all I/O points and requires all I/O points to have a name.
# Date: 2016-02-02
# Author(s):
#   Andrew Que <aque@bb7.com>
#   Benjamin Oye <oye@uchicago.edu> [port to python3, Jan 2024]
###############################################################################


from __future__ import absolute_import
from abc import ABCMeta, abstractmethod
import six

class IO_Point(six.with_metaclass(ABCMeta)):
  # Make class abstract.
  list = []
  map = {}

  #---------------------------------------------------------------------
  def __init__( self, name ):
    """
    Constructor. Save name and insert self into list of NamedIO.

    """

    # Make sure this name isn't already in use.
    assert name not in IO_Point.list

    IO_Point.list.append( self )
    IO_Point.map[ name ] = self

    self._name = name

  #---------------------------------------------------------------------
  def getName( self ) :
    """
    Return the name of this instance.

    Returns:
      string name of this instance.
    """

    return self._name

  #---------------------------------------------------------------------
  @abstractmethod
  def get( self ):
    """
    Abstract function that must be define in the child class that will return the data from this I/O point.

    Returns:
      The current state of this I/O point.
    """

    pass

# end class
