###############################################################################
# Name: ControlStateMachine.py
# Uses: Root level state machine.
# Date: 2016-02-11
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-11 - QUE - Creation.
###############################################################################

from Library.LoggedStateMachine import LoggedStateMachine
from Control.HardwareMode import HardwareMode
from Control.StopMode import StopMode
from Control.WindMode import WindMode
from Control.ManualMode import ManualMode

class ControlStateMachine( LoggedStateMachine ) :

  class States :
    HARDWARE    = 0,
    STOP        = 1,
    WIND        = 2,
    CALIBRATE   = 3,
    MANUAL      = 4,
    TENTION     = 5
  # end class

  #---------------------------------------------------------------------
  def update( self ) :
    """
    Overridden update function.  Runs some base logic before any other
    state.
    """

    if not self._io.isFunctional() \
      and self.getState() != self.States.HARDWARE :
        self.changeState( self.States.HARDWARE )
    # Emergency stop.
    elif self._io.estop.get() \
      and self.getState() != self.States.STOP :
        self.log.add(
          self.__class__.__name__,
          "ESTOP",
          "Emergency stop detected."
        )
        self.changeState( self.States.STOP )

    LoggedStateMachine.update( self )

  #---------------------------------------------------------------------
  def isStopped( self ) :
    """
    See if state machine is in stop.

    Return:
      True if state machine is in stop.
    """
    return self.States.STOP == self.getState()

  #---------------------------------------------------------------------
  def isMovementReady( self ) :
    """
    Check to see if the state machine is in a state suitable for starting
    motion.

    Returns:
      True if machine can begin motion.
    """
    return self.States.STOP == self.getState() and self.stopMode.isIdle()

  #---------------------------------------------------------------------
  def __init__( self, io, log ) :
    """
    Constructor.

    Args:
      io: Instance of I/O map.
      log: Log file to write state changes.
      gCodeHandler: Instance of GCodeHandler.
      manualCommand: Instance of ManualCommand.
    """

    LoggedStateMachine.__init__( self, log )
    self.hardwareMode = HardwareMode( self, self.States.HARDWARE, io, log )
    self.stopMode     = StopMode(     self, self.States.STOP,     io, log )
    self.windMode     = WindMode(     self, self.States.WIND,     io, log )
    self.manualMode   = ManualMode(   self, self.States.MANUAL,   io, log )

    self.changeState( self.States.HARDWARE )

    self._io = io

    self.gCodeHandler = None

    self.startRequest = False
    self.stopRequest = False

    # Manual mode options.
    self.manualRequest = False
    self.isJogging = False
    self.seekX = None
    self.seekY = None
    self.seekZ = None
    self.seekVelocity = None


# end class
