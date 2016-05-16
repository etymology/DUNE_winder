###############################################################################
# Name: main.py
# Uses: Initialize and start the control system.
# Date: 2016-02-03
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

import signal
import sys
import traceback
import time
import json

from Library.SystemTime import SystemTime
from Library.Log import Log
from Library.Configuration import Configuration
from Library.Version import Version

from Machine.Settings import Settings

from Control.LowLevelIO import LowLevelIO
from Control.Process import Process

from Threads.PrimaryThread import PrimaryThread
from Threads.UI_ServerThread import UI_ServerThread
from Threads.ControlThread import ControlThread
from Threads.WebServerThread import WebServerThread

#==============================================================================
# Debug settings.
# These should all be set to False for production.
# Can be overridden from the command-line.
#==============================================================================

# True if using simulated I/O.
isSimulated = False

# True to use debug interface.
debugInterface = False

# True to echo log to screen.
isLogEchoed = True

# True to log I/O.
# CAUTION: Log file will get large very quickly.
isIO_Logged = False

#==============================================================================

#-----------------------------------------------------------------------
def commandHandler( _, command ) :
  """
  Handle a remote command.
  This is define in main so that is has the most global access possible.

  Args:
    command: A command to evaluate.

  Returns:
    The data returned from the command.
  """

  try:
    result = eval( command )
  except Exception as exception:
    result = "Invalid request"

    exceptionTypeName, exceptionValues, tracebackValue = sys.exc_info()

    if debugInterface :
      traceback.print_tb( tracebackValue )

    tracebackAsString = repr( traceback.format_tb( tracebackValue ) )
    log.add(
      "Main",
      "commandHandler",
      "Invalid command issued from UI.",
      [ command, exception, exceptionTypeName, exceptionValues, tracebackAsString ]
    )

  # Try and make JSON object of result.
  try:
    result = json.dumps( result )
  except TypeError :
    # If it cannot be made JSON, just make it a string.
    result = json.dumps( str( result ) )

  return result

#-----------------------------------------------------------------------
def signalHandler( signalNumber, frame ):
  """
  Keyboard interrupt handler. Used to shutdown system for Ctrl-C.

  Args:
    signal: Ignored.
    frame: Ignored.
  """
  signalNumber = signalNumber
  frame = frame
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
  elif "LOG_IO" == option :
    isIO_Logged = ( "TRUE" == value )
  elif "VERIFY_VERSION" == option :
    version = Version( Settings.VERSION_FILE, ".", Settings.CONTROL_FILES )
    uiVersion = Version( Settings.UI_VERSION_FILE, Settings.WEB_DIRECTORY, Settings.UI_FILES )

    returnResult = 0
    if not version.verify() :
      print "Control version incorrect."
      returnResult -= 1
    else :
      print "Control version correct."

    if not uiVersion.verify() :
      print "UI version incorrect."
      returnResult -= 2
    else :
      print "UI version correct."

    sys.exit( returnResult )

# Install signal handler for Ctrl-C shutdown.
signal.signal( signal.SIGINT, signalHandler )

#
# Create various objects.
#

systemTime = SystemTime()

# Load configuration and setup default values.
configuration = Configuration( Settings.CONFIG_FILE )
Settings.defaultConfig( configuration )

# Setup log file.
log = Log( systemTime, configuration.get( "LogDirectory" ) + '/log.csv', isLogEchoed )
log.add( "Main", "START", "Control system starts." )

try:
  # Version information for control software.
  version = Version( Settings.VERSION_FILE, ".", Settings.CONTROL_FILES )

  if version.update() :
    log.add( "Main", "VERSION_CHANGE", "Control software has changed." )

  log.add(
    "Main",
    "VERSION",
    "Control software version " + str( version.getVersion() ),
    [ version.getVersion(), version.getHash(), version.getDate() ]
  )

  # Version information for user interface.
  uiVersion = Version( Settings.UI_VERSION_FILE, Settings.WEB_DIRECTORY, Settings.UI_FILES )

  # Create I/O map.
  if isSimulated :
    from Simulator.PLC_Simulator import PLC_Simulator
    from IO.Maps.SimulatedIO import SimulatedIO
    io = SimulatedIO()
    plcSimulator = PLC_Simulator( io )
  else:
    from IO.Maps.ProductionIO import ProductionIO
    io = ProductionIO( configuration.get( "plcAddress" ) )

  # Use low-level I/O to avoid warning.
  # (Low-level I/O is needed by remote commands.)
  LowLevelIO.getTags()

  # Primary control process.
  process = Process( io, log, configuration )

  #
  # Initialize threads.
  #

  uiServer = UI_ServerThread( commandHandler, log )
  webServerThread = WebServerThread( commandHandler, log )

  controlThread = ControlThread( io, log, process.controlStateMachine, systemTime, isIO_Logged )

  # Setup debug interface (if enabled).
  if debugInterface :
    from Threads.DebugThread import DebugThread
    debugUI = \
      DebugThread(
        log,
        configuration.get( "serverAddress" ),
        int( configuration.get( "serverPort" ) )
      )

  PrimaryThread.useGracefulException = not debugInterface

  # Begin operation.
  PrimaryThread.startAllThreads()

  # While the program is running...
  while ( PrimaryThread.isRunning ) :
    time.sleep( 0.1 )

  PrimaryThread.stopAllThreads()

  # Shutdown the current processes.
  process.closeAPA()

  # Save configuration.
  configuration.save()

  # $$$DEBUG - Shutdown I/O.

except Exception as exception:
  PrimaryThread.stopAllThreads()
  exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
  tracebackString = repr( traceback.format_tb( exceptionTraceback ) )
  if debugInterface :
    traceback.print_tb( exceptionTraceback )
    raise exception
  else :
    log.add(
      "Main",
      "FAILURE",
      "Caught an exception.",
      [ exception, exceptionType, exceptionValue, tracebackString ]
    )

# Sign off.
log.add( "Main", "END", "Control system stops." )

# "If you think you understand quantum mechanics, you don't understand quantum
# mechanics." -- Richard Feynman
