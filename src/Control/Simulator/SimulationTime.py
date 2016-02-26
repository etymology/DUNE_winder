###############################################################################
# Name: SimulationTime.py
# Uses: Unit for creating time with simulator.
# Date: 2016-02-07
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-07 - QUE - Creation.
###############################################################################

from Library.TimeSource import TimeSource
import datetime

class SimulationTime( TimeSource ) :
  #-------------------------------------------------------------------
  def __init__( self, initialTime = datetime.datetime.utcnow() ) :
    """
    Constructor.

    Args:
      initialTime: Time at which to start simulator. Defaults to current system time.

    """

    # State with system time.
    self._time = initialTime

  #-------------------------------------------------------------------
  def get( self ) :
    """
    Return the current simulation time.

    Returns:
      Returns current simulation time.
    """

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
