###############################################################################
# Name: CameraThread.py
# Uses: Thread for camera updates.
# Date: 2016-12-15
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from Machine.Settings import Settings
from Control.IO_Log import IO_Log
from Threads.PrimaryThread import PrimaryThread

class ControlThread( PrimaryThread ) :

  #---------------------------------------------------------------------
  def __init__( self, io ) :
    """
    Constructor.

    Args:
      io: Instance of I/O map.
    """

    PrimaryThread.__init__( self, "CameraThread", log )
    self._io = io

  #---------------------------------------------------------------------
  def body( self ) :
    """
    Body of camera thread.
    """

    while PrimaryThread.isRunning :
      io.camera.poll()
      # # Mark the start of this update.
      # startTime = self._systemTime.get()
      #
      # # Update I/O.
      # self._io.pollInputs()
      #
      # # Update state machine.
      # self._stateMachine.update()
      #
      # # Mark time at end of update.
      # endTime = self._systemTime.get()
      #
      # # Measure time update took.
      # updateTime = endTime - startTime
      # updateTime = updateTime.total_seconds()
      #
      # # Update I/O log.
      # if self._isIO_Logged :
      #   self._ioLog.log( startTime, updateTime )
      #
      # # Calculate how long to sleep before updating again.
      # # Roughly creates intervals of Settings.IO_UPDATE_TIME.
      # sleepTime = Settings.IO_UPDATE_TIME - updateTime
      # if sleepTime > 0 :
      #   # Wait before updating again.
      #   self._systemTime.sleep( sleepTime )

# end class
