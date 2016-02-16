#==============================================================================
# Name: main.py
# Uses: Initialize and start the control system.
# Date: 2016-02-03
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-03 - QUE - Creation.
#==============================================================================

# Import I/O map.
from IO.IO import io

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

import datetime
import time
import signal
import sys

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
  except Exception :
    result = "Invalid request"
  return result

#-----------------------------------------------------------------------
def signalHandler( signal, frame ):
  """
  Keyboard interrupt handler. Used to shutdown system for Ctrl-C.

  Args:
    signal: Ignored.
    frame: Ignored.

  """

  print "Forced shutdown"
  PrimaryThread.stopAllThreads()

def magic() :
  print datetime.datetime.utcnow()
  io.simulationTime.set( datetime.datetime.utcnow() )

#-----------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------

# Install signal handler for Ctrl-C shutdown.
signal.signal( signal.SIGINT, signalHandler )

#
# Create various objects.
#

systemTime = SystemTime()
log = Log( systemTime, 'log.txt' )
log.attach( 'log2.txt' )
log.add( "Main", "START", "Control system starts." )
log.detach( 'log2.txt' )
gCodeHandler = GCodeHandler()
manualCommand = ManualCommand()
controlStateMachine = ControlStateMachine( log, gCodeHandler, manualCommand )

# Initialize threads.
uiServer = UI_ServerThread( commandHandler, log )
controlThread = ControlThread( controlStateMachine )
debugUI = DebugThread( '', Settings.SERVER_PORT )

# Begin operation.
PrimaryThread.startAllThreads()

# $$$DEBUG - Remove from this location.
io.xAxis.setEnable( True )
io.yAxis.setEnable( True )
io.zAxis.setEnable( True )

# While the program is running...
while ( PrimaryThread.isRunning ) :
  time.sleep( 0.1 )

log.add( "Main", "END", "Control system stops." )
