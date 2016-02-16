#==============================================================================
# Name: PrimaryThread.py
# Uses: Class for primary threads.
# Date: 2016-02-03
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-03 - QUE - Creation.
# Notes:
#   Used to keep a list of primary threads.  Such threads start when the
#   program loads and run until the program finishes.  They are signaled to
#   stop when PrimaryThread.isRunning to False.  When this occurs, each thread must
#   shutdown.
#==============================================================================
import threading
from Library.SystemSemaphore import SystemSemaphore

class PrimaryThread( threading.Thread ):

  list = []
  isRunning = False

  #---------------------------------------------------------------------
  def __init__( self, name ) :
    """
    Constructor.

    Args:
      name: Name of thread.

    """

    threading.Thread.__init__( self )
    PrimaryThread.list.append( self )
    self._name = name

  #---------------------------------------------------------------------
  @staticmethod
  def startAllThreads():
    """
    Start all threads. Call at start of program after thread creation.

    """

    PrimaryThread.isRunning = True
    for instance in PrimaryThread.list:
      instance.start()

  #---------------------------------------------------------------------
  @staticmethod
  def stopAllThreads():
    """
    Stop all threads. Call at end of program.

    """

    PrimaryThread.isRunning = False
    SystemSemaphore.releaseAll()

# end class
