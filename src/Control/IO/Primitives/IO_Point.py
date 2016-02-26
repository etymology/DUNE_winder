###############################################################################
# Name: IO_Point.py
# Uses: A generic abstract class used for all I/O points. Keeps a static list
#       of all I/O points and requires all I/O points to have a name.
# Date: 2016-02-02
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-02 - Creation.
###############################################################################

from abc import ABCMeta, abstractmethod

class IO_Point:
  # Make class abstract.
  __metaclass__ = ABCMeta

  # Static list of all IO_Point objects in system.
  list = []

  #---------------------------------------------------------------------
  def __init__( self, name ) :
    """
    Constructor. Save name and insert self into list of NamedIO.

    """

    self._name = name
    IO_Point.list.append( self )

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
