###############################################################################
# Name: CameraThread.py
# Uses: Thread for camera updates.
# Date: 2016-12-15
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

from Library.SystemSemaphore import SystemSemaphore
from Threads.PrimaryThread import PrimaryThread

class CameraThread( PrimaryThread ) :

  # Amount of time to sleep if FIFO is empty.
  SLEEP_TIME = 50

  #---------------------------------------------------------------------
  def __init__( self, camera, log, systemTime ) :
    """
    Constructor.

    Args:
      camera: Instance of IO.Systems.Camera.
      log: Instance of system log.
      systemTime: Instance of SystemTime.
    """
    PrimaryThread.__init__( self, "CameraThread", log )
    self._camera = camera
    self._isRunning = False
    self._semaphore = SystemSemaphore( 0 )
    self._systemTime = systemTime
    camera.setCallback( self._setEnable )

  #---------------------------------------------------------------------
  def _setEnable( self, isEnabled ) :
    """
    Camera trigger enable callback.  Private.

    Args:
      isEnabled: True if enabling camera trigger, False if disabling.
    """
    self._isRunning = isEnabled

    if isEnabled :
      self._semaphore.release()

  #---------------------------------------------------------------------
  def body( self ) :
    """
    Body of camera thread.
    """
    while PrimaryThread.isRunning :

      # If not running, wait.
      if not self._isRunning :
        self._semaphore.acquire()

      # If not shutting down...
      if PrimaryThread.isRunning :
        # Assume there will be no sleep (a yield only).
        sleepTime = 0

        # Update camera if running...
        if self._isRunning :
          hasData = self._camera.poll()

          # If there was no data to read, sleep for awhile.  Otherwise, read
          # again soon.
          if not hasData :
            sleepTime = CameraThread.SLEEP_TIME

        # Yield thread time.
        self._systemTime.sleep( sleepTime )

# end class
