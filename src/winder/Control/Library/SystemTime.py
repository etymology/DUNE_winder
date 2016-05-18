###############################################################################
# Name: SystemTime.py
# Uses: Normal system time source.
# Date: 2016-02-12
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from Library.TimeSource import TimeSource
import datetime

class SystemTime( TimeSource ) :
  #-------------------------------------------------------------------
  def get( self ) :
    """
    Return the current time.

    Returns:
      Returns current time.
    """

    return datetime.datetime.utcnow()

  #-------------------------------------------------------------------
  def getDelta( self, then, now=None ) :
    """
    Return the amount of time between two time stamps.

    Args:
      then - Starting time.
      now - Current time.  If omitted, the current time is used.

    Returns:
      Time between to time stamps.
    """

    if None == now :
      now = self.get()

    delta = now - then

    return delta.total_seconds()

