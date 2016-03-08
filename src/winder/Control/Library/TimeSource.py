###############################################################################
# Name: TimeSource.py
# Uses: Abstract class for a source of time.
# Date: 2016-02-12
# Author(s):
#   Andrew Que <aque@bb7.com>
# Notes:
#     A time source provides a reference of forward-moving time.  This
#   typically just comes from the system clock, but could also come from a
#   simulated source.  The time source must only increase, but is not required
#   to do so in even increments.
#     What objects are actually returned are irrelevant to this unit, but
#   need to stay consistent in the implementation used.  It will typically
#   be a time.time() object.
###############################################################################

from abc import ABCMeta, abstractmethod

class TimeSource :

  # Make class abstract.
  __metaclass__ = ABCMeta

  #-------------------------------------------------------------------
  @abstractmethod
  def get( self ) :
    """
    Return the current time.

    Returns:
      Returns current time.
    """

    pass
