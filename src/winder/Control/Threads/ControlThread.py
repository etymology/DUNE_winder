###############################################################################
# Name: ControlThread.py
# Uses: Primary system control thread.  Loop runs master state machine.
# Date: 2016-02-04
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-04 - QUE - Creation.
###############################################################################
from Control.Settings import Settings
from PrimaryThread import PrimaryThread
from IO_Log import IO_Log

import time

class ControlThread( PrimaryThread ) :

  #---------------------------------------------------------------------
  def __init__( self, io, stateMachine, systemTime, isIO_Logged ) :
    """
    Constructor.

    Args:
      io: Instance of I/O map.
      stateMachine: Instance of state machine.
    """

    PrimaryThread.__init__( self, "ControlThread" )
    self._io = io
    self._systemTime = systemTime
    self._stateMachine = stateMachine
    self._isIO_Logged = isIO_Logged

    if isIO_Logged :
      self._ioLog = IO_Log( Settings.IO_LOG )

  #---------------------------------------------------------------------
  def run( self ) :
    """
    Body of control thread--the "main loop" of the program.
    """

    while PrimaryThread.isRunning :

      # Mark the start of this update.
      startTime = self._systemTime.get()

      # Update I/O.
      self._io.pollInputs()

      # Update state machine.
      self._stateMachine.update()

      # Mark time at end of update.
      endTime = self._systemTime.get()

      # Measure time update took.
      updateTime = endTime - startTime
      updateTime = updateTime.total_seconds()

      # Update I/O log.
      if self._isIO_Logged :
        self._ioLog.log( startTime, updateTime )

      # Calculate how long to sleep before updating again.
      # Roughly creates intervals of Settings.IO_UPDATE_TIME.
      sleepTime = Settings.IO_UPDATE_TIME - updateTime
      if sleepTime > 0 :
        # Wait before updating again.
        time.sleep( sleepTime )

# end class