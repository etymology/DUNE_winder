###############################################################################
# Name: main.py
# Uses: Initialize and start the control system.
# Date: 2016-02-03
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-03 - QUE - Creation.
###############################################################################

from Control.Settings import Settings
from Control.GCodeHandler import GCodeHandler
from Control.ControlStateMachine import ControlStateMachine
from Control.ManualCommand import ManualCommand

from Threads.PrimaryThread import PrimaryThread
from Threads.UI_ServerThread import UI_ServerThread
from Threads.ControlThread import ControlThread
from Library.SystemTime import SystemTime
from Library.Log import Log
from Library.Configuration import Configuration

from Simulator.PLC_Simulator import PLC_Simulator

from Process.AnodePlaneArray import AnodePlaneArray

import time
import signal
import sys
import traceback

#==============================================================================
# Debug settings.
# These should all be set to False for production.
# Can be overridden from the command-line.
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
      "Main",
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

# Handle command line.
for argument in sys.argv:
  argument = argument.upper()
  option = argument
  value = "TRUE"
  if -1 != argument.find( "=" ) :
    option, value = argument.split( "=" )

  if "SIMULATED" == option or "SIMULATOR" == option :
    isSimulated = ( "TRUE" == value )
  elif "DEBUG" == option :
    debugInterface = ( "TRUE" == value )
  elif "LOG" == option :
    isLogEchoed = ( "TRUE" == value )

# Install signal handler for Ctrl-C shutdown.
signal.signal( signal.SIGINT, signalHandler )

#
# Create various objects.
#

systemTime = SystemTime()

# Load configuration and setup default values.
configuration = Configuration()
Settings.defaultConfig( configuration )

# Setup log file.
log = Log( systemTime, configuration.get( "LogDirectory" ) + '/log.csv', isLogEchoed )
log.add( "Main", "START", "Control system starts." )

# Create I/O map.
if isSimulated :
  from IO.Maps.SimulatedIO import SimulatedIO
  io = SimulatedIO()
  plcSimulator = PLC_Simulator( io )
else:
  from IO.Maps.Test_IO import Test_IO
  io = Test_IO( configuration.get( "plcAddress" ) )

gCodeHandler = GCodeHandler( io )
manualCommand = ManualCommand( io, log )
controlStateMachine = ControlStateMachine( io, log, gCodeHandler, manualCommand )

# Initialize threads.
uiServer = UI_ServerThread( commandHandler, log )
controlThread = ControlThread( io, controlStateMachine )

# Setup debug interface (if enabled).
if debugInterface :
  from Threads.DebugThread import DebugThread
  debugUI = \
    DebugThread(
      configuration.get( "serverAddress" ),
      int( configuration.get( "serverPort" ) )
    )



# $$$DEBUG
apa = AnodePlaneArray( configuration.get( "APA_LogDirectory" ), "TestAPA", log, True )
apa.loadRecipie( gCodeHandler, "GCodeA.txt", 128 )
apa.close()



# Begin operation.
PrimaryThread.startAllThreads()

# While the program is running...
while ( PrimaryThread.isRunning ) :
  time.sleep( 0.1 )

configuration.save()
log.add( "Main", "END", "Control system stops." )
