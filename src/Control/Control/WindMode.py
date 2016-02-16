#==============================================================================
# Name: WindMode.py
# Uses: Main control mode for winding process.
# Date: 2016-02-11
# Author(s):
#   Andrew Que <aque@bb7.com>
# Revisions:
#   2016-02-11 - QUE - Creation.
#==============================================================================

from IO.IO import io
#from Library.GCode import GCode
from Control.GCodeHandler import GCodeHandler
from Library.StateMachineState import StateMachineState

class WindMode( StateMachineState ) :

  #---------------------------------------------------------------------
  def __init__( self, stateMachine, state, gCodeHandler ) :
    """
    Constructor.

    Args:
      stateMachine: Parent state machine.
      state: Integer representation of state.
      gCodeHandler: Instance of G-Code handler.
    """

    StateMachineState.__init__( self, stateMachine, state )
    self.gCodeHandler = gCodeHandler

  #---------------------------------------------------------------------
  def update( self ):
    """
    Update function that is called periodically.

    """


    # If ESTOP or I/O isn't ready...
    # $$$DEBUG - Added I/O check.
    if io.estop.get() :
      self.changeState( self.stateMachine.States.STOP )
    else:
      # Done moving?
      if not io.xyAxis.isSeeking() :

        # Done with G-Code script?
        if self.gCodeHandler.isDone() :
          self.changeState( self.stateMachine.States.STOP )
        else :
          self.gCodeHandler.runNextLine()

