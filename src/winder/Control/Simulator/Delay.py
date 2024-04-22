###############################################################################
# Name: Delay.py
# Uses: A time delay function for simulator.
# Date: 2016-04-26
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import datetime

class Delay :

  #---------------------------------------------------------------------
  def __init__( self, systemTime, delay=None ):
    """
    Constructor.

    Args:
      systemTime: Instance of SystemTime.
      delay: Delay in milliseconds.  None to start disabled.
    """

    self._systemTime = systemTime
    self._endTime = None

    if delay is not None:
      self.set( delay )


  #---------------------------------------------------------------------
  def set( self, delay ) :
    """
    Set the delay.

    Args:
      delay: Delay in milliseconds.
    """
    delta = datetime.timedelta( milliseconds=delay )
    self._endTime = self._systemTime.get() + delta

  #---------------------------------------------------------------------
  def hasExpired( self ):
    """
    Check to see if the delay time has elapsed.

    Returns:
      True if delay has elapsed, False if not.
    """
    return (self._systemTime.get() >= self._endTime
            if self._endTime is not None else True)