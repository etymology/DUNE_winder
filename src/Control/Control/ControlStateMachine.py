#==============================================================================
# Name: ControlStateMachine.py
# Uses: Root level state machine.
# Date: 2016-02-11
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-11 - QUE - Creation.
#==============================================================================

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
    Overriden update function.  Runs some base logic before any other
    state.

    """

    if not self.io.isFunctional() \
      and self.getState() != self.States.HARDWARE :
        self.changeState( self.States.HARDWARE )

    LoggedStateMachine.update( self )

  #---------------------------------------------------------------------
  def __init__( self, io, log, gCodeHandler, manualCommand ) :
    """
    Constructor.

    Args:
      io: Instance of I/O map.
      log: Log file to write state changes.
      gCodeHandler: Instance of GCodeHandler.
      manualCommand: $$$DEBUG
    """

    LoggedStateMachine.__init__( self, log )
    self.hardwareMode = HardwareMode( self, self.States.HARDWARE, io, log )
    self.stopMode     = StopMode(     self, self.States.STOP,     io, log )
    self.windMode     = WindMode(     self, self.States.WIND,     io, log, gCodeHandler )
    self.manualMode   = ManualMode(   self, self.States.MANUAL,   io, manualCommand )

    self.io = io

    self.changeState( self.States.HARDWARE )

# end class
