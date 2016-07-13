###############################################################################
# Name: SimulationTime.py
# Uses: Unit for creating time with simulator.
# Date: 2016-02-07
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import time
import datetime
from Library.TimeSource import TimeSource

class SimulationTime( TimeSource ) :
  #-------------------------------------------------------------------
  def __init__( self, initialTime = datetime.datetime.utcnow(), isRealTime=True ) :
    """
    Constructor.

    Args:
      initialTime: Time at which to start simulator. Defaults to current system time.

    """

    # State with system time.
    self._time = initialTime
    self._isRealTime = isRealTime

  #-------------------------------------------------------------------
  def sleep( self, sleepTime ) :
    """
    Sleep for specified time (in seconds).

    Args:
      sleepTime: Time to sleep (in seconds and can be fractional).
    """
    if self._isRealTime :
      time.sleep( sleepTime )
    else:
      self._time += datetime.timedelta( seconds = sleepTime )

  #-------------------------------------------------------------------
  def get( self ) :
    """
    Return the current simulation time.

    Returns:
      Returns current simulation time.
    """

    if self._isRealTime :
      self.setLocal()

    return self._time

  #-------------------------------------------------------------------
  def set( self, time ) :
    """
    Set current simulation time.

    Args:
      time: New simulation time.

    """

    self._time = time

  #-------------------------------------------------------------------
  def setLocal( self ) :
    """
    Set current simulation time to the local system time.

    """

    self._time = datetime.datetime.utcnow()

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

