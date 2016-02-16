#==============================================================================
# Name: ControlStateMachine.py
# Uses: Root level state machine.
# Date: 2016-02-11
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-11 - QUE - Creation.
#==============================================================================

from IO.IO import io
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
  def __init__( self, log, gCodeHandler, manualCommand ) :
    """
    Constructor.

    Args:
      log: Log file to write state changes.
      gCodeHandler: Instance of GCodeHandler.

    """

    LoggedStateMachine.__init__( self, log )
    self.hardwareMode = HardwareMode( self, self.States.HARDWARE )
    self.stopMode     = StopMode( self, self.States.STOP, log )
    self.windMode     = WindMode( self, self.States.WIND, gCodeHandler )
    self.manualMode   = ManualMode( self, self.States.MANUAL, manualCommand )

    self.changeState( self.States.HARDWARE )

# end class
