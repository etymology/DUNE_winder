###############################################################################
# Name: PrimaryThread.py
# Uses: Class for primary threads.
# Date: 2016-02-03
# Author(s):
#   Andrew Que <aque@bb7.com>
# Notes:
#   Used to keep a list of primary threads.  Such threads start when the
#   program loads and run until the program finishes.  They are signaled to
#   stop when PrimaryThread.isRunning to False.  When this occurs, each thread must
#   shutdown.
###############################################################################
import threading
import sys
import traceback
from Library.SystemSemaphore import SystemSemaphore

class PrimaryThread( threading.Thread ):

  list = []
  isRunning = False
  useGracefulException = True

  #---------------------------------------------------------------------
  def __init__( self, name, log ) :
    """
    Constructor.

    Args:
      name: Name of thread.
    """

    threading.Thread.__init__( self )
    PrimaryThread.list.append( self )
    self._name = name
    self._log = log

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

    for instance in PrimaryThread.list:
      instance.stop()

    SystemSemaphore.releaseAll()

  #---------------------------------------------------------------------
  def stop( self ) :
    """
    Stop this thread. Can be overloaded for custom shutdown.
    """
    pass

  #---------------------------------------------------------------------
  def run( self ) :
    try:
      self.body()
    except Exception as exception :
      PrimaryThread.stopAllThreads()
      exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
      tracebackString = repr( traceback.format_tb( exceptionTraceback ) )
      self._log.add(
        self.__class__.__name__,
        "ThreadException",
        "Thread had an exception.",
        [ exception, exceptionType, exceptionValue, tracebackString ]
      )

      if not PrimaryThread.useGracefulException :
        raise


# end class
