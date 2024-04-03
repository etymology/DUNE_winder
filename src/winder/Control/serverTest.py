###############################################################################
# Name: main.py
# Uses: Initialize and start the control system.
# Date: 2016-02-03
# Author(s):
#   Andrew Que <aque@bb7.com>
#   Benjamin Oye <oye@uchicago.edu> [port to python3, Jan 2024 - present]
###############################################################################


from __future__ import absolute_import
from __future__ import print_function
import signal
import sys
import traceback
import time
import json

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
from Threads.CameraThread import CameraThread

from IO.IO_map import IO_map
from IO.PLC import PLC

from Simulation.SimulationTime import SimulationTime

from Machine.DefaultCalibration import DefaultMachineCalibration
from datetime import datetime


# -----------------------------------------------------------------------
def commandHandler(_, command):
    """
    Handle a remote command.
    This is define in main so that is has the most global access possible.

    Args:
      command: A command to evaluate.

    Returns:
      The data returned from the command.
    """

    try:
        result = eval(command)
    except Exception as exception:
        result = "Invalid request"

        exceptionTypeName, exceptionValues, tracebackValue = sys.exc_info()

        traceback.print_tb(tracebackValue)

        tracebackAsString = repr(traceback.format_tb(tracebackValue))
        log.add(
            "Main",
            "commandHandler",
            "Invalid command issued from UI.",
            [command, exception, exceptionTypeName,
             exceptionValues, tracebackAsString]
        )

    # Try to make JSON object of result.
    # (Custom encoder escapes any invalid UTF-8 characters which would otherwise
    # raise an exception.)
    if isinstance(result, datetime):
        result = result.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(result, PLC.Tag):
        result = result._tagName
    try:
        return json.dumps(result, ensure_ascii=True)
    except TypeError:
        # If it cannot be made JSON, just make it a string.
        return json.dumps(result, ensure_ascii=True)

# -----------------------------------------------------------------------


def signalHandler(signalNumber, frame):
    """
    Keyboard interrupt handler. Used to shutdown system for Ctrl-C.

    Args:
      signal: Ignored.
      frame: Ignored.
    """
    signalNumber = signalNumber
    frame = frame
    PrimaryThread.stopAllThreads()


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------
# Install signal handler for Ctrl-C shutdown.
signal.signal(signal.SIGINT, signalHandler)


systemTime = SimulationTime()
startTime = systemTime.get()

# Load configuration and setup default values.
configuration = Configuration(Settings.CONFIG_FILE)
Settings.defaultConfig(configuration)

# Save configuration (just in case it had not been created or new default
# values added).
configuration.save()

# Setup log file.
log = Log(systemTime, configuration.get("LogDirectory") + '/log.csv')
log.add("Main", "START", "Control system starts.")

try:
    uiServer = UI_ServerThread(commandHandler, log)
    webServerThread = WebServerThread(commandHandler, log)
    PrimaryThread.startAllThreads()

    while (PrimaryThread.isRunning):
        time.sleep(0.1)
        PrimaryThread.stopAllThreads()
        # Shutdown the current processes.

except Exception as exception:
    PrimaryThread.stopAllThreads()
    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    tracebackString = repr(traceback.format_tb(exceptionTraceback))
    traceback.print_tb(exceptionTraceback)
    raise exception
