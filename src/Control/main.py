###############################################################################
# Name: main.py
# Uses: Initialize and start the control system.
# Date: 2016-02-03
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-03 - QUE - Creation.
###############################################################################

# Import I/O map.
from IO.Maps.Test_IO import Test_IO
from IO.Maps.SimulatedIO import SimulatedIO

from Control.Settings import Settings
from Control.GCodeHandler import GCodeHandler
from Control.ControlStateMachine import ControlStateMachine
from Control.ManualCommand import ManualCommand

from Threads.PrimaryThread import PrimaryThread
from Threads.UI_ServerThread import UI_ServerThread
from Threads.ControlThread import ControlThread
from Threads.DebugThread import DebugThread
from Library.SystemTime import SystemTime
from Library.Log import Log
from Library.Configuration import Configuration

import time
import signal
import sys, traceback

#==============================================================================

# True if using simulated I/O.
isSimulated = False

# True to use debug interface.
debugInterface = True

# True to echo log to screen.
isLogEchoed = True

#==============================================================================





#-----------------------------------------------------------------------
def commandHandler( command ) :
  """
  Handle a remote command.

  Args:
    command: A command to evaluate.

  Returns:
    The data returned from the command.
  """

  try:
    result = eval( command )
  except Exception as exception:
    result = "Invalid request"

    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    tracebackString = repr( traceback.format_tb( exceptionTraceback ) )
    log.add(
      "MAIN",
      "commandHandler",
      "Invalid command issued from UI.",
      [ exception, exceptionType, exceptionValue, tracebackString ]
    )

  return result

#-----------------------------------------------------------------------
def signalHandler( signal, frame ):
  """
  Keyboard interrupt handler. Used to shutdown system for Ctrl-C.

  Args:
    signal: Ignored.
    frame: Ignored.

  """
  PrimaryThread.stopAllThreads()

#-----------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------

# Install signal handler for Ctrl-C shutdown.
signal.signal( signal.SIGINT, signalHandler )

#
# Create various objects.
#

systemTime = SystemTime()
log = Log( systemTime, 'log.csv', isLogEchoed )

# Load configuration and setup default values.
configuration = Configuration()
Settings.defaultConfig( configuration )

# Create I/O map.
if isSimulated :
  io = SimulatedIO()
else:
  io = Test_IO( configuration.get( "plcAddress" ) )

gCodeHandler = GCodeHandler( io )
manualCommand = ManualCommand( io, log )
controlStateMachine = ControlStateMachine( io, log, gCodeHandler, manualCommand )

# Initialize threads.
uiServer = UI_ServerThread( commandHandler, log )
controlThread = ControlThread( io, controlStateMachine )

if debugInterface :
  debugUI = \
    DebugThread(
      configuration.get( "serverAddress" ),
      int( configuration.get( "serverPort" ) )
    )

# Begin operation.
PrimaryThread.startAllThreads()

# # $$$DEBUG - Remove from this location.
# io.xAxis.setEnable( True )
# io.yAxis.setEnable( True )
# io.zAxis.setEnable( True )

# While the program is running...
while ( PrimaryThread.isRunning ) :
  time.sleep( 0.1 )

configuration.save()
log.add( "Main", "END", "Control system stops." )
